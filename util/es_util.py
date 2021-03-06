import json
import requests

from config import ES_SERVICE

def request_es(source, payload):
    # public
    url = ES_SERVICE + "/robot_{}/_search".format(source)
    response = json.loads(requests.post(url, json=payload).text)
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
