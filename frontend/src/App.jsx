import './App.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Login from './pages/login';
import Register from './pages/Register';
import RestaurantList from './components/Restaurants/Restaurant';
import ManagerDashboard from './pages/ManagerDashboard';
import CustomerDashboard from './pages/customer_dashboard';
import AdminDashboard from './pages/admin_dashboard';
import DriverDashboard from './pages/driver_dashboard';
import Orders from './components/orders';
import OrderDetail from './components/OrderDetail';
import DeliveryDetail from './components/DeliveryDetail';
import CartPage from './pages/CartPage';
import CheckoutPage from './pages/CheckoutPage';
import SuccessPage from './pages/SuccessPage';
import FailurePage from './pages/FailurePage';

const App = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/restaurants" element={<RestaurantList />} />
          <Route path="/manager" element={<ManagerDashboard />} />
          <Route path="/customer-dashboard" element={<CustomerDashboard />} />
          <Route path="/my-orders" element={<Orders />} />
          <Route path="/delivery/:deliveryId" element={<DeliveryDetail />} />
          <Route path="/my-orders/:orderId" element={<OrderDetail />} />
          <Route path="/admin-dashboard" element={<AdminDashboard />} />
          <Route path="/driver-dashboard" element={<DriverDashboard />} />
          <Route path="/cart" element={<CartPage />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/success" element={<SuccessPage />} />
          <Route path="/payment-failed" element={<FailurePage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
