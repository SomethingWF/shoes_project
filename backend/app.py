"""
Основной модуль приложения Flask
"""

import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import create_access_token, JWTManager
from dotenv import load_dotenv

from db import db
from models import User, Product

load_dotenv()

app = Flask(__name__, static_folder='static')

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
app.json.ensure_ascii = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app)
jwt = JWTManager(app)

@app.route('/api/login', methods=['POST'])
def login():
    """Аутентификация"""
    data = request.get_json()
    req_login = data.get('login', None)
    req_password = data.get('password', None)

    user = User.query.filter_by(login=req_login, password=req_password).first()

    if not user:
        return jsonify({"msg": "Неверный логин или пароль"}), 401

    additional_claims = {"role_id": user.role_id}
    access_token = create_access_token(identity=user.id, additional_claims=additional_claims)

    return jsonify(
        access_token=access_token,
        user_fullname=user.full_name,
        user_role_id=user.role_id
    )

@app.route('/api/products', methods=['GET'])
def get_products():
    """Получение товаров"""
    products = Product.query.all()
    result = [product.to_dict() for product in products]
    return jsonify(result)

@app.route('/static/images/<filename>')
def serve_image(filename):
    """Получение картинок"""
    return send_from_directory(app.config['STATIC_FOLDER'] + '/images', filename)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
