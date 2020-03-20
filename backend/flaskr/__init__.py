import random

from flask import Flask, jsonify, abort, request
from flask_cors import CORS

from backend.constants import QUESTIONS_PER_PAGE, StatusCode
from backend.models import Category, setup_db, Question, paginate_selection, format_selection


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

    @app.route('/questions')
    def list_questions():
        """
        Get questions for a given page.
        :return:
        """
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

    @app.route('/questions', methods=['POST'])
    def create_question():
        """
        Add a question to database.
        :return:
        """
        question = request.get_json()

        if not question:
            abort(StatusCode.HTTP_400_BAD_REQUEST.value)

        question = Question(**question)
        question.insert()

        return jsonify({
            'success': True, 'id': question.id
        }), StatusCode.HTTP_201_CREATED.value

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """
        Delete question by given id.
        :param question_id:
        :return:
        """
        question = Question.query.get(question_id)
        if not question:
            abort(StatusCode.HTTP_404_NOT_FOUND.value)

        question.delete()
        return jsonify({
            'success': True
        }), StatusCode.HTTP_204_NO_CONTENT.value

    @app.route('/questions/filter', methods=['POST'])
    def filter_questions():
        """
        Return the list of questions after filteration.
        :return:
        """
        page = request.args.get('page', 1, type=int)
        search_term = request.get_json().get('searchTerm') or ''
        selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        selection, total_selection_count = paginate_selection(selection, page=page, limit=QUESTIONS_PER_PAGE)

        return jsonify({
            'success': True,
            'questions': format_selection(selection),
            'total_questions': total_selection_count,
        })

    @app.route('/categories')
    def list_categories():
        """
        Return the categories with id and type.
        :return:
        """
        result = {
            "success": True,
            "categories": {
                category.id: category.type
                for category in Category.query.all()
            }
        }
        return jsonify(result)

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        """
        Get questions by category.
        :param category_id:
        :return:
        """
        category = Category.query.get(category_id)

        if not category:
            abort(StatusCode.HTTP_404_NOT_FOUND.value)

        page = request.args.get('page', 1, type=int)
        selection = Question.query.filter_by(category=category_id).all()
        selection, total_selection_count = paginate_selection(selection, page=page, limit=QUESTIONS_PER_PAGE)

        return jsonify({
            "success": True,
            "questions": format_selection(selection),
            "total_questions": total_selection_count,
            "current_category": category.format(),
        })

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        """
        Play quiz route to get questions for quizzes.
        :return:
        """
        request_data = request.get_json()
        previous_questions = request_data.get('previous_questions', [])
        quiz_category = request_data.get('quiz_category')

        if not quiz_category:
            abort(StatusCode.HTTP_400_BAD_REQUEST.value)

        category_id = quiz_category.get('id', None)
        if category_id:
            questions = Question.query.filter_by(category=category_id)
        else:
            questions = Question.query

        questions = format_selection(questions.filter(~Question.id.in_(previous_questions)).all())
        random_question = random.choice(questions) if questions else None

        return jsonify({
            'question': random_question, 'success': True
        })

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
