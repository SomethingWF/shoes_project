import React from 'react';
import PropTypes from 'prop-types';

const OrderCard = ({ order, isAdmin, onEdit, onDelete }) => {
  return (
    <div className="order-card">
      <div className="order-main-info">
        <div><strong>Номер заказа:</strong> {order.id}</div>
        <div><strong>Состав заказа:</strong> {order.items.map(i => i.product_name).join(', ')}</div>
        <div className="order-items-list">
          {order.items.map((item, idx) => (
            <div key={idx}>— {item.article} | {item.product_name} ({item.count} шт.)</div>
          ))}
        </div>
        <div><strong>Статус заказа:</strong> {order.status}</div>
        <div><strong>Пункт выдачи:</strong> {order.pickup_point}</div>
        <div><strong>Дата заказа:</strong> {order.order_date}</div>
        <div><strong>Заказчик:</strong> {order.user_name}</div>
        
        {isAdmin && (
          <div className="admin-actions">
            <button className="btn-edit" onClick={() => onEdit(order)}>Редактировать</button>
            <button className="btn-delete" onClick={() => onDelete(order.id)}>Удалить</button>
          </div>
        )}
      </div>

      <div className="order-delivery-info">
        Дата доставки: <br />
        {order.delivery_date}
      </div>
    </div>
  );
};

OrderCard.propTypes = {
  order: PropTypes.shape({
    id: PropTypes.number.isRequired,
    order_date: PropTypes.string.isRequired,
    delivery_date: PropTypes.string.isRequired,
    status: PropTypes.string.isRequired,
    pickup_point: PropTypes.string.isRequired,
    user_name: PropTypes.string.isRequired,
    items: PropTypes.arrayOf(PropTypes.shape({
      article: PropTypes.string,
      product_name: PropTypes.string,
      count: PropTypes.number,
    })).isRequired,
  }).isRequired,
  isAdmin: PropTypes.bool.isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
};

export default OrderCard;