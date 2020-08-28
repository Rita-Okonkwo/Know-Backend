from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import os

from sqlalchemy.orm import relationship

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'knowcovid.db')
app.config['JWT_SECRET_KEY'] = 'super_secret'

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)


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


@app.route('/register', methods=['POST'])
def register():
    user_name = request.json['user_name']
    test = User.query.filter_by(user_name=user_name).first()
    if test:
        return jsonify(message='This username already exists'), 409
    else:
        email = request.json['email']
        password = request.json['password']
        user = User(user_name=user_name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message='User has been successfully created'), 201


@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']
    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message='Login succeeded!', access_token=access_token)
    else:
        return jsonify(message='Bad email or password'), 401


@app.route('/leaderboard', methods=['POST'])
def leaderboard():
    user_name = request.json['username']
    score = request.json['score']
    test = LeaderBoard.query.filter_by(user_name=user_name).first()
    if test:
        test.score = score
    else:
        new_user = LeaderBoard(user_name=user_name, score=score)
        db.session.add(new_user)
        db.session.commit()
    leaderboard = LeaderBoard.query.all()
    result = leaderboard_schema.dump(leaderboard)
    return jsonify(result)



# database models

class User(db.Model):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String)
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


class LeaderBoard(db.Model):
    __tablename__ = 'leaderBoard'
    board_id = Column(Integer, primary_key=True)
    user_name = Column(String)
    score = Column(Integer)


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


class LeaderBoardSchema(ma.Schema):
    class Meta:
        fields = ('board_id', 'user_name', 'score')


users_schema = UserSchema(many=True)
questions_schema = QuestionSchema(many=True)
videos_schema = VideosSchema(many=True)
leaderboard_schema = LeaderBoardSchema(many=True)
if __name__ == '__main__':
    app.run()
