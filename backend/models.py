"""
Модели данных приложения.

Этот файл определяет классы моделей SQLAlchemy, которые соответствуют
таблицам базы данных, и устанавливает связи между ними.
"""

from db import db

class Role(db.Model):
    """
    Представляет роль пользователя в системе.
    """
    __tablename__ = 'Role'
    id = db.Column('RoleID', db.BigInteger, primary_key=True)
    name = db.Column('RoleName', db.String(255), nullable=False)

class Category(db.Model):
    """
    Представляет категорию товара.
    """
    __tablename__ = 'Category'
    id = db.Column('CategoryID', db.BigInteger, primary_key=True)
    name = db.Column('CategoryName', db.String(255), nullable=False)

class Manufacturer(db.Model):
    """
    Представляет производителя товара.
    """
    __tablename__ = 'Manufacturer'
    id = db.Column('ManufacturerID', db.BigInteger, primary_key=True)
    name = db.Column('ManufacturerName', db.String(255), nullable=False)

class Supplier(db.Model):
    """
    Представляет поставщика товара.
    """
    __tablename__ = 'Supplier'
    id = db.Column('SuplierID', db.BigInteger, primary_key=True)
    name = db.Column('SupplierName', db.String(255), nullable=False)

class Status(db.Model):
    """
    Представляет статус заказа.
    """
    __tablename__ = 'Status'
    id = db.Column('StatusID', db.BigInteger, primary_key=True)
    name = db.Column('StatusName', db.String(255), nullable=False)

class PickupPoint(db.Model):
    """
    Представляет пункт выдачи заказов.
    """
    __tablename__ = 'PickupPoint'
    id = db.Column('PickupPointID', db.BigInteger, primary_key=True)
    index = db.Column('PostIndex', db.BigInteger, nullable=False)
    city = db.Column('City', db.String(255), nullable=False)
    street = db.Column('Street', db.String(255), nullable=False)
    house = db.Column('HouseNumber', db.BigInteger, nullable=False)

class User(db.Model):
    """
    Представляет пользователя системы.
    """
    __tablename__ = 'User'
    id = db.Column('UserID', db.BigInteger, primary_key=True)
    full_name = db.Column('UserFullName', db.String(255), nullable=False)
    login = db.Column('UserLogin', db.String(255), nullable=False)
    password = db.Column('UserPassword', db.String(255), nullable=False)

    role_id = db.Column('UserRoleID', db.BigInteger, db.ForeignKey('Role.RoleID'), nullable=False)

    role = db.relationship('Role')

class Product(db.Model):
    """
    Представляет товар в каталоге.
    """
    __tablename__ = 'Product'
    id = db.Column('ProductID', db.BigInteger, primary_key=True)
    article = db.Column('ProductArticle', db.String(255), nullable=False)
    name = db.Column('ProductName', db.String(255), nullable=False)
    price = db.Column('ProductPrice', db.Float, nullable=False)
    discount = db.Column('ProductDiscount', db.BigInteger, nullable=False)
    quantity = db.Column('ProductQuantityInStock', db.BigInteger, nullable=False)
    description = db.Column('ProductDescription', db.String(255), nullable=False)
    icon_link = db.Column('ProductIconLink', db.String(255), nullable=False)

    category_id = db.Column('ProductCategoryID', db.BigInteger,
                            db.ForeignKey('Category.CategoryID'), nullable=False)
    manufacturer_id = db.Column('ProductManufacturerID', db.BigInteger,
                                db.ForeignKey('Manufacturer.ManufacturerID'), nullable=False)
    supplier_id = db.Column('ProductSupplierID', db.BigInteger,
                            db.ForeignKey('Supplier.SuplierID'), nullable=False)

    category = db.relationship('Category')
    manufacturer = db.relationship('Manufacturer')
    supplier = db.relationship('Supplier')

    def to_dict(self):
        """Конвертер в JSON для API"""
        return {
            "id": self.id,
            "article": self.article,
            "name": self.name,
            "price": self.price,
            "discount": self.discount,
            "quantity": self.quantity,
            "description": self.description,
            "icon_link": self.icon_link,
            "category_name": self.category.name if self.category else None,
            "manufacturer_name": self.manufacturer.name if self.manufacturer else None,
            "supplier_name": self.supplier.name if self.supplier else None
        }

class Order(db.Model):
    """
    Представляет заказ, сделанный пользователем.
    """
    __tablename__ = 'Order'
    id = db.Column('OrderID', db.BigInteger, primary_key=True)
    date = db.Column('OrderDate', db.Date, nullable=False)
    delivery_date = db.Column('OrderDeliveryDate', db.Date, nullable=False)
    code = db.Column('OrderCode', db.BigInteger, nullable=False)

    user_id = db.Column('OrderUserID', db.BigInteger,
                        db.ForeignKey('User.UserID'), nullable=False)
    point_id = db.Column('OrderPickupPointID', db.BigInteger,
                         db.ForeignKey('PickupPoint.PickupPointID'), nullable=False)
    status_id = db.Column('OrderStatusID', db.BigInteger,
                          db.ForeignKey('Status.StatusID'), nullable=False)

    user = db.relationship('User')
    pickup_point = db.relationship('PickupPoint')
    status = db.relationship('Status')

    products_in_order = db.relationship('OrderProduct', backref='order',
                                        lazy=True, cascade="all, delete-orphan")

class OrderProduct(db.Model):
    """
    Связующая модель для товаров в заказе.
    """
    __tablename__ = 'OrderProduct'
    id = db.Column('OrderProductID', db.BigInteger, primary_key=True)
    count = db.Column('ProductCount', db.BigInteger, nullable=False)

    order_id = db.Column('OrderID', db.BigInteger, db.ForeignKey('Order.OrderID'), nullable=False)
    product_id = db.Column('ProductID', db.BigInteger,
                           db.ForeignKey('Product.ProductID'), nullable=False)

    product = db.relationship('Product')
