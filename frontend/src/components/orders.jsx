import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';

const Orders = () => {
  const [orders, setOrders] = useState([]);
  const navigate = useNavigate();
  const { user } = useAuth(); // ← Use the same auth context

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await api.get('/orders/');
        // Filter orders by current user's ID - same as deliveries
        const userOrders = response.data.filter(
          order => order.customer_id === user?.id
        );
        setOrders(userOrders);
      } catch (err) {
        console.error("Failed to fetch orders", err);
      }
    };
    
    if (user?.id) {
      fetchOrders();
    }
  }, [user?.id]);

  const calculateOrderTotal = (items) => {
    if (!items || items.length === 0) return "0.00";
    const subtotal = items.reduce((acc, item) => acc + (item.unit_price * item.quantity), 0);
    const tax = subtotal * 0.13;
    const deliveryFee = 1.49;
    return (subtotal + tax + deliveryFee).toFixed(2);
  };

  return (
    <div style={{ padding: '20px', color: 'white', backgroundColor: '#121212', minHeight: '100vh' }}>
      
      <div style={{ maxWidth: '800px', margin: '0 auto', marginBottom: '20px' }}>
        <button 
          onClick={() => navigate('/customer-dashboard')} 
          style={{ color: '#007bff', cursor: 'pointer', background: 'none', border: 'none', fontSize: '1rem' }}
        >
          ← Back to Dashboard
        </button>
      </div>

      <h2 style={{ textAlign: 'center', marginBottom: '30px' }}>My Orders</h2>
      
      <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {orders.length > 0 ? (
          orders.map(order => (
            <div key={order.id} style={cardStyle}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <strong style={{ fontSize: '1.1rem' }}>Order #{order.id.substring(0, 8)}</strong>
                  <p style={{ fontSize: '0.85rem', color: '#888', margin: '5px 0' }}>
                    Placed: {new Date(order.created_at).toLocaleDateString()}
                  </p>
                </div>
                <span style={statusBadge(order.status)}>{order.status}</span>
              </div>
              
              <div style={{ 
                marginTop: '15px', 
                paddingTop: '15px', 
                borderTop: '1px solid #333', 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center' 
              }}>
                <div>
                  <span style={{ color: '#aaa', fontSize: '0.9rem' }}>Total: </span>
                  <strong style={{ fontSize: '1.2rem', color: '#fff' }}>
                    ${calculateOrderTotal(order.items)}
                  </strong>
                </div>
                <button 
                  onClick={() => navigate(`/my-orders/${order.id}`)} 
                  style={btnStyle}
                >
                  View Details
                </button>
              </div>
            </div>
          ))
        ) : (
          <p style={{ textAlign: 'center', color: '#666' }}>No orders found.</p>
        )}
      </div>
    </div>
  );
};

const cardStyle = { backgroundColor: '#1e1e1e', padding: '20px', borderRadius: '12px', border: '1px solid #333' };
const btnStyle = { backgroundColor: '#007bff', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' };
const statusBadge = (s) => ({
  backgroundColor: s === 'cancelled' ? '#d32f2f' : s === 'confirmed' ? '#2e7d32' : '#444',
  color: 'white', padding: '5px 12px', borderRadius: '20px', fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 'bold'
});

export default Orders;