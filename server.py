import sys
import pandas as pd
import numpy as np
import json
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
import pymongo
from pymongo import MongoClient

from read_message import get_messages
from config import DB_MONGO

sys.path.append("/home/xiaomu/xiaomu")

client = MongoClient(DB_MONGO)
xiaomu = client.xiaomu

app = Flask(__name__)


course_ids = xiaomu.message.distinct("course_id")

course_info = pd.read_csv(
    './data/course_info.csv', index_col='tw_ms_courseinfo_d.id')

from collections import defaultdict
c2course = defaultdict(list)
id2name = {}

print(list(course_info))
for index, row in course_info.iterrows():
    if row['tw_ms_courseinfo_d.course_id'] not in course_ids:
        continue
    try:
        category = json.loads(row['tw_ms_courseinfo_d.category'])
    except:
        category = {}
    course_id = row['tw_ms_courseinfo_d.course_id']
    # latest = xiaomu.message.find({'course_id':course_id}).sort("_id", pymongo.DESCENDING).limit(1)
    # latest = str(latest.next()['time'])
    id2name[row['tw_ms_courseinfo_d.course_id']
            ] = row['tw_ms_courseinfo_d.name']
    c2course['-'.join(tuple(category.values()))].append([row['tw_ms_courseinfo_d.' + x] if type(row['tw_ms_courseinfo_d.' + x]) != float else ''
                                                         for x in ['start', 'end', 'course_id', 'name']])
for k in c2course:
    c2course[k].sort()


@app.route('/message/<course_id>/')
def message(course_id):
    qids, answers, questions, times, tags, cnt_left = get_messages(course_id)
    return render_template('message.html', q_a=zip(qids, questions, answers, times), course_id=course_id, name=id2name[course_id], cnt_left=cnt_left)


@app.route('/')
def main():
    return render_template("main.html", m=c2course)


@app.route('/statistics')
def statistics():
    id2cnt = defaultdict(list)
    for course_id, name in id2name.items():
        cnt_left = 0
        cnt_saved = 0
        latest = ''
        id2cnt[course_id].append([course_id, cnt_left, cnt_saved, latest])
    return render_template('statistics.html', id2cnt)


@app.route('/saved')
def saved():
    pass


@app.route('/gen_qa_pair', methods=['POST'])
def add_pre():
    # we store the annotated pair into mongo datebase
    course_id = request.form["course_id"]
    item = {k: v for k, v in request.form.items()}
    item.update({'created': datetime.now()})
    xiaomu.qa_annotation.insert(item)
    return json.dumps({'success': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9005, threaded=True, debug=True)
