import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import ProductCard from '../components/ProductCard';

const ProductsPage = () => {
  const [products, setProducts] = useState([]);
  const [suppliers, setSuppliers] = useState([]);

  const [search, setSearch] = useState('');
  const [supplierId, setSupplierId] = useState('all');
  const [sortBy, setSortBy] = useState('asc');

  const navigate = useNavigate();
  
  const userFullName = localStorage.getItem('userFullName') || 'Гость';
  const roleId = localStorage.getItem('roleId');
  const isAdmin = roleId === '1';

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/api/suppliers')
      .then(res => setSuppliers(res.data))
      .catch(err => console.error(err));
  }, []);

  const fetchProducts = () => {
    const params = {
      search: search,
      supplier_id: supplierId,
      sort_by: sortBy
    };

    axios.get('http://127.0.0.1:5000/api/products', { params })
      .then(response => setProducts(response.data))
      .catch(error => console.error("Ошибка загрузки товаров:", error));
  };

  useEffect(() => {
    fetchProducts();
  }, [search, supplierId, sortBy]);

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const handleDelete = async (productId) => {
    if (window.confirm('Вы уверены, что хотите удалить этот товар?')) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`http://127.0.0.1:5000/api/products/${productId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        alert('Товар удален');
        fetchProducts();
      } catch (error) {
        alert(error.response?.data?.msg || 'Ошибка при удалении');
      }
    }
  };

  const handleEdit = (product) => {
    navigate('/product-form', { state: { product } });
  };

  return (
    <div>
      <div className="header">
        <h1>Список товаров</h1>
        <div>
          <span style={{ marginRight: '15px', fontWeight: 'bold' }}>{userFullName}</span>
          <button onClick={handleLogout}>Выйти</button>
        </div>
      </div>

      {isAdmin && (
        <div style={{ marginBottom: '20px' }}>
          <button className="btn-add" onClick={() => navigate('/product-form')}>+ Добавить товар</button>
        </div>
      )}

      <div className="controls-panel">
        <input 
          type="text" 
          placeholder="Поиск по названию..." 
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ flexGrow: 1 }}
        />
        
        <select value={supplierId} onChange={(e) => setSupplierId(e.target.value)}>
          <option value="all">Все поставщики</option>
          {suppliers.map(sup => (
            <option key={sup.id} value={sup.id}>{sup.name}</option>
          ))}
        </select>

        <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
          <option value="asc">Сначала меньше на складе</option>
          <option value="desc">Сначала больше на складе</option>
        </select>
      </div>

      <div className="products-list">
        {products.map(product => (
          <ProductCard 
            key={product.id} 
            product={product} 
            isAdmin={isAdmin} 
            onEdit={handleEdit} 
            onDelete={handleDelete} 
          />
        ))}
      </div>
    </div>
  );
};

export default ProductsPage;