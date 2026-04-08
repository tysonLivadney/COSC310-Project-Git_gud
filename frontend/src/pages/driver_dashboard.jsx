import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api';

const DriverDashboard = () => {
  const { user, logout } = useAuth();
  const [deliveries, setDeliveries] = useState([]);
  const [error, setError] = useState('');

  const fetchDeliveries = async () => {
    try {
      const res = await api.get('/deliveries');
      const mine = res.data.filter(d => d.driver?.id === user?.id);
      setDeliveries(mine);
      setError('');
    } catch {
      setError('Failed to load deliveries.');
    }
  };

  useEffect(() => {
    fetchDeliveries();
  }, []);

  return (
    <div style={{ maxWidth: '800px', margin: '40px auto', padding: '0 20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1>Driver Dashboard</h1>
        <button onClick={logout} style={{ padding: '8px 16px', cursor: 'pointer' }}>
          Logout
        </button>
      </div>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {deliveries.length === 0 ? (
        <p>No deliveries assigned to you.</p>
      ) : (
        deliveries.map(delivery => (
          <div key={delivery.id} style={{
            border: '1px solid #444',
            borderRadius: '8px',
            padding: '20px',
            marginBottom: '16px',
          }}>
            <p><strong>Order ID:</strong> {delivery.order_id}</p>
            <p><strong>Pickup:</strong> {delivery.pickup_address || 'N/A'}</p>
            <p><strong>Dropoff:</strong> {delivery.dropoff_address || 'N/A'}</p>
            <p><strong>Status:</strong> {delivery.status}</p>
          </div>
        ))
      )}
    </div>
  );
};

export default DriverDashboard;
