import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/login', {
        login,
        password
      });

      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('userFullName', response.data.user_fullname);
      localStorage.setItem('roleId', response.data.user_role_id);
      
      navigate('/products');
    } catch (err) {
      console.error("Ошибка при входе:", err);
      setError('Неверный логин или пароль');
    }
  };

  const handleGuest = () => {
    localStorage.clear();
    navigate('/products');
  };

  return (
    <div className="login-container">
      <h2>Авторизация</h2>
      <form onSubmit={handleLogin}>
        <input 
          type="text" 
          placeholder="Логин (Email)" 
          value={login} 
          onChange={(e) => setLogin(e.target.value)} 
          required 
        />
        <input 
          type="password" 
          placeholder="Пароль" 
          value={password} 
          onChange={(e) => setPassword(e.target.value)} 
          required 
        />
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <button type="submit">Войти</button>
      </form>
      <button onClick={handleGuest} style={{ backgroundColor: '#ccc' }}>Продолжить как гость</button>
    </div>
  );
};

export default LoginPage;