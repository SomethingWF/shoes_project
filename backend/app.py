"""
Основной модуль приложения Flask
"""

import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from sqlalchemy import or_

from db import db
from models import User, Product, Category, Manufacturer, Supplier, OrderProduct

load_dotenv()

app = Flask(__name__, static_folder='static')

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
app.json.ensure_ascii = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app)
jwt = JWTManager(app)

def check_is_admin():
    """Проверка на админа по role_id"""
    claims = get_jwt()
    if claims.get('role_id') != 1:
        return False
    return True

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
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)

    return jsonify(
        access_token=access_token,
        user_fullname=user.full_name,
        user_role_id=user.role_id
    )

@app.route('/api/products', methods=['GET'])
def get_products():
    """Получение списка товаров с фильтрацией, поиском и сортировкой."""
    search_query = request.args.get('search', '')
    supplier_id = request.args.get('supplier_id', '')
    sort_by = request.args.get('sort_by', '')

    query = Product.query

    if search_query:
        search_term = f"%{search_query}%"
        query = query.join(Manufacturer).filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                Manufacturer.name.ilike(search_term)
            )
        )

    if supplier_id and supplier_id != 'all':
        query = query.filter(Product.supplier_id == int(supplier_id))

    if sort_by == 'asc':
        query = query.order_by(Product.quantity.asc())
    elif sort_by == 'desc':
        query = query.order_by(Product.quantity.desc())
    else:
        query = query.order_by(Product.id.asc())

    products = query.all()
    return jsonify([product.to_dict() for product in products])

@app.route('/static/images/<filename>')
def serve_image(filename):
    """Получение картинок"""
    images_dir = os.path.join(app.static_folder, 'images')
    return send_from_directory(images_dir, filename)

@app.route('/api/products', methods=['POST'])
@jwt_required()
def create_product():
    """Добавление нового товара (Только Админ)."""
    if not check_is_admin():
        return jsonify({"msg": "Доступ запрещен. Только для администраторов."}), 403

    data = request.form

    icon_link = "picture.png"
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.static_folder, 'images', filename))
            icon_link = filename

    new_product = Product(
        article=data.get('article'),
        name=data.get('name'),
        price=float(data.get('price')),
        discount=int(data.get('discount')),
        quantity=int(data.get('quantity')),
        description=data.get('description'),
        category_id=int(data.get('category_id')),
        manufacturer_id=int(data.get('manufacturer_id')),
        supplier_id=int(data.get('supplier_id')),
        icon_link=icon_link
    )

    db.session.add(new_product)
    db.session.commit()

    return jsonify({"msg": "Товар успешно добавлен", "product": new_product.to_dict()}), 201


@app.route('/api/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Редактирование товара (Только Админ)."""
    if not check_is_admin():
        return jsonify({"msg": "Доступ запрещен."}), 403

    product = Product.query.get_or_404(product_id)
    data = request.form

    product.article = data.get('article', product.article)
    product.name = data.get('name', product.name)
    product.price = float(data.get('price', product.price))
    product.discount = int(data.get('discount', product.discount))
    product.quantity = int(data.get('quantity', product.quantity))
    product.description = data.get('description', product.description)
    product.category_id = int(data.get('category_id', product.category_id))
    product.manufacturer_id = int(data.get('manufacturer_id', product.manufacturer_id))
    product.supplier_id = int(data.get('supplier_id', product.supplier_id))

    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '':
            if product.icon_link and product.icon_link != "picture.png":
                old_path = os.path.join(app.static_folder, 'images', product.icon_link)
                if os.path.exists(old_path):
                    os.remove(old_path)
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.static_folder, 'images', filename))
            product.icon_link = filename

    db.session.commit()
    return jsonify({"msg": "Товар обновлен", "product": product.to_dict()})


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Удаление товара (Только Админ)."""
    if not check_is_admin():
        return jsonify({"msg": "Доступ запрещен."}), 403

    product = Product.query.get_or_404(product_id)

    order_exists = OrderProduct.query.filter_by(product_id=product_id).first()
    if order_exists:
        return jsonify({
            "msg": "Ошибка! Этот товар уже есть в заказах клиентов. Удаление запрещено."
            }), 400

    db.session.delete(product)
    db.session.commit()
    return jsonify({"msg": "Товар успешно удален."})

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Получение категорий для выпадающего списка"""
    categories = Category.query.all()
    return jsonify([{"id": c.id, "name": c.name} for c in categories])

@app.route('/api/manufacturers', methods=['GET'])
def get_manufacturers():
    """Получение производителей для выпадающего списка"""
    manufacturers = Manufacturer.query.all()
    return jsonify([{"id": m.id, "name": m.name} for m in manufacturers])

@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    """Получение поставщиков для выпадающего списка"""
    suppliers = Supplier.query.all()
    return jsonify([{"id": s.id, "name": s.name} for s in suppliers])


if __name__ == '__main__':
    app.run(debug=True, port=5000)
