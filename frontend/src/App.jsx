import React from 'react';
import './App.css';
import RestaurantList from './components/Restaurants/Restaurants';
import ManagerDashboard from './pages/ManagerDashboard';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/restaurants" element={<RestaurantList />} />
        <Route path="/manager" element={<ManagerDashboard />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;