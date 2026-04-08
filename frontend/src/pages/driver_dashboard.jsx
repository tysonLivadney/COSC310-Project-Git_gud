import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api';

const NEXT_ACTION = {
  assigned:   { label: 'Confirm Pickup', endpoint: 'pickup' },
  picked_up:  { label: 'Start Transit',  endpoint: 'transit' },
  in_transit: { label: 'Mark Delivered', endpoint: 'complete' },
};

const DriverDashboard = () => {
  const { user, logout } = useAuth();
  const [deliveries, setDeliveries] = useState([]);
  const [error, setError] = useState('');
  const [actionError, setActionError] = useState('');

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

  const handleAction = async (deliveryId, endpoint) => {
    try {
      setActionError('');
      await api.patch(`/deliveries/${deliveryId}/${endpoint}`);
      fetchDeliveries();
    } catch (err) {
      setActionError(err.response?.data?.detail || 'Action failed.');
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '40px auto', padding: '0 20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1>Driver Dashboard</h1>
        <button onClick={logout} style={{ padding: '8px 16px', cursor: 'pointer' }}>
          Logout
        </button>
      </div>

      {error && <p style={{ color: 'red' }}>{error}</p>}
      {actionError && <p style={{ color: 'red' }}>{actionError}</p>}

      {deliveries.length === 0 ? (
        <p>No deliveries assigned to you.</p>
      ) : (
        deliveries.map(delivery => {
          const action = NEXT_ACTION[delivery.status];
          return (
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

              {action ? (
                <button
                  onClick={() => handleAction(delivery.id, action.endpoint)}
                  style={{ marginTop: '10px', padding: '8px 16px', cursor: 'pointer' }}
                >
                  {action.label}
                </button>
              ) : (
                <p style={{ marginTop: '10px', color: '#888' }}>Delivery complete</p>
              )}
            </div>
          );
        })
      )}
    </div>
  );
};

export default DriverDashboard;
