import React from 'react';
import './App.css';
import RestaurantList from './components/Restaurants/Restaurants';
import ManagerDashboard from './pages/ManagerDashboard';
import Login from './pages/login';
import Register from './pages/Register';
import CartPage from "./pages/CartPage";
import CheckoutPage from "./pages/CheckoutPage";
import SuccessPage from "./pages/SuccessPage";
import FailurePage from "./pages/FailurePage";
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
        <Route path="/cart" element={<CartPage />} />
        <Route path="/checkout" element={<CheckoutPage />} />
        <Route path="/success" element={<SuccessPage />} />
        <Route path="/payment-failed" element={<FailurePage />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;