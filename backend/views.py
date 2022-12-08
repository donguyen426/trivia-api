from flask import Flask, request, abort, jsonify
from models import Category, Question, db
from sqlalchemy.exc import SQLAlchemyError
from http import HTTPStatus


QUESTIONS_PER_PAGE = 10

# "/categories", methods=["GET"]


def get_categories():
    """GET /categories"""
    categories = {}
    {categories.update(item.format()) for item in Category.query.all()}
    return jsonify({"categories": categories})


def get_questions():
    """GET /questions"""
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questionsJson = [item.format() for item in Question.query.all()]
    categories = {}
    {categories.update(item.format()) for item in Category.query.all()}

    return jsonify({"questions": questionsJson[start:end], "totalQuestions": len(questionsJson), "categories": categories, "currentCategory": "unused"})


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
        formatted_question = question.format()
        return {"question": formatted_question}, HTTPStatus.CREATED
    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        abort(HTTPStatus.INTERNAL_SERVER_ERROR)
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
        return jsonify({"questions": json, "totalQuestions": len(json), "currentCategory": currentCategory})


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
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        finally:
            db.session.close()


def search_questions():
    """POST /questions/search"""
    searchTerm = request.get_json()["searchTerm"]
    questions = Question.query.filter(
        Question.question.ilike(f"%{searchTerm}%")).all()
    formatted_questions = [item.format() for item in questions]
    return jsonify({"questions": formatted_questions, "totalQuestions": len(formatted_questions), "currentCategory": "do not know what to return"})


def get_quizzes():
    """POST /quizzes"""
    prev_questions = request.get_json()["previous_questions"]
    category_id = request.get_json()["quiz_category"]["id"]
    next_question = Question.query.filter(
        Question.category == category_id).filter(Question.id.notin_(prev_questions)).first()
    formatted_question = next_question.format() if next_question else {}

    return jsonify({"question": formatted_question})
