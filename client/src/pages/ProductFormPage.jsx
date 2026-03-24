import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useLocation } from 'react-router-dom';

const ProductFormPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const editingProduct = location.state?.product || null;

  const [categories, setCategories] = useState([]);
  const [manufacturers, setManufacturers] = useState([]);
  const [suppliers, setSuppliers] = useState([]);

  const [formData, setFormData] = useState({
    article: editingProduct ? editingProduct.article : '',
    name: editingProduct ? editingProduct.name : '',
    price: editingProduct ? editingProduct.price : 0,
    discount: editingProduct ? editingProduct.discount : 0,
    quantity: editingProduct ? editingProduct.quantity : 0,
    description: editingProduct ? editingProduct.description : '',
    category_id: editingProduct ? editingProduct.category_id : '',
    manufacturer_id: editingProduct ? editingProduct.manufacturer_id : '',
    supplier_id: editingProduct ? editingProduct.supplier_id : '',
  });

  const [imageFile, setImageFile] = useState(null);

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/api/categories').then(res => setCategories(res.data));
    axios.get('http://127.0.0.1:5000/api/manufacturers').then(res => setManufacturers(res.data));
    axios.get('http://127.0.0.1:5000/api/suppliers').then(res => setSuppliers(res.data));
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleFileChange = (e) => {
    setImageFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const data = new FormData();
    for (const key in formData) {
      data.append(key, formData[key]);
    }
    if (imageFile) {
      data.append('image', imageFile);
    }

    const token = localStorage.getItem('token');
    const headers = { 
      Authorization: `Bearer ${token}`,
      'Content-Type': 'multipart/form-data' 
    };

    try {
      if (editingProduct) {
        await axios.put(`http://127.0.0.1:5000/api/products/${editingProduct.id}`, data, { headers });
        alert('Товар обновлен!');
      } else {
        await axios.post('http://127.0.0.1:5000/api/products', data, { headers });
        alert('Товар добавлен!');
      }
      navigate('/products');
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.msg || 'Произошла ошибка');
    }
  };

  return (
    <div style={{ padding: '20px', backgroundColor: 'white', maxWidth: '600px', margin: '0 auto' }}>
      <button onClick={() => navigate(-1)} style={{ marginBottom: '20px' }}>&larr; Назад</button>
      <h2>{editingProduct ? 'Редактирование товара' : 'Добавление товара'}</h2>
      
      <form onSubmit={handleSubmit} className="product-form">
        <label>Артикул:</label>
        <input type="text" name="article" value={formData.article} onChange={handleChange} required />

        <label>Наименование:</label>
        <input type="text" name="name" value={formData.name} onChange={handleChange} required />

        <label>Категория:</label>
        <select name="category_id" value={formData.category_id} onChange={handleChange} required>
          <option value="" disabled>Выберите категорию</option>
          {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>

        <label>Производитель:</label>
        <select name="manufacturer_id" value={formData.manufacturer_id} onChange={handleChange} required>
          <option value="" disabled>Выберите производителя</option>
          {manufacturers.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
        </select>

        <label>Поставщик:</label>
        <select name="supplier_id" value={formData.supplier_id} onChange={handleChange} required>
          <option value="" disabled>Выберите поставщика</option>
          {suppliers.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>

        <label>Цена:</label>
        <input type="number" name="price" value={formData.price} onChange={handleChange} min="0" step="0.01" required />

        <label>Скидка (%):</label>
        <input type="number" name="discount" value={formData.discount} onChange={handleChange} min="0" max="100" />

        <label>Количество на складе:</label>
        <input type="number" name="quantity" value={formData.quantity} onChange={handleChange} min="0" required />

        <label>Описание:</label>
        <textarea name="description" value={formData.description} onChange={handleChange} rows="3" required></textarea>

        <label>Фотография товара (max 300x200):</label>
        <input type="file" accept="image/png, image/jpeg" onChange={handleFileChange} />

        <button type="submit" className="btn-add" style={{ marginTop: '20px' }}>Сохранить товар</button>
      </form>
    </div>
  );
};

export default ProductFormPage;