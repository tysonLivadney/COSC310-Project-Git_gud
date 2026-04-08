import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';

const STATUSES = ['all', 'draft', 'confirmed', 'completed', 'cancelled'];

const AdminDashboard = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const [orders, setOrders] = useState([]);
  const [statusFilter, setStatusFilter] = useState('all');
  const [error, setError] = useState('');

  const fetchOrders = async (status) => {
    try {
      const params = status !== 'all' ? { status } : {};
      const res = await api.get('/admin/orders', { params });
      setOrders(res.data);
      setError('');
    } catch {
      setError('Failed to load orders. Make sure you are logged in as a manager.');
    }
  };

  useEffect(() => {
    fetchOrders(statusFilter);
  }, [statusFilter]);

  return (
    <div style={{ maxWidth: '1000px', margin: '40px auto', padding: '0 20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1>Admin Dashboard</h1>
        <button onClick={() => { logout(); navigate('/login'); }} style={{ padding: '8px 16px', cursor: 'pointer' }}>
          Logout
        </button>
      </div>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {/* Orders Section */}
      <section style={{ marginBottom: '40px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 style={{ margin: 0 }}>Orders</h2>
          <select
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
            style={{ padding: '6px 12px', cursor: 'pointer' }}
          >
            {STATUSES.map(s => (
              <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
            ))}
          </select>
        </div>

        {orders.length === 0 ? (
          <p style={{ color: '#888' }}>No orders found.</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #444', textAlign: 'left' }}>
                <th style={{ padding: '8px' }}>Order ID</th>
                <th style={{ padding: '8px' }}>Customer</th>
                <th style={{ padding: '8px' }}>Restaurant</th>
                <th style={{ padding: '8px' }}>Status</th>
                <th style={{ padding: '8px' }}>Date</th>
              </tr>
            </thead>
            <tbody>
              {orders.map(order => (
                <tr key={order.id} style={{ borderBottom: '1px solid #2a2a2a' }}>
                  <td style={{ padding: '8px', fontFamily: 'monospace', fontSize: '12px' }}>{order.id}</td>
                  <td style={{ padding: '8px', fontFamily: 'monospace', fontSize: '12px' }}>{order.customer_id}</td>
                  <td style={{ padding: '8px' }}>{order.restaurant_id}</td>
                  <td style={{ padding: '8px' }}>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      backgroundColor:
                        order.status === 'completed' ? '#1a3a1a' :
                        order.status === 'confirmed' ? '#1a2a3a' :
                        order.status === 'cancelled' ? '#3a1a1a' : '#2a2a2a',
                      color:
                        order.status === 'completed' ? '#4caf50' :
                        order.status === 'confirmed' ? '#64b5f6' :
                        order.status === 'cancelled' ? '#ef5350' : '#aaa',
                    }}>
                      {order.status}
                    </span>
                  </td>
                  <td style={{ padding: '8px', fontSize: '12px' }}>{new Date(order.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
};

export default AdminDashboard;
