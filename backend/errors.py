from flask import jsonify


def register_error_handlers(app):
    """Register global error handlers."""

    @app.errorhandler(400)
    def bad_request(e):
        app.logger.warning(f'400 Bad Request: {str(e)}')
        return jsonify({'error': 'Bad request', 'message': str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        app.logger.warning(f'401 Unauthorized: {str(e)}')
        return jsonify({'error': 'Unauthorized', 'message': 'Please login to continue'}), 401

    @app.errorhandler(403)
    def forbidden(e):
        app.logger.warning(f'403 Forbidden: {str(e)}')
        return jsonify({'error': 'Forbidden', 'message': 'You do not have permission'}), 403

    @app.errorhandler(404)
    def not_found(e):
        app.logger.warning(f'404 Not Found: {str(e)}')
        return jsonify({'error': 'Not found', 'message': 'The requested resource was not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'error': 'Method not allowed'}), 405

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f'500 Internal Server Error: {str(e)}')
        return jsonify({'error': 'Internal server error', 'message': 'Something went wrong on our end'}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f'Unhandled exception: {str(e)}', exc_info=True)
        return jsonify({'error': 'Unexpected error', 'message': str(e)}), 500
