import sqlite3
import telegram

base = sqlite3.connect("database.db")
cursor = base.cursor()

cursor.execute("""create table tables_with_students (teacher_id integer, teacher_name text, teacher_table_link text, teacher_table_name text)""")

def get_response(msg):
    if msg == "test":
        return "msg"
