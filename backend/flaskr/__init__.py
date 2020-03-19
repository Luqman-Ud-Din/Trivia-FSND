# import os
# from flask import Flask, request, abort, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
# import random
#
# from models import setup_db, Question, Category
from enum import Enum

from flask import Flask, jsonify, abort, request
from flask_cors import CORS

from backend.models import Category, setup_db, Question

QUESTIONS_PER_PAGE = 10


class StatusCode(Enum):
    """Enum to maintain status codes."""

    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_204_NO_CONTENT = 204
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_405_METHOD_NOT_ALLOWED = 405
    HTTP_422_UNPROCESSABLE_ENTITY = 422
    HTTP_500_INTERNAL_SERVER_ERROR = 500


def paginate_selection(selection, page=1, limit=10):
    start = (page - 1) * limit
    end = start + limit
    return selection[start:end], len(selection)


def format_selection(selection):
    return [s.format() for s in selection]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        """
        Handler for after a request has been made.
        :param response:
        """
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization'
        )
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        )
        return response

    @app.route('/categories')
    def list_categories():
        """
        Return the categories with id and type.
        :return:
        """
        try:
            result = {
                "success": True,
                "categories": {
                    category.id: category.type
                    for category in Category.query.all()
                }
            }
            return jsonify(result)
        except:
            abort(StatusCode.HTTP_500_INTERNAL_SERVER_ERROR.value)

    @app.route('/questions')
    def list_questions():
        """
        Get questions for a given page.
        :return:
        """
        try:
            page = request.args.get('page', 1, type=int)
            selection = Question.query.all()
            selection, total_selection_count = paginate_selection(selection, page=page, limit=QUESTIONS_PER_PAGE)

            categories = {
                category.id: category.type for category in Category.query.all()
            }

            if len(selection) == 0:
                abort(StatusCode.HTTP_404_NOT_FOUND.value)

            return jsonify({
                'success': True,
                'current_category': None,
                'categories': categories,
                'questions': format_selection(selection),
                'total_questions': total_selection_count
            })
        except:
            abort(StatusCode.HTTP_500_INTERNAL_SERVER_ERROR.value)

    @app.route('/questions', methods=['POST'])
    def create_question():
        """
        Add a question to database.
        :return:
        """
        try:
            question = request.get_json()

            if not question:
                abort(StatusCode.HTTP_400_BAD_REQUEST.value)

            question = Question(**question)
            question.insert()

            return jsonify({
                'success': True, 'id': question.id
            }), StatusCode.HTTP_201_CREATED.value
        except:
            abort(StatusCode.HTTP_500_INTERNAL_SERVER_ERROR.value)

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """
        Delete question by given id.
        :param question_id:
        :return:
        """
        try:
            question = Question.query.get(question_id)
            if not question:
                abort(StatusCode.HTTP_404_NOT_FOUND.value)

            question.delete()
            return jsonify({
                'success': True
            }), StatusCode.HTTP_204_NO_CONTENT.value
        except:
            abort(StatusCode.HTTP_500_INTERNAL_SERVER_ERROR.value)

    @app.route('/questions/filter', methods=['POST'])
    def filter_questions():
        """
        Return the list of questions after filteration.
        :return:
        """
        try:
            page = request.args.get('page', 1, type=int)
            search_term = request.get_json().get('searchTerm') or ''
            selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
            selection, total_selection_count = paginate_selection(selection, page=page, limit=QUESTIONS_PER_PAGE)

            return jsonify({
                'success': True,
                'questions': format_selection(selection),
                'total_questions': total_selection_count,
            })
        except:
            abort(StatusCode.HTTP_500_INTERNAL_SERVER_ERROR.value)

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 
  
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
  
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''

    @app.errorhandler(StatusCode.HTTP_400_BAD_REQUEST.value)
    def bad_request(error):
        """
        Error handler for bad request with status code 400.
        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': StatusCode.HTTP_400_BAD_REQUEST.value,
            'message': StatusCode.HTTP_400_BAD_REQUEST.name
        }), StatusCode.HTTP_400_BAD_REQUEST.value

    @app.errorhandler(StatusCode.HTTP_401_UNAUTHORIZED.value)
    def unauthorized(error):
        """
        Error handler for unauthorized with status code 401.
        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': StatusCode.HTTP_401_UNAUTHORIZED.value,
            'message': StatusCode.HTTP_401_UNAUTHORIZED.name
        }), StatusCode.HTTP_401_UNAUTHORIZED.value

    @app.errorhandler(StatusCode.HTTP_403_FORBIDDEN.value)
    def forbidden(error):
        """
        Error handler for forbidden with status code 403.
        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': StatusCode.HTTP_403_FORBIDDEN.value,
            'message': StatusCode.HTTP_403_FORBIDDEN.name
        }), StatusCode.HTTP_403_FORBIDDEN.value

    @app.errorhandler(StatusCode.HTTP_404_NOT_FOUND.value)
    def not_found(error):
        """
        Error handler for not found with status code 404.
        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': StatusCode.HTTP_404_NOT_FOUND.value,
            'message': StatusCode.HTTP_404_NOT_FOUND.name
        }), StatusCode.HTTP_404_NOT_FOUND.value

    @app.errorhandler(StatusCode.HTTP_405_METHOD_NOT_ALLOWED.value)
    def method_not_allowed(error):
        """
        Error handler for method not allowed with status code 405.
        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': StatusCode.HTTP_405_METHOD_NOT_ALLOWED.value,
            'message': StatusCode.HTTP_405_METHOD_NOT_ALLOWED.name
        }), StatusCode.HTTP_405_METHOD_NOT_ALLOWED.value

    @app.errorhandler(StatusCode.HTTP_422_UNPROCESSABLE_ENTITY.value)
    def unprocessable_entity(error):
        """
        Error handler for unprocessable entity with status code 422.
        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': StatusCode.HTTP_422_UNPROCESSABLE_ENTITY.value,
            'message': StatusCode.HTTP_422_UNPROCESSABLE_ENTITY.name
        }), StatusCode.HTTP_422_UNPROCESSABLE_ENTITY.value

    @app.errorhandler(StatusCode.HTTP_500_INTERNAL_SERVER_ERROR.value)
    def internal_server_error(error):
        """
        Error handler for internal server error with status code 500.
        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': StatusCode.HTTP_500_INTERNAL_SERVER_ERROR.value,
            'message': StatusCode.HTTP_500_INTERNAL_SERVER_ERROR.name
        }), StatusCode.HTTP_500_INTERNAL_SERVER_ERROR.value

    return app
