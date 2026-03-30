import React from 'react';
import './App.css';
import RestaurantList from './components/Restaurants/Restaurants';
import Manager from './components/Manager/Manager';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/restaurants" element={<RestaurantList />} />
        <Route path="/" element={<Manager />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;