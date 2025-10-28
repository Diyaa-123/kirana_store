from flask import Flask, render_template, request, jsonify, session
from src.database.db_json import category
from datetime import timedelta
import secrets
from src.routes.page_route import page_bp
from src.routes.api_routes import api_bp
from src.routes.error_bp import error_bp

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# ==================== PAGE ROUTES ====================
app.register_blueprint(page_bp)
# ==================== API ROUTES ====================
app.register_blueprint(api_bp)
# ==================== ERROR HANDLERS ====================
app.register_blueprint(error_bp)

if __name__ == "__main__":
    app.run(debug=True)
