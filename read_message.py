from pymongo import MongoClient
from datetime import datetime
import numpy as np
import time

client = MongoClient('mongodb://10.0.2.180:27017')
xiaomu = client.xiaomu
message = xiaomu.message


def get_messages(course_id):
    message_set = message.find(
        {'course_id': course_id, 'flag': {"$in": [None, 'more', 'try', "cached", "cached_more"]}}).sort('_id', -1)

    q_dict, a_list = {}, []
    for m in message_set:
        if 'message' not in m.keys():
            continue

        if m['type'] == 'question' and m.get('question_source', None) not in ['wobudong', 'active_question']:

            q_dict[m['_id']] = m

        if m['type'] == 'answer':
            a_list.append(m)

    print(course_id)

    stored_questions = set(
        [x['question'] for x in xiaomu.qa_annotation.find({"course_id": course_id})])

    qid_list, q_text, a_text, times, tags = [], [], [], [], []
    for v in a_list:
        if 'origin_question' not in v:
            continue

        q_id = v['origin_question']
        if q_id not in q_dict:
            continue

        if q_dict[q_id]['message'] in stored_questions:
            continue

        qid_list.append(q_id)
        q_text.append(q_dict[q_id]['message'])
        a_text.append(v['message'] if v['message'] else (v['answers'][0]['message'] if 'answers' in v else ''))
        
        times.append(v['time'])
        tags.append(v.get('tag', -1))

    response = [qid_list, a_text, q_text, times, tags]
    return [x[:100] for x in response]
