import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getOrderById } from '../api/orders';
import { useAuth } from '../context/AuthContext';
import api from '../api';

const OrderDetail = () => {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const { addToBalance } = useAuth();
  const [order, setOrder] = useState(null);

  useEffect(() => {
    if (orderId) {
      getOrderById(orderId)
        .then(data => setOrder(data))
        .catch(err => console.error("API Error:", err));
    }
  }, [orderId]);

  if (!order) return <div style={{ color: 'white', padding: '20px' }}>Loading...</div>;

  const subtotal = order.items?.reduce((acc, item) => acc + (Number(item.unit_price) * item.quantity), 0) || 0;
  const tax = subtotal * 0.13;
  const deliveryFee = 1.49;
  const discountAmount = order.discount ? Number(order.discount) : 0;
  const totalAmount = subtotal + tax + deliveryFee - discountAmount;

  const handleRefund = async () => {
    const refundTotal = totalAmount;
  
    try {
      await api.delete(`/orders/${orderId}`); 
      addToBalance(refundTotal);
      
      alert(`Order refunded! $${refundTotal.toFixed(2)} added to your wallet.`);
      navigate('/customer-dashboard');
    } catch (err) {
      console.error("Action failed:", err);
      alert("Could not process request. Ensure the order is in a state that can be cancelled.");
    }
  };

  const handleCancel = async () => {
    try {
      await api.delete(`/orders/${orderId}`);
      alert("Order deleted/cancelled.");
      navigate('/my-orders');
    } catch (err) {
      console.error("Cancel failed:", err);
    }
  };

  return (
    <div style={containerStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '30px', alignItems: 'center' }}>
        <button onClick={() => navigate('/my-orders')} style={backBtnStyle}>
          ← Back
        </button>

        <div style={{ display: 'flex', gap: '10px' }}>
          {(order.status === 'draft') && (
            <button onClick={handleCancel} style={cancelBtnStyle}>Cancel Order</button>
          )}

          {order.status === 'confirmed' && (
            <button onClick={handleRefund} style={refundBtnStyle}>Request Refund</button>
          )}
        </div>
      </div>

      <h1 style={{ marginBottom: '10px' }}>Order Details</h1>
      <p style={{ color: '#888', marginBottom: '30px', fontSize: '1rem' }}>
        Status: <span style={statusBadge(order.status)}>{order.status}</span>
      </p>
      
      <div style={cardStyle}>
        <h3 style={{ marginTop: 0, borderBottom: '1px solid #333', paddingBottom: '15px', fontSize: '1.2rem' }}>Items</h3>
        
        {order.items?.map((item, idx) => (
          <div key={idx} style={itemRow}>
            <div>
              <div style={{ fontWeight: 'bold', fontSize: '1rem' }}>{item.food_item}</div>
              <div style={{ fontSize: '0.9rem', color: '#888', marginTop: '4px' }}>
                ${Number(item.unit_price).toFixed(2)} × {item.quantity}
              </div>
            </div>
            <span style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>
              ${(Number(item.unit_price) * item.quantity).toFixed(2)}
            </span>
          </div>
        ))}
        
        <div style={{ borderTop: '2px solid #333', marginTop: '20px', paddingTop: '20px' }}>
          <div style={summaryRow}>
            <span>Subtotal:</span>
            <span>${subtotal.toFixed(2)}</span>
          </div>
          <div style={summaryRow}>
            <span>Delivery Fee:</span>
            <span>${deliveryFee.toFixed(2)}</span>
          </div>
          <div style={summaryRow}>
            <span>Tax (13%):</span>
            <span>${tax.toFixed(2)}</span>
          </div>
          {order.promo_code && (
            <div style={summaryRow}>
              <span>Promo ({order.promo_code}):</span>
              <span style={{ color: '#4caf50' }}>-${discountAmount.toFixed(2)}</span>
            </div>
          )}
          <div style={totalRow}>
            <span><strong>Total:</strong></span>
            <span><strong>${totalAmount.toFixed(2)}</strong></span>
          </div>
        </div>
      </div>

      {order.restaurant_name && (
        <div style={infoCardStyle}>
          <h3 style={{ marginTop: 0, marginBottom: '8px', fontSize: '1rem' }}>Restaurant</h3>
          <p style={{ margin: 0, color: '#bbb' }}>{order.restaurant_name}</p>
        </div>
      )}

      {order.delivery_address && (
        <div style={infoCardStyle}>
          <h3 style={{ marginTop: 0, marginBottom: '8px', fontSize: '1rem' }}>Delivery Address</h3>
          <p style={{ margin: 0, color: '#bbb' }}>{order.delivery_address}</p>
        </div>
      )}
    </div>
  );
};

// Styles
const containerStyle = {
  padding: '40px',
  color: 'white',
  maxWidth: '900px',
  margin: '0 auto',
  backgroundColor: '#121212',
  minHeight: '100vh',
  fontFamily: 'sans-serif'
};

const cardStyle = {
  backgroundColor: '#1e1e1e',
  padding: '30px',
  borderRadius: '12px',
  border: '1px solid #333',
  marginBottom: '20px'
};

const infoCardStyle = {
  backgroundColor: '#1e1e1e',
  padding: '20px',
  borderRadius: '12px',
  border: '1px solid #333',
  marginTop: '20px'
};

const itemRow = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'flex-start',
  padding: '15px 0',
  borderBottom: '1px solid #2a2a2a'
};

const summaryRow = {
  display: 'flex',
  justifyContent: 'space-between',
  margin: '10px 0',
  fontSize: '1rem',
  color: '#bbb'
};

const totalRow = {
  display: 'flex',
  justifyContent: 'space-between',
  borderTop: '2px solid #444',
  marginTop: '15px',
  paddingTop: '15px',
  fontSize: '1.3rem'
};

const backBtnStyle = {
  color: '#007bff',
  background: 'none',
  border: 'none',
  cursor: 'pointer',
  fontSize: '1rem',
  fontWeight: '500'
};

const cancelBtnStyle = {
  border: '1px solid #ff4444',
  color: '#ff4444',
  background: 'none',
  padding: '10px 20px',
  borderRadius: '8px',
  cursor: 'pointer',
  fontWeight: 'bold',
  fontSize: '0.9rem'
};

const refundBtnStyle = {
  backgroundColor: '#ffc107',
  color: '#000',
  border: 'none',
  padding: '10px 20px',
  borderRadius: '8px',
  cursor: 'pointer',
  fontWeight: 'bold',
  fontSize: '0.9rem'
};

const statusBadge = (status) => ({
  display: 'inline-block',
  backgroundColor: status === 'delivered' ? '#4caf50' : 
                   status === 'cancelled' ? '#f44336' : 
                   status === 'confirmed' ? '#2196f3' : 
                   status === 'refunded' ? '#ff9800' : '#ff9800',
  color: 'white',
  padding: '6px 14px',
  borderRadius: '20px',
  fontSize: '0.8rem',
  fontWeight: 'bold',
  textTransform: 'uppercase',
  marginLeft: '8px'
});

export default OrderDetail;