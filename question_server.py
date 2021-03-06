import logging
import sys

import json
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify, Response

import pymongo
from bson.json_util import dumps

from config import PORT

from util.db_util import message_table, random_question_table, qa_label_table, kp_table, get_unlabeled, get_labeled
from util.data_util import get_course_info


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
log.addHandler(ch)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

course_id_list = message_table.distinct("course_id")
id2name, c2course = get_course_info(course_id_list)
log.info("Category to Course Info: {}".format(c2course))


def get_cnt_unlabeled(course_id, labeled_questions):
    message_set = message_table.find(
        {'course_id': course_id, 'type': 'question', 'flag': {"$in": [None, 'more']}, 'question_source': {"$nin": ['wobudong', 'active_question']}})
    message_set = list(message_set)
    items = message_table.find(
        {'course_id': course_id, 'type': 'answer', 'flag': {"$in": [None, 'more', ""]}})
    items = list(filter(lambda x: 'message' in x or 'answers' in x, items))

    origin_question_ids = set()
    for item in items:
        if 'origin_question' in item:
            origin_question_ids.add(item['origin_question'])
    unlabeled = list(filter(lambda x: x['message'] not in labeled_questions and '[    ]' not in x['message']
                            and x['_id'] in origin_question_ids, message_set))
    return len(set([x['message'] for x in unlabeled])), max([x['time'] for x in unlabeled]) if unlabeled else ''


@app.route('/unlabeled/<path:course_id>/')
def message(course_id):
    qids, answers, questions, times, tags, cnt_left = get_unlabeled(course_id)
    return render_template('message.html', q_a=zip(qids, questions, answers, times), course_id=course_id, name=id2name[course_id], cnt_left=cnt_left)


@app.route('/')
def main():
    return render_template("main.html", m=c2course)


tags = {
    0: "平台使用相关",
    1: "课程信息相关",
    2: "简单知识点解释",
    3: "复杂知识点讨论",
    4: "共性的反馈及建议",
    5: "聊天及其他",
    6: "个人相关的请求",
    7: "无意义或不适宜的内容",
    8: "预置的服务请求"
}


@app.route('/record')
def record():
    items = qa_label_table.find()
    from collections import Counter
    log.info('>>> record')
    c = Counter([str(x['created'].date()) for x in items if 'created' in x])
    return render_template('record.html', m=[(a, c[a]) for a in sorted(c.keys(), reverse=True)])


@app.route('/record_date/<date>')
def record_date(date):
    date = datetime.strptime(date, '%Y-%m-%d')
    items = qa_label_table.find(
        {'created': {"$gte": date, "$lt": date+timedelta(1)}}).sort("created", pymongo.DESCENDING)
    return jsonify([x['question'] for x in items])


@app.route('/statistics')
def statistics():
    log.info('>>> statistics')
    concepts = set([x['concept'] for x in kp_table.find()])
    log.info('concepts: %d' % len(concepts))
    active_questions = set([x["content"] if x["question_type"] != 'keyword' else "什么是%s？" % (
        x['content']) for x in random_question_table.find()])
    log.info('active_questions: %d' % len(active_questions))
    labeled_questions = set(
        [x['question'] for x in qa_label_table.find()])
    log.info('labeled_questions: %d' % len(labeled_questions))

    labeled_questions = labeled_questions.union(
        active_questions).union(concepts)
    log.info('labeled_questions: %d' % len(labeled_questions))

    question_all = list(message_table.find({'type': 'question', 'flag': {"$in": [
                        None, 'more']}, 'question_source': {"$nin": ['wobudong', 'active_question']}}))
    log.info('question_all: %d' % len(question_all))
    answer_all = list(message_table.find(
        {'type': 'answer', 'flag': {"$in": [None, 'more', ""]}}))
    answer_all = list(
        [x for x in answer_all if 'message' in x and x['message'] or 'answers' in x])
    log.info('answer_all: %d' % len(answer_all))
    labeled_all = list(qa_label_table.find())
    log.info('labeled_all: %d' % len(labeled_all))

    log.info('id2name: %d' % len(id2name))
    l = []
    for course_id, course_name in id2name.items():
        log.info(course_id)
        message_set = [x for x in question_all if x['course_id'] == course_id]

        items = [x for x in answer_all if x['course_id'] == course_id]

        origin_question_ids = set([x['origin_question']
                                   for x in items if 'origin_question' in x])
        unlabeled = list(filter(lambda x: x['message'] not in labeled_questions and '[    ]' not in x['message']
                                and x['_id'] in origin_question_ids, message_set))
        cnt_unlabeled = len(set([x['message'] for x in unlabeled]))
        latest = max([x['time'] for x in unlabeled]) if unlabeled else ''

        cnt_labeled = len(
            [x for x in labeled_all if x['course_id'] == course_id])

        tags_distribution = []

        for i in range(9):
            cnt = len([x for x in labeled_all if x['course_id'] ==
                       course_id and x.get('category', "") == str(i)])
            tags_distribution.append(cnt)

        if not cnt_unlabeled:
            continue
        l.append([latest, cnt_unlabeled, course_id,
                  course_name, cnt_labeled, tags_distribution])
    l.sort(reverse=True)
    return render_template('statistics.html', l=l)


@app.route('/labeled/<course_id>/')
def labeled(course_id):
    qids, answers, questions, times, tags, cnt_left = get_labeled(course_id)
    return render_template('message.html', q_a=zip(qids, questions, answers, times), course_id=course_id, name=id2name[course_id], cnt_left=cnt_left)


@app.route('/gen_qa_pair', methods=['POST'])
def add_pre():
    # we store the annotated pair into mongo datebase
    item = {k: v for k, v in request.form.items()}
    item.update({'created': datetime.now()})
    qa_label_table.insert(item)
    return json.dumps({'success': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, threaded=True, debug=True)
