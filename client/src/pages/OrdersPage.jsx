import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import OrderCard from '../components/OrderCard';

const OrdersPage = () => {
  const [orders, setOrders] = useState([]);
  const navigate = useNavigate();
  
  const token = localStorage.getItem('token');
  const roleId = localStorage.getItem('roleId');
  const isAdmin = roleId === '1';

  const fetchOrders = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/api/orders', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setOrders(res.data);
    } catch (err) {
      console.error(err);
      alert('Ошибка доступа к заказам');
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const handleDelete = async (id) => {
    if (window.confirm('Удалить заказ?')) {
      await axios.delete(`http://127.0.0.1:5000/api/orders/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchOrders();
    }
  };

  return (
    <div>
      <div className="header">
        <h1>Список заказов</h1>
        <button className="btn-secondary" onClick={() => navigate('/products')}>&larr; К товарам</button>
      </div>

      {isAdmin && (
        <div className="actions-bar">
          <button className="btn-add" onClick={() => navigate('/order-form')}>
            + Создать новый заказ
          </button>
        </div>
      )}

      <div className="orders-list">
        {orders.map(order => (
          <OrderCard 
            key={order.id} 
            order={order} 
            isAdmin={isAdmin} 
            onEdit={(o) => navigate('/order-form', { state: { order: o } })} 
            onDelete={handleDelete}
          />
        ))}
      </div>
    </div>
  );
};

export default OrdersPage;