# -*- coding: utf-8 -*-
"""Flask API для регистрации ONU на ZTE OLT"""
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import os

# Загрузка переменных окружения
load_dotenv()

# Импорт Blueprints
from blueprints import api_onu_bp, api_utils_bp
from docs import docs_bp

# Настройка логирования
# def setup_logging():
#     if not os.path.exists('logs'):
#         os.mkdir('logs')
    
#     file_handler = logging.FileHandler(
#         os.getenv('LOG_FILE', 'logs/onu_registration.log'),
#         maxBytes=10240000,
#         backupCount=10
#     )
#     file_handler.setFormatter(logging.Formatter(
#         '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
#     ))
#     file_handler.setLevel(logging.INFO)
    
#     console_handler = logging.StreamHandler()
#     console_handler.setLevel(logging.DEBUG)
    
#     logger = logging.getLogger()
#     logger.setLevel(logging.INFO)
#     logger.addHandler(file_handler)
#     logger.addHandler(console_handler)
    
#     return logger

# logger = setup_logging()

# Инициализация Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'onu_secret_key')
app.config['JSON_AS_ASCII'] = False

# CORS настройки
CORS(app, origins=[
    os.getenv('FRONTEND_URL', 'http://185.253.216.7:3500/'),
    'http://localhost:3500',
    'http://185.253.216.7'
])

# Регистрация Blueprints
app.register_blueprint(api_onu_bp)
app.register_blueprint(api_utils_bp)
app.register_blueprint(docs_bp)

if __name__ == '__main__':
    # logger.info("Запуск ONU Registration API...")
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5500)),
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )