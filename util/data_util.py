from collections import defaultdict
import csv
import json

from config import COURSE_INFO_FILE 

def get_course_info(course_id_list):
    c2course = defaultdict(list)
    id2name = {}
    with open(COURSE_INFO_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['course_id'] not in course_id_list:
                continue
            try:
                category = json.loads(row['category'])
            except:
                # TODO(songzy): log a warning message here.
                category = {}

            id2name[row['course_id']] = row['name']
            c2course['-'.join(tuple(category.values()))].append([
                row[x] if type(row[x]) != float else '' for x in ['course_id', 'name']
            ])
    for k in c2course:
        c2course[k].sort()
    return id2name, c2course
