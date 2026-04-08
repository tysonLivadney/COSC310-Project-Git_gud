import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';

const DeliveryDetail = () => {
  const { deliveryId } = useParams();
  const navigate = useNavigate();
  const [delivery, setDelivery] = useState(null);

  useEffect(() => {
    const fetchDelivery = async () => {
      try {
        const res = await api.get(`/deliveries/${deliveryId}`);
        setDelivery(res.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchDelivery();
  }, [deliveryId]);

  const handleCancelDelivery = async () => {
    if (window.confirm("Are you sure you want to cancel this delivery?")) {
      try {
        // Calls your PATCH /{delivery_id}/cancel endpoint
        await api.patch(`/deliveries/${deliveryId}/cancel`);
        alert("Delivery cancelled successfully.");
        navigate('/customer-dashboard');
      } catch (err) {
        alert(err.response?.data?.detail || "Failed to cancel delivery.");
      }
    }
  };

  if (!delivery) return <div style={{color: 'white'}}>Loading...</div>;

  return (
    <div style={containerStyle}>
      <button onClick={() => navigate(-1)} style={backBtn}>← Back</button>
      
      <div style={detailCard}>
        <h2>Delivery Status: <span style={{color: '#ff9800'}}>{delivery.status}</span></h2>
        <hr style={{borderColor: '#333'}} />
        
        <div style={section}>
          <h4>Addresses</h4>
          <p><strong>Pickup:</strong> {delivery.pickup_address}</p>
          <p><strong>Dropoff:</strong> {delivery.dropoff_address}</p>
        </div>

        {delivery.driver && (
          <div style={section}>
            <h4>Driver Details</h4>
            <p><strong>Name:</strong> {delivery.driver.name}</p>
            <p><strong>Phone:</strong> {delivery.driver.phone}</p>
          </div>
        )}

        {/* Cancel button: Only show if not already delivered or cancelled */}
        {['pending', 'assigned', 'picked_up'].includes(delivery.status) && (
          <button onClick={handleCancelDelivery} style={cancelBtn}>
            Cancel Delivery
          </button>
        )}
      </div>
    </div>
  );
};

// --- Styles ---
const containerStyle = { padding: '40px', color: 'white', maxWidth: '800px', margin: '0 auto' };
const detailCard = { backgroundColor: '#1e1e1e', padding: '30px', borderRadius: '12px', border: '1px solid #333' };
const section = { marginBottom: '20px' };
const backBtn = { background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', marginBottom: '20px' };
const cancelBtn = { backgroundColor: '#ff4444', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', marginTop: '20px' };

export default DeliveryDetail;