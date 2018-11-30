import sys
import pandas as pd
import numpy as np
import json
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

from read_message import get_messages
from config import DB_MONGO

sys.path.append("/home/xiaomu/xiaomu")

client = MongoClient(DB_MONGO)
xiaomu = client.xiaomu

app = Flask(__name__)


@app.route('/message/<course_id>/')
def message(course_id):
    qids, answers, questions, times, tags = get_messages(course_id)
    return render_template('message.html', q_a=zip(qids, questions, answers, times), course=course_id)


@app.route('/')
def main():
    course_ids = xiaomu.message.distinct("course_id")

    course_info = pd.read_csv(
        './data/course_info.csv', index_col='tw_ms_courseinfo_d.id')

    from collections import defaultdict
    m = defaultdict(list)
    print(list(course_info))
    for index, row in course_info.iterrows():
        if row['tw_ms_courseinfo_d.course_id'] not in course_ids:
            continue
        try:
            category = json.loads(row['tw_ms_courseinfo_d.category'])
        except:
            category = {}
        m['-'.join(tuple(category.values()))].append([row['tw_ms_courseinfo_d.' + x] if type(row['tw_ms_courseinfo_d.' + x]) != float else ''
                                                      for x in ['start', 'end', 'course_id', 'name']])
    for k in m:
        m[k].sort()
    return render_template("main.html", m=m)


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
