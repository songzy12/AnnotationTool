import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import sys

from read_message import get_messages

sys.path.append("/home/xiaomu/xiaomu")

client = MongoClient('mongodb://10.0.2.180:27017')
xiaomu = client.xiaomu

app = Flask(__name__)


@app.route('/message/<course_id>/')
def message(course_id):
    answers, questions, times, tags = get_messages(course_id)
    return render_template('message.html', q_a=zip(questions, answers, tags, times), course=course_id)


@app.route('/')
def main():
    course_info = pd.read_csv(
        './course_info.csv', index_col='tw_ms_courseinfo_d.id')
    m = {k: v for k, v in zip(
        course_info['tw_ms_courseinfo_d.course_id'].values,
        course_info['tw_ms_courseinfo_d.name'].values)}

    course_ids = xiaomu.message.distinct("course_id")

    cs, ns = [], []
    for course_id in course_ids:
        if course_id not in m:
            continue
        cs.append(course_id)
        ns.append(m[course_id])

    return render_template("main.html", c_n=zip(cs, ns))


@app.route('/gen_qa_pair', methods=['POST'])
def add_pre():
    # we store the annotated pair into mongo datebase
    course_id = request.form["course_id"]
    xiaomu.qa_annotation.insert({k:v for k, v in request.form.items()})
    return redirect('/message/'+course_id)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9005, threaded=True, debug=True)
