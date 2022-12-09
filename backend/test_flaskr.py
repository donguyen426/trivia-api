import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
import time
import math
import random
from flask import jsonify


class TestTriviaAPI(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "student", "student", "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def test_get_categories(self):
        """Test GET /categories endpoint"""
        response = self.client().get("/categories")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.json["categories"], None)

    def test_get_paginated_questions(self):
        """Test GET /questions?page=<page_num> endpoint"""
        # test first page
        response = self.client().get("/questions?page=1")
        self.assertEqual(response.status_code, 200)
        totalQuestions = response.json["total_questions"]
        if totalQuestions > 10:
            self.assertEqual(len(response.json["questions"]), 10)
        else:
            self.assertEqual(
                response.json["questions"], totalQuestions)
        # test last page
        lastPage = math.floor(totalQuestions / 10) + 1
        expectedQuestions = totalQuestions % 10
        response = self.client().get(f"/questions?page={lastPage}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(expectedQuestions, len(response.json["questions"]))

    def test_create_question_success(self):
        """Test POST /questions endpoint with happy path test data"""
        unique_str = str(time.time_ns())
        new_question = {"question": f"question {unique_str}",
                        "answer": f"answer {unique_str}", "difficulty": random.randint(1, 5), "category": 1}
        response = self.client().post("/questions", json=new_question)
        self.assertEqual(response.status_code, 201)
        # test the fields of newly created record
        self.assertEqual(new_question.items() <=
                         response.json["question"].items(), True)

    def test_create_question_with_invalid_category(self):
        """Test POST /questions endpoint with category that does not exist"""
        unique_str = str(time.time_ns())
        new_question = {"question": f"question {unique_str}",
                        "answer": f"answer {unique_str}", "difficulty": random.randint(1, 5), "category": 100000000000000000000}
        response = self.client().post("/questions", json=new_question)
        self.assertEqual(response.status_code, 404)

    def test_get_question_by_category(self):
        """Test GET /categories/<category_id>/questions endpoint"""
        response = self.client().get("/categories/1/questions")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.json["questions"]), response.json["total_questions"])

    def test_delete_question_success(self):
        """Test DELETE /questions/<question_id> endpoint"""
        # Create a new question
        response = self.client().post("/questions", json={"question": f"question {str(time.time_ns())}",
                                                          "answer": f"answer {str(time.time_ns())}", "difficulty": random.randint(1, 5), "category": 1})
        self.assertEqual(response.status_code, 201)
        created_question_id = response.json["question"]["id"]
        # delete it
        delete_response = self.client().delete(
            f"/questions/{created_question_id}")
        self.assertEqual(delete_response.status_code, 204)

    def test_delete_question_with_incorrect_id(self):
        """Test DELETE /questions/<question_id> endpoint with incorrect question id"""
        delete_response = self.client().delete("/questions/111111111111111111111111")
        self.assertEqual(delete_response.status_code, 404)

    def test_search_question(self):
        """Test POST /questions/search"""
        response = self.client().post("/questions/search",
                                      json={"searchTerm": "question"})
        self.assertEqual(response.status_code, 200)

    def test_quizzes_specific_category(self):
        """Test POST /quizzes with provided category """
        # get the number of questions per play
        response = self.client().get("/configs")
        self.assertEqual(response.status_code, 200)
        questions_per_play = response.json["configs"]["questions_per_play"]
        # get total questions of specified category
        response = self.client().get("/categories/1/questions")
        self.assertEqual(response.status_code, 200)
        total_questions = response.json["total_questions"]

        # play
        previous_questions = []
        isPlaying = True
        questions_received = 0
        while isPlaying == True:
            response = self.client().post("/quizzes",
                                          json={"previous_questions": previous_questions, "quiz_category": {"type": "", "id": 1}})
            self.assertEqual(response.status_code, 200)

            isPlaying = bool(response.json["question"])
            if isPlaying:
                # returning question must not be duplicated
                self.assertEqual(previous_questions.__contains__(
                    response.json["question"]["id"]), False)
                previous_questions.append(response.json["question"]["id"])
                questions_received = questions_received + 1

        # done playing, now verifying
        if total_questions < questions_per_play:
            self.assertEqual(questions_received, total_questions)
        else:
            self.assertEqual(questions_received, questions_per_play)

    def test_quizzes_category_all(self):
        """Test POST /quizzes with ALL category """
        # get the number of questions per play
        response = self.client().get("/configs")
        self.assertEqual(response.status_code, 200)
        questions_per_play = response.json["configs"]["questions_per_play"]
        # get total questions of specified category
        response = self.client().get("/questions?page=1")
        self.assertEqual(response.status_code, 200)
        total_questions = response.json["total_questions"]

        # play
        previous_questions = []
        isPlaying = True
        questions_received = 0
        while isPlaying == True:
            response = self.client().post("/quizzes",
                                          json={"previous_questions": previous_questions, "quiz_category": {"type": "click", "id": 0}})
            self.assertEqual(response.status_code, 200)

            isPlaying = bool(response.json["question"])
            if isPlaying:
                # returning question must not be duplicated
                self.assertEqual(previous_questions.__contains__(
                    response.json["question"]["id"]), False)
                previous_questions.append(response.json["question"]["id"])
                questions_received = questions_received + 1

        # done playing, now verifying
        if total_questions < questions_per_play:
            self.assertEqual(questions_received, total_questions)
        else:
            self.assertEqual(questions_received, questions_per_play)

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
