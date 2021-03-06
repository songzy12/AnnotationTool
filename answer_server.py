import json
from datetime import datetime
import traceback

import requests
from flask import Flask, render_template, request
import pymongo
from pymongo import MongoClient

from config import MONGO_SERVICE, ES_SERVICE
from util.db_util import qa_label_table, answer_label_table

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


def request_es(source, payload):
    # public
    url = ES_SERVICE + "/robot_{}/_search".format(source)
    try:
        response = json.loads(requests.post(url, json=payload).text)
    except:
        print(">>> request_es")
        traceback.print_exc()
    return response.get('hits', {'total': 0, 'max_score': 0, 'hits': []})


def get_candidates(question):
    candidates = []
    limit = 10

    payload = {
        'query': {
            'match': {
                'question': question
            }
        }
    }
    hits = request_es('common', payload)
    print(">>> get_common, len of hits: {}".format(hits['total']))

    for answer in hits['hits'][:limit]:
        question = answer['_source']['question']
        answer = answer['_source']['answer']
        candidates.append([question, answer])

    return candidates


def get_questions(amount):
    questions = []
    items = answer_label_table.find()
    saved = set([x['qid'] for x in items])

    items = qa_label_table.find(
        {"category": "0"}).sort("time", pymongo.DESCENDING)
    cnt = 0
    for item in items:
        qid, question, answer, evaluate, time = item['qid'], item['question'], item['answer'], item.get(
            'evaluate', ""), item['time']

        if qid in saved:
            continue

        candidates = get_candidates(question)

        if evaluate == 'both good':
            item = {'qid': qid, 'question': question,
                    'answer': answer, 'candidates': candidates, 'time': time}
            item.update({'created': datetime.now()})
            answer_label_table.insert(item)
            continue

        if not candidates:
            item = {'qid': qid, 'question': question,
                    'answer': "", 'candidates': candidates, 'time': time}
            item.update({'created': datetime.now()})
            answer_label_table.insert(item)
            continue

        questions.append([qid, time, question, candidates])
        cnt += 1
        if cnt == amount:
            break

    return questions


@app.route('/')
def index():
    questions = get_questions(100)
    return render_template('answer_selection.html', elements=questions)


@app.route('/label_answer', methods=['POST'])
def label_answer():
    # we store the annotated pair into mongo datebase
    item = {k: v for k, v in request.form.items()}
    item.update({'created': datetime.now()})
    answer_label_table.insert(item)
    return json.dumps({'success': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9006, threaded=True, debug=True)
