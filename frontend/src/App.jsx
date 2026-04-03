import React from 'react';
import './App.css';
import RestaurantList from './components/Restaurants/Restaurants';
import ManagerDashboard from './pages/ManagerDashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/restaurants" element={<RestaurantList />} />
        <Route path="/manager" element={<ManagerDashboard />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;