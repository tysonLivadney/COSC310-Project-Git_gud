import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';

const CustomerDashboard = () => {
  const { balance, user } = useAuth();
  const navigate = useNavigate();
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDeliveries = async () => {
      try {
        const response = await api.get('/deliveries/');
        setDeliveries(response.data);
      } catch (err) {
        console.error("Failed to fetch deliveries", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDeliveries();
  }, []);

  return (
    <div style={containerStyle}>
      {/* HEADER SECTION */}
      <header style={headerStyle}>
        <div>
          <h1 style={{ margin: 10 }}>Hello, {user?.name || 'Customer'}</h1>
          <p style={{ color: '#aaa' }}>Track your food and manage your account.</p>
        </div>
        
        <div style={{ textAlign: 'right' }}>
          <div style={balanceCard}>
            <span style={{ fontSize: '0.75rem', color: '#888', fontWeight: 'bold' }}>WALLET BALANCE</span>
            <h2 style={{ margin: '5px 0', color: '#4caf50' }}>${balance.toFixed(2)}</h2>
          </div>
          
          {/* THE BUTTON */}
          <button 
            onClick={() => navigate('/my-orders')} 
            style={orderBtnStyle}
          >
            View My Orders →
          </button>
        </div>
      </header>

      {/* ACTIVE DELIVERIES SECTION */}
      <section>
        <h3 style={{ borderBottom: '1px solid #333', paddingBottom: '10px' }}>Active Deliveries</h3>
        {loading ? (
          <p>Loading your orders...</p>
        ) : deliveries.length > 0 ? (
          <div style={gridStyle}>
            {deliveries.map((delivery) => (
              <div 
                key={delivery.id} 
                style={cardStyle} 
                onClick={() => navigate(`/delivery/${delivery.id}`)}
              >
                <div style={cardHeader}>
                  <span style={statusBadge(delivery.status)}>{delivery.status}</span>
                  <small style={{ color: '#666' }}>ID: {delivery.id.slice(0, 6)}</small>
                </div>
                
                <div style={{ margin: '15px 0' }}>
                  <p style={addressText}>📍 <strong>From:</strong> {delivery.pickup_address}</p>
                  <p style={addressText}>🏠 <strong>To:</strong> {delivery.dropoff_address}</p>
                </div>

                <div style={cardFooter}>View Details & Manage →</div>
              </div>
            ))}
          </div>
        ) : (
          <div style={emptyState}>No active deliveries found.</div>
        )}
      </section>
    </div>
  );
};

// --- NEW BUTTON STYLE ---
const orderBtnStyle = {
  marginTop: '12px',
  backgroundColor: '#1e1e1e',
  color: '#007bff',
  border: '1px solid #333',
  padding: '10px 20px',
  borderRadius: '8px',
  cursor: 'pointer',
  fontWeight: 'bold',
  fontSize: '0.9rem',
  transition: 'all 0.2s'
};

// --- REST OF YOUR STYLES ---
const containerStyle = { padding: '30px', color: 'white', backgroundColor: '#121212', minHeight: '100vh', fontFamily: 'sans-serif' };
const headerStyle = { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '40px' };
const balanceCard = { backgroundColor: '#1e1e1e', padding: '15px 25px', borderRadius: '12px', border: '1px solid #333' };
const gridStyle = { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' };
const cardStyle = { backgroundColor: '#1e1e1e', padding: '20px', borderRadius: '12px', border: '1px solid #333', cursor: 'pointer' };
const cardHeader = { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' };
const addressText = { margin: '4px 0', fontSize: '0.9rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' };
const cardFooter = { marginTop: '15px', color: '#007bff', fontSize: '0.85rem', fontWeight: 'bold' };
const emptyState = { padding: '40px', textAlign: 'center', color: '#555', backgroundColor: '#1a1a1a', borderRadius: '12px' };
const statusBadge = (status) => ({
  backgroundColor: status === 'delivered' ? '#4caf50' : status === 'cancelled' ? '#f44336' : '#ff9800',
  color: 'white', padding: '4px 10px', borderRadius: '20px', fontSize: '0.7rem', fontWeight: 'bold', textTransform: 'uppercase'
});

export default CustomerDashboard;