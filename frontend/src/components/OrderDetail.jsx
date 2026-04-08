import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getOrderById, cancelOrder } from '../api/orders';
import { useAuth } from '../context/AuthContext';
import api from '../api'; // Ensure you import your api instance

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
  const totalAmount = subtotal + tax + deliveryFee;

  const handleRefund = async () => {
    const subtotal = order.items?.reduce((acc, item) => acc + (Number(item.unit_price) * item.quantity), 0) || 0;
    const refundTotal = subtotal + (subtotal * 0.13) + 1.49;
  
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
    <div style={{ padding: '20px', color: 'white', maxWidth: '600px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <button onClick={() => navigate('/my-orders')} style={{ color: '#007bff', background: 'none', border: 'none', cursor: 'pointer' }}>
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

      <h2>Order Details ({order.status})</h2>
      
      <div style={{ backgroundColor: '#1e1e1e', padding: '20px', borderRadius: '12px' }}>
        {order.items?.map((item, idx) => (
          <div key={idx} style={row}>
            <span>{item.food_item} x{item.quantity}</span>
            <span>${(Number(item.unit_price) * item.quantity).toFixed(2)}</span>
          </div>
        ))}
        <div style={{ borderTop: '1px solid #333', marginTop: '10px', paddingTop: '10px' }}>
          <div style={row}><span>Total Paid:</span> <strong>${totalAmount.toFixed(2)}</strong></div>
        </div>
      </div>
    </div>
  );
};

// Styles
const row = { display: 'flex', justifyContent: 'space-between', margin: '5px 0' };
const cancelBtnStyle = { border: '1px solid #ff4444', color: '#ff4444', background: 'none', padding: '5px 10px', borderRadius: '4px', cursor: 'pointer' };
const refundBtnStyle = { backgroundColor: '#ffc107', color: '#000', border: 'none', padding: '5px 10px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' };

export default OrderDetail;