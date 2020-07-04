from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields
import os

from sqlalchemy.orm import relationship

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'knowcovid.db')


db = SQLAlchemy(app)
ma = Marshmallow(app)

# create the database


@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created!')


# destroy the database
@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped')


# seed database
@app.cli.command('db_seed')
def db_seed():
    question = Question(
        question='Are antibiotics effective in preventing or treating COVID-19?'
    )
    answer1 = Answer(
        answer='No. Antibiotics do not work against viruses',
        correct=True,
        question=question
    )
    answer2 = Answer(
        answer='Yes. Antibiotics work against viruses',
        correct=False,
        question=question
    )
    answer3 = Answer(
        answer="Yes, when the antibiotics are combined with good food",
        correct=False,
        question=question
    )
    answer4 = Answer(
        answer='None of the above',
        correct=False,
        question=question
    )
    db.session.add(question)
    db.session.add(answer1)
    db.session.add(answer2)
    db.session.add(answer3)
    db.session.add(answer4)
    db.session.commit()
    print('Database seeded')


@app.route('/welcome')
def welcome():
    return "Welcome to COVID 19 Quiz API"


@app.route('/questions', methods=['GET'])
def questions():
    question_list = Question.query.all()
    result = questions_schema.dump(question_list)
    return jsonify(result)


@app.route('/videos', methods=['GET'])
def videos():
    video_list = Videos.query.all()
    result = videos_schema.dump(video_list)
    return jsonify(result)


# database models
class User(db.Model):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)


class Answer(db.Model):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    answer = Column(String)
    correct = Column(Boolean)
    question_id = Column(Integer, ForeignKey('questions.id'))


class Question(db.Model):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    question = Column(String)
    answers = relationship('Answer', backref='question')


class Videos(db.Model):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True)
    video_url = Column(String)
    description = Column(String)


# define marshmallow schema for serialization
class UserSchema(ma.Schema):
    class Meta:
        fields = ('user_id', 'first_name', 'last_name', 'email', 'password')


class AnswerSchema(ma.Schema):
    class Meta:
        fields = ('id', 'answer', 'correct', 'question_id')


class QuestionSchema(ma.Schema):
    question = fields.String()
    answers = fields.Nested(AnswerSchema, many=True)


class VideosSchema(ma.Schema):
    class Meta:
        fields = ('id', 'video_url', 'description')


users_schema = UserSchema(many=True)
questions_schema = QuestionSchema(many=True)
videos_schema = VideosSchema(many=True)
if __name__ == '__main__':
    app.run()


