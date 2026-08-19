from flask import jsonify
import logging

logger = logging.getLogger(__name__)


def success_response(data=None, message=None, status_code=200):
    """Standard success JSON response."""
    response = {'success': True}
    if message:
        response['message'] = message
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code


def error_response(error: str, status_code: int = 400):
    """Standard error JSON response."""
    return jsonify({'success': False, 'error': error}), status_code


def register_error_handlers(app):
    """Register global Flask error handlers."""
    
    @app.errorhandler(400)
    def bad_request(e):
        return error_response('Bad request.', 400)
    
    @app.errorhandler(401)
    def unauthorized(e):
        return error_response('Authentication required.', 401)
    
    @app.errorhandler(403)
    def forbidden(e):
        return error_response('You do not have permission to access this resource.', 403)
    
    @app.errorhandler(404)
    def not_found(e):
        return error_response('Resource not found.', 404)
    
    @app.errorhandler(413)
    def file_too_large(e):
        return error_response('File is too large. Maximum size is 50MB.', 413)
    
    @app.errorhandler(500)
    def internal_server_error(e):
        logger.exception('Internal server error')
        return error_response('An internal server error occurred.', 500)
