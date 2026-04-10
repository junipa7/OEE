# config.py

import os

class Config:
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///default.db')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')
    API_VERSION = os.getenv('API_VERSION', 'v1')