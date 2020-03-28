from datetime import datetime
from app import db


class Teacher(db.Model):
    __name__ = 'teacher'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(80))

    def __repr__(self):
        return f"Teacher('{self.id}', '{self.name}')"


class Tables(db.Model):
    __name__ = 'tables'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    list_name = db.Column(db.String(80))
    url = db.Column(db.String(80))

    def __repr__(self):
        return f"Tables('{self.id}', '{self.user_id}', '{self.list_name}', '{self.url}')"


class Student(db.Model):
    __name__ = 'student'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(80))
    phone = db.Column(db.String(20))

    def __repr__(self):
        return f"Student('{self.id}', '{self.name}', '{self.phone}')"
