from pymongo import MongoClient
from datetime import datetime
import numpy as np
import time

client = MongoClient('mongodb://10.0.2.180:27017')
xiaomu = client.xiaomu
xiaomu_random_question = client.xiaomu_random_question
message = xiaomu.message


def get_unlabeled(course_id):
    message_set = message.find(
        {'course_id': course_id, 'flag': {"$in": [None, 'more', ""]}, 'question_source': {"$nin": ['wobudong', 'active_question']}}).sort('_id', -1)

    q_dict, a_list = {}, []
    for m in message_set:
        if 'message' not in m.keys():
            continue

        if m['type'] == 'question':

            q_dict[m['_id']] = m

        if m['type'] == 'answer':
            a_list.append(m)

    concepts = set([x['concept'] for x in xiaomu.kp.find()])
    active_questions = set([x["content"] if x["question_type"] != 'keyword' else "什么是%s？" % (x['content']) for x in xiaomu_random_question.ques.find() ])
    labeled_questions = set(
        [x['question'] for x in xiaomu.qa_annotation.find()])

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


def get_labeled(course_id):
    return [], [], [], [], [], 0
