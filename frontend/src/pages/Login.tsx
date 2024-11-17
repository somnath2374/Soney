import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { login } from '../services/api';
import './Login.css';

interface LoginProps {
  setIsAuthenticated: (isAuthenticated: boolean) => void;
}

const Login: React.FC<LoginProps> = ({ setIsAuthenticated }) => {
  const [user, setUser] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const message = location.state?.message;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(user, password);
      setIsAuthenticated(true);
      alert('Login successful!');
      navigate('/profile');
    } catch (error) {
      alert('Invalid credentials');
    }
  };

  return (
    <div className='login'>
      <h1>Login</h1>
      {message && <p className="login-message">{message}</p>}
      <form onSubmit={handleSubmit}>
        <input type="text" placeholder="User" value={user} onChange={(e) => setUser(e.target.value)} />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default Login;
