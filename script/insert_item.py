from util.db_util import message_table

if __name__ == '__main__':
    item = {"course_id": "xxx"}
    message_table.insert_one(item)
