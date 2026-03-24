"""
Основной модуль приложения Flask
"""

import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import or_

from db import db
from models import User, Product, Category, Manufacturer, \
                    Supplier, OrderProduct, Status, PickupPoint, Order
from schemas import LoginSchema, ProductSchema, OrderCreateSchema, OrderUpdateSchema

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

def check_is_staff():
    """Проверка прав персонала"""
    claims = get_jwt()
    return claims.get('role_id') in [1, 2]

@app.route('/api/login', methods=['POST'])
def login():
    """Аутентификация"""
    try:
        valid_data = LoginSchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"msg": "Ошибка валидации данных", "details": e.errors()}), 400

    user = User.query.filter_by(login=valid_data.login, password=valid_data.password).first()

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
                Product.article.ilike(search_term),
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
    """Добавление нового товара."""
    if not check_is_admin():
        return jsonify({"msg": "Доступ запрещен"}), 403

    try:
        prod_data = ProductSchema(**request.form.to_dict())
    except ValidationError as e:
        return jsonify({"msg": "Ошибка валидации товара", "details": e.errors()}), 400

    icon_link = "picture.png"
    if 'image' in request.files and request.files['image'].filename != '':
        file = request.files['image']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.static_folder, 'images', filename))
        icon_link = filename

    new_product = Product(
        article=prod_data.article,
        name=prod_data.name,
        price=prod_data.price,
        discount=prod_data.discount,
        quantity=prod_data.quantity,
        description=prod_data.description,
        category_id=prod_data.category_id,
        manufacturer_id=prod_data.manufacturer_id,
        supplier_id=prod_data.supplier_id,
        icon_link=icon_link
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"msg": "Товар добавлен"}), 201


@app.route('/api/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Обновление товара"""
    if not check_is_admin():
        return jsonify({"msg": "Доступ запрещен"}), 403

    product = Product.query.get_or_404(product_id)

    try:
        data = ProductSchema(**request.form.to_dict())
    except ValidationError as e:
        return jsonify({"msg": "Ошибка валидации данных", "details": e.errors()}), 400

    product.article = data.article
    product.name = data.name
    product.price = data.price
    product.discount = data.discount
    product.quantity = data.quantity
    product.description = data.description
    product.category_id = data.category_id
    product.manufacturer_id = data.manufacturer_id
    product.supplier_id = data.supplier_id

    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '':
            if product.icon_link and product.icon_link != "picture.png":
                old_path = os.path.join(app.static_folder, 'images', product.icon_link)
                if os.path.exists(old_path):
                    os.remove(old_path)

            filename = secure_filename(file.filename)
            file.save(os.path.join(app.static_folder, 'images', filename))
            product.icon_link = filename

    try:
        db.session.commit()
        return jsonify({"msg": "Товар успешно обновлен", "product": product.to_dict()})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"msg": "Ошибка базы данных", "error": str(e)}), 500


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Удаление товара"""
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

@app.route('/api/orders', methods=['GET'])
@jwt_required()
def get_orders():
    """Получение списка всех заказов с полной детализацией."""
    orders = Order.query.all()

    result = []
    for order in orders:
        items = []
        for item in order.products_in_order:
            items.append({
                "product_id": item.product_id,
                "product_name": item.product.name,
                "article": item.product.article,
                "count": item.count,
                "price": item.product.price
            })

        result.append({
            "id": order.id,
            "order_date": order.date.strftime('%Y-%m-%d'),
            "delivery_date": order.delivery_date.strftime('%Y-%m-%d'),
            "code": order.code,
            "status": order.status.name,
            "status_id": order.status_id,
            "user_name": order.user.full_name,
            "user_id": order.user_id,
            "pickup_point": f"{order.pickup_point.city}, \
                            {order.pickup_point.street}, \
                            {order.pickup_point.house}",
            "point_id": order.point_id,
            "items": items
        })

    return jsonify(result)

@app.route('/api/orders', methods=['POST'])
@jwt_required()
def create_order():
    """Создание заказа"""
    if not check_is_admin():
        return jsonify({"msg": "Доступ запрещен"}), 403

    try:
        order_data = OrderCreateSchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"msg": "Ошибка в структуре заказа", "details": e.errors()}), 400

    try:
        new_order = Order(
            date=order_data.order_date,
            delivery_date=order_data.delivery_date,
            code=order_data.code,
            user_id=order_data.user_id,
            point_id=order_data.point_id,
            status_id=order_data.status_id
        )
        db.session.add(new_order)
        db.session.flush()

        for item in order_data.items:
            product = Product.query.get(item.product_id)
            if not product or product.quantity < item.count:
                db.session.rollback()
                return jsonify({"msg": f"Товар {item.product_id} недоступен или его мало"}), 400

            order_item = OrderProduct(
                order_id=new_order.id,
                product_id=item.product_id,
                count=item.count
            )
            db.session.add(order_item)

        db.session.commit()
        return jsonify({"msg": "Заказ успешно создан", "order_id": new_order.id}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"msg": "Ошибка целостности данных. Проверьте ID заказчика и пункта."}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"msg": "Внутренняя ошибка сервера при сохранении", "error": str(e)}), 500

@app.route('/api/orders/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order(order_id):
    """Редактирование заказа"""
    if not check_is_admin():
        return jsonify({"msg": "Доступ запрещен"}), 403

    order = Order.query.get_or_404(order_id)

    try:
        update_data = OrderUpdateSchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"msg": "Ошибка валидации", "details": e.errors()}), 400

    if update_data.status_id is not None:
        order.status_id = update_data.status_id
    if update_data.point_id is not None:
        order.point_id = update_data.point_id
    if update_data.user_id is not None:
        order.user_id = update_data.user_id
    if update_data.order_date is not None:
        order.order_date = update_data.order_date
    if update_data.delivery_date is not None:
        order.delivery_date = update_data.delivery_date

    if update_data.items is not None:
        OrderProduct.query.filter_by(order_id=order.id).delete()

        for item in update_data.items:
            new_item = OrderProduct(
                order_id=order.id,
                product_id=item.product_id,
                count=item.count
            )
            db.session.add(new_item)

    try:
        db.session.commit()
        return jsonify({"msg": "Заказ и его состав успешно обновлены"})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"msg": "Ошибка БД", "error": str(e)}), 500


@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    """Удаление заказа (только для Админа)."""
    if not check_is_admin():
        return jsonify({"msg": "Доступ запрещен"}), 403

    order = Order.query.get_or_404(order_id)

    db.session.delete(order)
    db.session.commit()
    return jsonify({"msg": "Заказ успешно удален"})

@app.route('/api/pickup-points', methods=['GET'])
def get_pickup_points():
    """Получение пунктов выдачи для выпадающего списка"""
    points = PickupPoint.query.all()
    return jsonify([{
        "id": p.id, 
        "address": f"{p.city}, {p.street}, {p.house} (индекс: {p.index})"
    } for p in points])

@app.route('/api/statuses', methods=['GET'])
def get_order_statuses():
    """Получение статусов заказов для выпадающего списка"""
    statuses = Status.query.all()
    return jsonify([{"id": s.id, "name": s.name} for s in statuses])

@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    """Получение списка пользователей"""
    if not check_is_staff():
        return jsonify({"msg": "Доступ запрещен"}), 403
    users = User.query.all()
    return jsonify([{"id": u.id, "name": u.full_name} for u in users])


if __name__ == '__main__':
    app.run(debug=True, port=5000)
