from datetime import datetime
import time

from pymongo import MongoClient

from config import MONGO_SERVICE

client = MongoClient(MONGO_SERVICE)
xiaomu_db = client.xiaomu

message_table = xiaomu_db.message
random_question_table = xiaomu_db.random_question
qa_label_table = xiaomu_db.qa_label
kp_table = xiaomu_db.kp
answer_label_table = xiaomu_db.answer_label_table


def get_unlabeled_qa(course_id):
    message_set = message_table.find(
        {'course_id': course_id, 'flag': {"$in": [None, 'more', ""]}, 'question_source': {"$nin": ['wobudong', 'active_question']}}).sort('_id', -1)

    q_dict, a_list = {}, []
    for m in message_set:
        if 'message' not in m.keys():
            continue

        if m['type'] == 'question':

            q_dict[m['_id']] = m

        if m['type'] == 'answer':
            a_list.append(m)

    concepts = set([x['concept'] for x in kp_table.find()])
    active_questions = set([x["content"] if x["question_type"] != 'keyword' else "什么是%s？" % (
        x['content']) for x in random_question_table.find()])
    labeled_questions = set(
        [x['question'] for x in qa_label_table.find()])

    qid_list, q_text, a_text, times, tags = [], [], [], [], []
    for v in a_list:
        if 'origin_question' not in v:
            continue

        q_id = v['origin_question']
        if q_id not in q_dict:
            continue

        if q_dict[q_id]['message'] in labeled_questions or \
                q_dict[q_id]['message'] in concepts or \
                q_dict[q_id]['message'] in active_questions:
            continue

        if '[    ]' in q_dict[q_id]['message']:
            continue

        answer = ''
        if v['message']:
            answer = v['message']
        elif 'answers' in v:
            if 'result' in v['answers']:
                answer = v['answers']['result']['message']
            else:
                answer = v['answers'][0]['message']

        if not answer:
            continue

        a_text.append(answer)

        qid_list.append(q_id)
        q_text.append(q_dict[q_id]['message'])

        times.append(v['time'])
        tags.append(v.get('tag', -1))

    response = [qid_list, a_text, q_text, times, tags]
    return [x[:100] for x in response] + [len(set(q_text))]


def get_labeled_qa(course_id):
    return [], [], [], [], [], 0


def get_unlabeled_qa_cnt(course_id, labeled_questions):
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
