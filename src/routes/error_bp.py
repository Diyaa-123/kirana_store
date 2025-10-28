from flask import Blueprint, session, jsonify, request, render_template
from src.database.product_catelog import category

error_bp = Blueprint('error_bp', __name__, static_folder='static', template_folder='templates')


@error_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Endpoint not found'}), 404
    return render_template('index.html'), 404

@error_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    return render_template('index.html'), 500
