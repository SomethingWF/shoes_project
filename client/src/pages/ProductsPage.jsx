import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import ProductCard from '../components/ProductCard';

const ProductsPage = () => {
  const [products, setProducts] = useState([]);
  const navigate = useNavigate();
  
  const userFullName = localStorage.getItem('userFullName') || 'Гость';

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/api/products')
      .then(response => {
        setProducts(response.data);
      })
      .catch(error => console.error("Ошибка загрузки товаров:", error));
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
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

      <div className="products-list">
        {products.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
};

export default ProductsPage;