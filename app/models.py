from datetime import datetime
from flask import current_app
from app import db


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(80))


class Tables(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    list_name = db.Column(db.String(80))
    url = db.Column(db.String(80))


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(80))
    phone = db.Column(db.String(20))
