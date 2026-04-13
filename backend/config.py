import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'fintech-super-secret-key')

    # Auto-switch: PostgreSQL on Railway, SQLite locally
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or f"sqlite:///{os.path.join(BASE_DIR, 'fintech.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY            = os.getenv('JWT_SECRET_KEY', 'fintech-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    EMAIL_USER     = os.getenv('EMAIL_USER', '')
    EMAIL_PASS     = os.getenv('EMAIL_PASS', '')
