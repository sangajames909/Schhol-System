from django import forms
from peewee import  *
from os import path
connection = path.dirname(path.realpath(__file__))
db =SqliteDatabase(path.join(connection,"School.db"))

class Users(Model):
    username = CharField()
    useremail = CharField(unique=True)
    password = CharField()
    studentID = IntegerField()
    studentcourse = CharField()
    role = IntegerField()
    class Meta:
        database = db

Users.create_table(fail_silently=True)

class Assignments(Model):
    assignment_name = CharField()
    course_name = CharField()
    start_date = IntegerField()
    due_date = IntegerField()
    file = CharField()
    class Meta:
        database = db

Assignments.create_table(fail_silently=True)

class Receipt(Model):
    studentname = CharField()
    studentclass = CharField()
    date = IntegerField()
    feesamount = IntegerField()
    amountpaid = IntegerField()
    balance = IntegerField()
    studentID = IntegerField()
    class Meta:
        database = db

Receipt.create_table(fail_silently=True)


class Submit(Model):
    student_name = CharField()
    assignment_name = CharField()
    course_name = CharField()
    file = CharField()
    class Meta:
        database = db

Submit.create_table(fail_silently=True)