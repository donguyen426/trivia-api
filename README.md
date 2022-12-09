# API Development and Documentation Final Project

## Trivia App

Udacity is invested in creating bonding experiences for its employees and students. A bunch of team members got the idea to hold trivia on a regular basis and created a webpage to manage the trivia app and play the game, but their API experience is limited and still needs to be built out.

That's where you come in! Help them finish the trivia app so they can start holding trivia and seeing who's the most knowledgeable of the bunch. The application must:

1. Display questions - both all questions and by category. Questions should show the question, category and difficulty rating by default and can show/hide the answer.
2. Delete questions.
3. Add questions and require that they include question and answer text.
4. Search for questions based on a text query string.
5. Play the quiz game, randomizing either all questions or within a specific category.

## Tech Stack
- Backend: Flask, SQLAlchemy
- Frontend: React

## Changes
There are changes that I made in addition to the TODO items:
- Change endpoint of search from 'POST /questions' to 'POST /questions/search'
- Remove questionsPerPlay constant in the frontend code to the backend. Also add 'GET /configs' endpoint to get questions_per_play from the frontend.
- In Play, display 'Question x/questions_per_play' before each question

## Get Started

> Backend: go to [Backend README](./backend/README.md) for more details.
> Frontend: go to [Frontend README](./frontend/README.md) for more details.

## API Reference
All APIs provided by the backend is described [here](./backend/README.md##API-Reference)
