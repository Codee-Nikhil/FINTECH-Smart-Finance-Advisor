from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from database import db
from routes.auth import auth_bp
from routes.budget import budget_bp
from routes.goals import goals_bp
from routes.advisor import advisor_bp
from routes.dashboard import dashboard_bp
from routes.pdf import pdf_bp
from routes.tax import tax_bp
from routes.networth import networth_bp, NetWorthEntry
from routes.email_routes import email_bp
from routes.stocks import stocks_bp
from config import Config
from logger import setup_logger
from errors import register_error_handlers
import time

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    JWTManager(app)

    # Logging
    setup_logger(app)

    # Error handlers
    register_error_handlers(app)

    # Blueprints
    app.register_blueprint(auth_bp,      url_prefix='/api/auth')
    app.register_blueprint(budget_bp,    url_prefix='/api/budget')
    app.register_blueprint(goals_bp,     url_prefix='/api/goals')
    app.register_blueprint(advisor_bp,   url_prefix='/api/advisor')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(pdf_bp,       url_prefix='/api/pdf')
    app.register_blueprint(tax_bp,       url_prefix='/api/tax')
    app.register_blueprint(networth_bp,  url_prefix='/api/networth')
    app.register_blueprint(email_bp,     url_prefix='/api/email')
    app.register_blueprint(stocks_bp,    url_prefix='/api/stocks')

    # Create tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created.")

    # Request logging middleware
    @app.before_request
    def log_request():
        app.logger.info(f'--> {request.method} {request.path}')

    @app.after_request
    def log_response(response):
        app.logger.info(f'<-- {response.status_code} {request.path}')
        return response

    @app.route('/')
    def index():
        return {"message": "FinTech API running ✦", "version": "3.0.0"}

    @app.route('/api/health')
    def health():
        return {"status": "healthy", "version": "3.0.0"}

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
