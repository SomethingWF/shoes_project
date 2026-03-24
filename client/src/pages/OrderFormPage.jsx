import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useLocation } from 'react-router-dom';

const OrderFormPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const editingOrder = location.state?.order || null;

  const [points, setPoints] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [users, setUsers] = useState([]);
  const [allProducts, setAllProducts] = useState([]);

  const [formData, setFormData] = useState({
    user_id: editingOrder ? String(editingOrder.user_id) : '',
    status_id: editingOrder ? String(editingOrder.status_id) : '2', 
    point_id: editingOrder ? String(editingOrder.point_id) : '',
    delivery_date: editingOrder ? editingOrder.delivery_date : '',
    order_date: editingOrder ? editingOrder.order_date : new Date().toISOString().split('T')[0],
    code: editingOrder ? editingOrder.code : Math.floor(100 + Math.random() * 900),
  });

  const [orderItems, setOrderItems] = useState(editingOrder ? editingOrder.items : []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const headers = { Authorization: `Bearer ${token}` };
    
    axios.get('http://127.0.0.1:5000/api/pickup-points').then(res => setPoints(res.data));
    axios.get('http://127.0.0.1:5000/api/statuses').then(res => setStatuses(res.data));
    axios.get('http://127.0.0.1:5000/api/users', { headers }).then(res => setUsers(res.data));
    axios.get('http://127.0.0.1:5000/api/products').then(res => setAllProducts(res.data));
  }, []);

  const addProductToOrder = (productId) => {
    const product = allProducts.find(p => p.id === parseInt(productId));
    if (product) {
      if (product.quantity <= 0) {
        alert("Этого товара нет в наличии на складе!");
        return;
      }
      if (!orderItems.find(item => item.product_id === product.id)) {
        setOrderItems([...orderItems, { 
          product_id: product.id, 
          product_name: product.name, 
          count: 1,
          max_stock: product.quantity
        }]);
      }
    }
  };

  const handleCountChange = (id, newCount) => {
    const productInStock = allProducts.find(p => p.id === id);
    const stockLimit = productInStock ? productInStock.quantity : 999;

    const count = parseInt(newCount);
    if (count > stockLimit) {
      alert(`Недостаточно товара на складе! Доступно всего: ${stockLimit}`);
      return;
    }
    
    setOrderItems(orderItems.map(item => 
      item.product_id === id ? { ...item, count: count || 0 } : item
    ));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (orderItems.length === 0) return alert("Добавьте хотя бы один товар!");

    const token = localStorage.getItem('token');
    const payload = { 
      ...formData, 
      user_id: parseInt(formData.user_id),
      status_id: parseInt(formData.status_id),
      point_id: parseInt(formData.point_id),
      items: orderItems 
    };

    try {
      if (editingOrder) {
        await axios.put(`http://127.0.0.1:5000/api/orders/${editingOrder.id}`, payload, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        await axios.post('http://127.0.0.1:5000/api/orders', payload, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      navigate('/orders');
    } catch (err) {
      alert(err.response?.data?.msg || 'Ошибка при сохранении заказа');
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '750px', margin: '0 auto', background: 'white', border: '1px solid #ccc' }}>
      <h2>{editingOrder ? `Редактирование заказа №${editingOrder.id}` : 'Оформление нового заказа'}</h2>
      
      <form onSubmit={handleSubmit} className="product-form">
        <label>Заказчик:</label>
        <select value={formData.user_id} onChange={(e) => setFormData({...formData, user_id: e.target.value})} required>
          <option value="">Выберите клиента</option>
          {users.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}
        </select>

        <label>Пункт выдачи:</label>
        <select value={formData.point_id} onChange={(e) => setFormData({...formData, point_id: e.target.value})} required>
          <option value="">Выберите пункт</option>
          {points.map(p => <option key={p.id} value={p.id}>{p.address}</option>)}
        </select>

        <label>Статус заказа:</label>
        <select value={formData.status_id} onChange={(e) => setFormData({...formData, status_id: e.target.value})} required>
          {statuses.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>

        <div style={{ display: 'flex', gap: '20px' }}>
          <div style={{ flex: 1 }}>
            <label>Дата заказа:</label>
            <input type="date" value={formData.order_date} onChange={(e) => setFormData({...formData, order_date: e.target.value})} />
          </div>
          <div style={{ flex: 1 }}>
            <label>Дата доставки:</label>
            <input type="date" value={formData.delivery_date} onChange={(e) => setFormData({...formData, delivery_date: e.target.value})} required />
          </div>
        </div>

        <h3 style={{ borderBottom: '1px solid #000', marginTop: '30px' }}>Состав заказа:</h3>
        
        <select onChange={(e) => { addProductToOrder(e.target.value); e.target.value = ""; }}>
          <option value="">Добавить товар в заказ...</option>
          {allProducts.map(p => (
             <option key={p.id} value={p.id} disabled={p.quantity <= 0}>
               {p.name} (Остаток: {p.quantity} шт.)
             </option>
          ))}
        </select>

        <div style={{ margin: '15px 0' }}>
          {orderItems.map(item => {
            const productInfo = allProducts.find(p => p.id === item.product_id);
            return (
              <div key={item.product_id} style={{ display: 'flex', alignItems: 'center', marginBottom: '10px', padding: '10px', borderBottom: '1px dotted #ccc' }}>
                <span style={{ flex: 1 }}>{item.product_name}</span>
                <div style={{ width: '200px', textAlign: 'right' }}>
                   <input 
                    type="number" 
                    value={item.count} 
                    onChange={(e) => handleCountChange(item.product_id, e.target.value)}
                    style={{ width: '60px' }} 
                    min="1"
                    max={productInfo ? productInfo.quantity : 999}
                  />
                  <span style={{ fontSize: '12px', marginLeft: '5px' }}>
                    / {productInfo ? productInfo.quantity : '?'} шт.
                  </span>
                  <button 
                    type="button" 
                    onClick={() => setOrderItems(orderItems.filter(i => i.product_id !== item.product_id))}
                    style={{ marginLeft: '10px', color: 'red', border: 'none', background: 'none', cursor: 'pointer' }}
                  >
                    ✖
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        <div className="actions-bar">
          <button type="submit" className="btn-add">Сохранить заказ</button>
          <button type="button" className="btn-secondary" onClick={() => navigate('/orders')}>Отмена</button>
        </div>
      </form>
    </div>
  );
};

export default OrderFormPage;