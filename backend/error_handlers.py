from flask import jsonify, current_app
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest


def register_error_handlers(app):
    """Register global error handlers for clean API error responses."""

    # ── 400 Bad Request ───────────────────────────────────────────
    @app.errorhandler(400)
    @app.errorhandler(BadRequest)
    def bad_request(e):
        current_app.logger.warning(f'400 Bad Request: {str(e)}')
        return jsonify({
            'error': 'Bad request',
            'message': str(e),
            'status': 400
        }), 400

    # ── 401 Unauthorized ──────────────────────────────────────────
    @app.errorhandler(401)
    def unauthorized(e):
        current_app.logger.warning(f'401 Unauthorized: {str(e)}')
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Please login to access this resource',
            'status': 401
        }), 401

    # ── 403 Forbidden ─────────────────────────────────────────────
    @app.errorhandler(403)
    def forbidden(e):
        current_app.logger.warning(f'403 Forbidden: {str(e)}')
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource',
            'status': 403
        }), 403

    # ── 404 Not Found ─────────────────────────────────────────────
    @app.errorhandler(404)
    @app.errorhandler(NotFound)
    def not_found(e):
        current_app.logger.warning(f'404 Not Found: {str(e)}')
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource does not exist',
            'status': 404
        }), 404

    # ── 405 Method Not Allowed ────────────────────────────────────
    @app.errorhandler(405)
    @app.errorhandler(MethodNotAllowed)
    def method_not_allowed(e):
        return jsonify({
            'error': 'Method not allowed',
            'message': str(e),
            'status': 405
        }), 405

    # ── 422 JWT errors ────────────────────────────────────────────
    @app.errorhandler(NoAuthorizationError)
    @app.errorhandler(InvalidHeaderError)
    def jwt_error(e):
        current_app.logger.warning(f'JWT error: {str(e)}')
        return jsonify({
            'error': 'Authentication required',
            'message': 'Please provide a valid token',
            'status': 422
        }), 422

    # ── 500 Internal Server Error ─────────────────────────────────
    @app.errorhandler(500)
    def internal_error(e):
        current_app.logger.error(f'500 Internal Error: {str(e)}', exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'Something went wrong on our end. Please try again.',
            'status': 500
        }), 500

    # ── Unhandled exceptions ──────────────────────────────────────
    @app.errorhandler(Exception)
    def unhandled_exception(e):
        current_app.logger.error(f'Unhandled exception: {str(e)}', exc_info=True)
        return jsonify({
            'error': 'Unexpected error',
            'message': 'An unexpected error occurred',
            'status': 500
        }), 500

    app.logger.info('Error handlers registered ✦')
