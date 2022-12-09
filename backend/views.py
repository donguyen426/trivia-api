from flask import Flask, request, abort, jsonify
from models import Category, Question, db
from sqlalchemy.exc import SQLAlchemyError
from http import HTTPStatus
from sqlalchemy.sql import func
from sqlalchemy.orm import load_only

QUESTIONS_PER_PAGE = 10

# number of questions per play
QUESTIONS_PER_PLAY = 5


def get_categories():
    """GET /categories"""
    categories = {}
    {categories.update(item.format()) for item in Category.query.all()}
    return jsonify({"categories": categories})


def create_category():
    """POST /categories"""
    category_type = request.json["type"]
    if "".__eq__(category_type):
        abort(HTTPStatus.UNPROCESSABLE_ENTITY)
    else:
        try:
            db.session.add(Category(category_type))
            db.session.commit()
        except SQLAlchemyError as e:
            print(e)
            db.session.rollback()
            abort(HTTPStatus.UNPROCESSABLE_ENTITY)
        finally:
            db.session.close()


def get_questions():
    """GET /questions"""
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questionsJson = [item.format() for item in Question.query.all()]
    categories = {}
    {categories.update(item.format()) for item in Category.query.all()}

    return jsonify({"questions": questionsJson[start:end], "total_questions": len(questionsJson), "categories": categories, "currentCategory": "unused"})


def create_question():
    """POST /questions"""
    json = request.get_json()
    category_id = int(json["category"])
    # category not exist?
    if Category.query.get(category_id) == None:
        abort(HTTPStatus.NOT_FOUND)
    try:
        question = Question(question=json["question"], answer=json["answer"],
                            difficulty=json["difficulty"], category=category_id)
        db.session.add(question)
        db.session.commit()
        # return the newly created question together with 201
        formatted_question = question.format()
        return {"question": formatted_question}, HTTPStatus.CREATED
    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        abort(HTTPStatus.UNPROCESSABLE_ENTITY)
    finally:
        db.session.close()


def get_questions_by_category(category_id):
    """GET /categories/<category_id>/questions"""
    if Category.query.get(category_id) is None:
        abort(HTTPStatus.NOT_FOUND)
    else:
        questions = Question.query.filter(Question.category == category_id)
        json = [item.format() for item in questions]
        currentCategory = Category.query.get(category_id).type
        return jsonify({"questions": json, "total_questions": len(json), "currentCategory": currentCategory})


def delete_question(question_id):
    """DELETE /questions/<question_id>"""
    question = Question.query.get(question_id)
    if question is None:
        abort(HTTPStatus.NOT_FOUND)
    else:
        try:
            db.session.delete(question)
            db.session.commit()
            return '', HTTPStatus.NO_CONTENT
        except SQLAlchemyError as e:
            print(e)
            db.session.rollback()
            abort(HTTPStatus.UNPROCESSABLE_ENTITY)
        finally:
            db.session.close()


def search_questions():
    """POST /questions/search"""
    searchTerm = request.get_json()["searchTerm"]
    # filter case insensitive
    questions = Question.query.filter(
        Question.question.ilike(f"%{searchTerm}%")).all()
    formatted_questions = [item.format() for item in questions]

    return jsonify({"questions": formatted_questions, "total_questions": len(formatted_questions), "currentCategory": "do not know what to return"})


def get_quizzes():
    """POST /quizzes"""
    previous_questions = request.json["previous_questions"]
    category_id = request.json["quiz_category"]["id"]
    # randomly pick the question based on specified category
    next_question = get_random_question(previous_questions, category_id) if len(
        previous_questions) < QUESTIONS_PER_PLAY else None

    formatted_question = next_question.format() if next_question else None
    return jsonify({"question": formatted_question})


def get_configs():
    """GET /configs"""
    return jsonify({"configs": {"questions_per_play": QUESTIONS_PER_PLAY}})


def get_random_question(prev_questions, category_id):
    # category is "ALL"
    if category_id == 0:
        return Question.query.filter(Question.id.notin_(prev_questions)).order_by(func.random()).first()
    # specific category
    else:
        return Question.query.filter(Question.id.notin_(prev_questions)).filter(
            Question.category == category_id).order_by(func.random()).first()
