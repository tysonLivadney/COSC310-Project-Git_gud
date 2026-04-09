import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';

const STATUSES = ['all', 'draft', 'confirmed', 'completed', 'cancelled'];

const StatusBadge = ({ status }) => {
  const colors = {
    completed: { bg: '#1a3a1a', fg: '#4caf50' },
    confirmed: { bg: '#1a2a3a', fg: '#64b5f6' },
    cancelled: { bg: '#3a1a1a', fg: '#ef5350' },
    delivered: { bg: '#1a3a1a', fg: '#4caf50' },
    assigned:  { bg: '#2a2a1a', fg: '#ffb74d' },
    in_transit:{ bg: '#1a2a3a', fg: '#64b5f6' },
    pending:   { bg: '#2a2a2a', fg: '#aaa' },
  };
  const c = colors[status] || { bg: '#2a2a2a', fg: '#aaa' };
  return (
    <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '12px', backgroundColor: c.bg, color: c.fg }}>
      {status}
    </span>
  );
};

const AdminDashboard = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const [orders, setOrders] = useState([]);
  const [statusFilter, setStatusFilter] = useState('all');
  const [deliveries, setDeliveries] = useState([]);
  const [availableDrivers, setAvailableDrivers] = useState([]);
  const [selectedDriver, setSelectedDriver] = useState({});
  const [report, setReport] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [error, setError] = useState('');
  const [actionError, setActionError] = useState('');

  // promo code state
  const [promoCodes, setPromoCodes] = useState([]);
  const [promoCode, setPromoCode] = useState('');
  const [discountType, setDiscountType] = useState('percentage');
  const [discountValue, setDiscountValue] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [maxUses, setMaxUses] = useState('');
  const [minOrder, setMinOrder] = useState('');
  const [promoError, setPromoError] = useState('');

  const fetchOrders = async (status) => {
    try {
      const params = status !== 'all' ? { status } : {};
      const res = await api.get('/admin/orders', { params });
      setOrders(res.data);
    } catch {
      setError('Failed to load orders. Make sure you are logged in as a manager.');
    }
  };

  const fetchDeliveries = async () => {
    try {
      const res = await api.get('/deliveries');
      setDeliveries(res.data);
    } catch {
      setError('Failed to load deliveries.');
    }
  };

  const fetchAvailableDrivers = async () => {
    try {
      const res = await api.get('/drivers/available');
      setAvailableDrivers(res.data);
    } catch {
      // not critical if this fails
    }
  };

  const fetchPromoCodes = async () => {
    try {
      const res = await api.get('/promo-codes');
      setPromoCodes(res.data);
    } catch {
      // not critical
    }
  };

  useEffect(() => {
    fetchOrders(statusFilter);
  }, [statusFilter]);

  const fetchReviews = async () => {
    try {
      const restRes = await api.get('/restaurants');
      const allReviews = [];
      for (const r of restRes.data) {
        try {
          const revRes = await api.get(`/reviews/restaurant/${r.id}`);
          revRes.data.forEach(rev => allReviews.push({ ...rev, restaurant_name: r.name }));
        } catch {
          // restaurant may have no reviews
        }
      }
      setReviews(allReviews);
    } catch {
      // non-critical
    }
  };

  const fetchReport = async () => {
    try {
      const res = await api.get('/admin/reports');
      setReport(res.data);
    } catch {
      // non-critical
    }
  };

  useEffect(() => {
    fetchDeliveries();
    fetchAvailableDrivers();
    fetchReport();
    fetchReviews();
    fetchPromoCodes();
  }, []);

  const handleAssign = async (deliveryId) => {
    const driverId = selectedDriver[deliveryId];
    if (!driverId) return;
    try {
      setActionError('');
      await api.patch(`/deliveries/${deliveryId}/assign`, null, { params: { driver_id: driverId } });
      fetchDeliveries();
      fetchAvailableDrivers();
    } catch (err) {
      setActionError(err.response?.data?.detail || 'Failed to assign driver.');
    }
  };

  const handleCreatePromo = async (e) => {
    e.preventDefault();
    setPromoError('');
    const payload = {
      code: promoCode,
      discount_type: discountType,
      discount_value: parseFloat(discountValue),
    };
    if (expiryDate) payload.expiry_date = expiryDate + 'T23:59:59';
    if (maxUses) payload.max_uses = parseInt(maxUses);
    if (minOrder) payload.min_order_amount = parseFloat(minOrder);

    try {
      await api.post('/promo-codes', payload);
      setPromoCode(''); setDiscountValue(''); setExpiryDate(''); setMaxUses(''); setMinOrder('');
      fetchPromoCodes();
    } catch (err) {
      setPromoError(err.response?.data?.detail || 'Failed to create promo code');
    }
  };

  const handleDeactivate = async (code) => {
    try {
      await api.delete(`/promo-codes/${code}`);
      fetchPromoCodes();
    } catch {
      setPromoError('Failed to deactivate code');
    }
  };

  const unassigned = deliveries.filter(d => !d.driver);
  const active = deliveries.filter(d => d.driver && d.status !== 'delivered' && d.status !== 'cancelled');

  return (
    <div style={{ maxWidth: '1000px', margin: '40px auto', padding: '0 20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1>Admin Dashboard</h1>
        <button onClick={() => { logout(); navigate('/login'); }} style={{ padding: '8px 16px', cursor: 'pointer' }}>
          Logout
        </button>
      </div>

      {error && <p style={{ color: 'red' }}>{error}</p>}
      {actionError && <p style={{ color: 'red' }}>{actionError}</p>}

      {/* Promo Codes Section */}
      <section style={{ marginBottom: '48px' }}>
        <h2 style={{ marginBottom: '16px' }}>Promo Codes</h2>

        {promoError && <p style={{ color: 'red' }}>{promoError}</p>}

        <form onSubmit={handleCreatePromo} style={{ marginBottom: '20px' }}>
          <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
            <input placeholder="Code (e.g. SAVE20)" value={promoCode} onChange={e => setPromoCode(e.target.value)} required style={{ padding: '6px 10px', flex: 1 }} />
            <select value={discountType} onChange={e => setDiscountType(e.target.value)} style={{ padding: '6px 10px' }}>
              <option value="percentage">Percentage (%)</option>
              <option value="flat">Flat ($)</option>
            </select>
            <input type="number" step="0.01" placeholder={discountType === 'percentage' ? '% off' : '$ off'} value={discountValue} onChange={e => setDiscountValue(e.target.value)} required style={{ padding: '6px 10px', width: '100px' }} />
          </div>
          <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
            <input type="date" value={expiryDate} onChange={e => setExpiryDate(e.target.value)} style={{ padding: '6px 10px', flex: 1 }} />
            <input type="number" placeholder="Max uses" value={maxUses} onChange={e => setMaxUses(e.target.value)} style={{ padding: '6px 10px', width: '100px' }} />
            <input type="number" step="0.01" placeholder="Min order $" value={minOrder} onChange={e => setMinOrder(e.target.value)} style={{ padding: '6px 10px', width: '120px' }} />
          </div>
          <button type="submit" style={{ padding: '6px 16px', cursor: 'pointer' }}>Create</button>
        </form>

        {promoCodes.length === 0 ? (
          <p style={{ color: '#888' }}>No promo codes yet.</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #444', textAlign: 'left' }}>
                <th style={{ padding: '8px' }}>Code</th>
                <th style={{ padding: '8px' }}>Discount</th>
                <th style={{ padding: '8px' }}>Used</th>
                <th style={{ padding: '8px' }}>Expires</th>
                <th style={{ padding: '8px' }}>Min Order</th>
                <th style={{ padding: '8px' }}>Status</th>
                <th style={{ padding: '8px' }}></th>
              </tr>
            </thead>
            <tbody>
              {promoCodes.map(p => (
                <tr key={p.id} style={{ borderBottom: '1px solid #2a2a2a', opacity: p.active ? 1 : 0.5 }}>
                  <td style={{ padding: '8px', fontWeight: 'bold' }}>{p.code}</td>
                  <td style={{ padding: '8px' }}>{p.discount_type === 'percentage' ? `${p.discount_value}%` : `$${p.discount_value}`}</td>
                  <td style={{ padding: '8px' }}>{p.usage_count}{p.max_uses ? `/${p.max_uses}` : ''}</td>
                  <td style={{ padding: '8px', fontSize: '12px' }}>{p.expiry_date ? p.expiry_date.split('T')[0] : '-'}</td>
                  <td style={{ padding: '8px' }}>{p.min_order_amount ? `$${p.min_order_amount}` : '-'}</td>
                  <td style={{ padding: '8px' }}>{p.active ? <StatusBadge status="completed" /> : <StatusBadge status="cancelled" />}</td>
                  <td style={{ padding: '8px' }}>
                    {p.active && <button onClick={() => handleDeactivate(p.code)} style={{ padding: '4px 10px', cursor: 'pointer', fontSize: '12px' }}>Deactivate</button>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {/* Orders Section */}
      <section style={{ marginBottom: '48px' }}>
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
                  <td style={{ padding: '8px' }}><StatusBadge status={order.status} /></td>
                  <td style={{ padding: '8px', fontSize: '12px' }}>{new Date(order.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {/* Deliveries Section */}
      <section style={{ marginBottom: '48px' }}>
        <h2 style={{ marginBottom: '16px' }}>Deliveries</h2>

        {unassigned.length > 0 && (
          <>
            <h3 style={{ color: '#ffb74d', marginBottom: '12px' }}>Unassigned ({unassigned.length})</h3>
            {unassigned.map(d => (
              <div key={d.id} style={{ border: '1px solid #444', borderRadius: '8px', padding: '16px', marginBottom: '12px' }}>
                <p style={{ margin: '0 0 4px' }}><strong>Order:</strong> {d.order_id}</p>
                <p style={{ margin: '0 0 4px' }}><strong>Pickup:</strong> {d.pickup_address || 'N/A'}</p>
                <p style={{ margin: '0 0 12px' }}><strong>Dropoff:</strong> {d.dropoff_address || 'N/A'}</p>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <select
                    value={selectedDriver[d.id] || ''}
                    onChange={e => setSelectedDriver(prev => ({ ...prev, [d.id]: e.target.value }))}
                    style={{ padding: '6px 10px', cursor: 'pointer', flex: 1 }}
                  >
                    <option value=''>-- Select a driver --</option>
                    {availableDrivers.map(driver => (
                      <option key={driver.user_id} value={driver.user_id}>{driver.name}</option>
                    ))}
                  </select>
                  <button
                    onClick={() => handleAssign(d.id)}
                    disabled={!selectedDriver[d.id]}
                    style={{ padding: '6px 16px', cursor: selectedDriver[d.id] ? 'pointer' : 'not-allowed', opacity: selectedDriver[d.id] ? 1 : 0.5 }}
                  >
                    Assign
                  </button>
                </div>
                {availableDrivers.length === 0 && (
                  <p style={{ color: '#888', fontSize: '13px', marginTop: '8px' }}>No available drivers.</p>
                )}
              </div>
            ))}
          </>
        )}

        {active.length > 0 && (
          <>
            <h3 style={{ color: '#64b5f6', marginBottom: '12px', marginTop: '24px' }}>Active ({active.length})</h3>
            {active.map(d => (
              <div key={d.id} style={{ border: '1px solid #2a2a2a', borderRadius: '8px', padding: '16px', marginBottom: '12px' }}>
                <p style={{ margin: '0 0 4px' }}><strong>Order:</strong> {d.order_id}</p>
                <p style={{ margin: '0 0 4px' }}><strong>Driver:</strong> {d.driver?.name || 'N/A'}</p>
                <p style={{ margin: 0 }}><strong>Status:</strong> <StatusBadge status={d.status} /></p>
              </div>
            ))}
          </>
        )}

        {unassigned.length === 0 && active.length === 0 && (
          <p style={{ color: '#888' }}>No active deliveries.</p>
        )}
      </section>

      {/* Reports Section */}
      {report && (
        <section style={{ marginBottom: '48px' }}>
          <h2 style={{ marginBottom: '16px' }}>Reports</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
            <div style={{ border: '1px solid #444', borderRadius: '8px', padding: '16px' }}>
              <p style={{ color: '#888', margin: '0 0 4px', fontSize: '13px' }}>Total Revenue</p>
              <p style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>${report.total_revenue.toFixed(2)}</p>
            </div>
            <div style={{ border: '1px solid #444', borderRadius: '8px', padding: '16px' }}>
              <p style={{ color: '#888', margin: '0 0 4px', fontSize: '13px' }}>Avg Delivery Time</p>
              <p style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>
                {report.average_delivery_time != null ? `${report.average_delivery_time} min` : 'N/A'}
              </p>
            </div>
          </div>

          {report.revenue_per_restaurant.length > 0 && (
            <>
              <h3 style={{ marginBottom: '12px' }}>Revenue by Restaurant</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #444', textAlign: 'left' }}>
                    <th style={{ padding: '8px' }}>Restaurant ID</th>
                    <th style={{ padding: '8px' }}>Orders</th>
                    <th style={{ padding: '8px' }}>Revenue</th>
                  </tr>
                </thead>
                <tbody>
                  {report.revenue_per_restaurant.map(r => (
                    <tr key={r.restaurant_id} style={{ borderBottom: '1px solid #2a2a2a' }}>
                      <td style={{ padding: '8px' }}>{r.restaurant_id}</td>
                      <td style={{ padding: '8px' }}>{r.order_count}</td>
                      <td style={{ padding: '8px' }}>${r.total_revenue.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </section>
      )}

      {/* Reviews Section */}
      <section style={{ marginBottom: '48px' }}>
        <h2 style={{ marginBottom: '16px' }}>Reviews</h2>
        {reviews.length === 0 ? (
          <p style={{ color: '#888' }}>No reviews yet.</p>
        ) : (
          reviews.map(review => (
            <div key={review.id} style={{ border: '1px solid #2a2a2a', borderRadius: '8px', padding: '16px', marginBottom: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span><strong>{review.restaurant_name || `Restaurant ${review.restaurant_id}`}</strong></span>
                <span style={{ color: '#ffb74d' }}>{'★'.repeat(review.rating)}{'☆'.repeat(5 - review.rating)}</span>
              </div>
              {review.comment && <p style={{ color: '#ccc', margin: '0 0 6px', fontSize: '14px' }}>{review.comment}</p>}
              <p style={{ color: '#666', fontSize: '12px', margin: 0 }}>Order: {review.order_id}</p>
            </div>
          ))
        )}
      </section>
    </div>
  );
};

export default AdminDashboard;
