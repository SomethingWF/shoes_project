"""
Модуль Pydantic схем для валидации входящих данных API
"""
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field, field_validator

class LoginSchema(BaseModel):
    """Схема для авторизации пользователя"""
    login: str
    password: str

class ProductSchema(BaseModel):
    """Схема для создания и редактирования товара"""
    article: str
    name: str
    price: float = Field(ge=0.0, description="Цена не может быть отрицательной")
    discount: int = Field(ge=0, le=100, description="Скидка от 0 до 100")
    quantity: int = Field(ge=0, description="Количество не может быть отрицательным")
    description: str
    category_id: int
    manufacturer_id: int
    supplier_id: int

class OrderItemSchema(BaseModel):
    """Схема одного товара внутри заказа"""
    product_id: int
    count: int = Field(gt=0, description="Количество товара должно быть больше нуля")

class OrderCreateSchema(BaseModel):
    """Схема для создания нового заказа"""
    order_date: date
    delivery_date: date
    code: int
    user_id: int
    point_id: int
    status_id: int
    items: List[OrderItemSchema]

    @field_validator('items')
    @classmethod
    def items_must_not_be_empty(cls, v: List[OrderItemSchema]) -> List[OrderItemSchema]:
        """Проверяет, что список товаров не пуст"""
        if not v:
            raise ValueError('Список товаров не может быть пустым')
        return v

class OrderUpdateSchema(BaseModel):
    """Схема редактирования заказа."""
    status_id: Optional[int] = None
    point_id: Optional[int] = None
    user_id: Optional[int] = None
    order_date: Optional[date] = None
    delivery_date: Optional[date] = None
    items: Optional[List[OrderItemSchema]] = None

    model_config = {
        "coerce_numbers_to_str": True,
        "populate_by_name": True
    }
