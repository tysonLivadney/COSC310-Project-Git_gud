import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api';

const AdminDashboard = () => {
  const { user } = useAuth();
  const [promoCodes, setPromoCodes] = useState([]);
  const [orders, setOrders] = useState([]);
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');
  const [orderFilter, setOrderFilter] = useState('all');

  const [code, setCode] = useState('');
  const [discountType, setDiscountType] = useState('percentage');
  const [discountValue, setDiscountValue] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [maxUses, setMaxUses] = useState('');
  const [minOrder, setMinOrder] = useState('');

  const loadData = async () => {
    try {
      const [promoRes, orderRes, reportRes] = await Promise.all([
        api.get('/promo-codes'),
        api.get('/admin/orders'),
        api.get('/admin/reports'),
      ]);
      setPromoCodes(promoRes.data);
      setOrders(orderRes.data);
      setReport(reportRes.data);
    } catch (err) {
      console.error('failed to load dashboard', err);
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleCreatePromo = async (e) => {
    e.preventDefault();
    setError('');
    const payload = {
      code: code,
      discount_type: discountType,
      discount_value: parseFloat(discountValue),
    };
    if (expiryDate) payload.expiry_date = expiryDate + 'T23:59:59';
    if (maxUses) payload.max_uses = parseInt(maxUses);
    if (minOrder) payload.min_order_amount = parseFloat(minOrder);

    try {
      await api.post('/promo-codes', payload);
      setCode(''); setDiscountValue(''); setExpiryDate(''); setMaxUses(''); setMinOrder('');
      loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create promo code');
    }
  };

  const handleDeactivate = async (promoCode) => {
    try {
      await api.delete(`/promo-codes/${promoCode}`);
      loadData();
    } catch (err) {
      setError('Failed to deactivate code');
    }
  };

  const filteredOrders = orderFilter === 'all' ? orders : orders.filter(o => o.status === orderFilter);

  return (
    <div style={{ padding: '30px', color: 'white', backgroundColor: '#121212', minHeight: '100vh', fontFamily: 'sans-serif' }}>
      <h1 style={{ margin: '0 0 5px 0' }}>Admin Dashboard</h1>
      <p style={{ color: '#aaa', marginTop: 0 }}>Welcome, {user?.name || 'Admin'}</p>

      {error && <div style={{ color: 'white', background: '#d9534f', padding: '10px', marginBottom: '15px', borderRadius: '8px' }}>{error}</div>}

      {/* report numbers */}
      {report && (
        <div style={{ display: 'flex', gap: '15px', marginBottom: '30px' }}>
          <div style={cardStyle}><span style={{ color: '#888', fontSize: '0.8rem' }}>Total Revenue</span><h2 style={{ margin: '5px 0', color: '#4caf50' }}>${report.total_revenue.toFixed(2)}</h2></div>
          <div style={cardStyle}><span style={{ color: '#888', fontSize: '0.8rem' }}>Avg Delivery</span><h2 style={{ margin: '5px 0' }}>{report.average_delivery_time ? `${report.average_delivery_time} min` : 'N/A'}</h2></div>
          <div style={cardStyle}><span style={{ color: '#888', fontSize: '0.8rem' }}>Orders</span><h2 style={{ margin: '5px 0' }}>{orders.length}</h2></div>
        </div>
      )}

      {/* create promo code */}
      <h3 style={{ borderBottom: '1px solid #333', paddingBottom: '10px' }}>Create Promo Code</h3>
      <form onSubmit={handleCreatePromo} style={{ marginBottom: '30px' }}>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
          <input placeholder="Code (e.g. SAVE20)" value={code} onChange={e => setCode(e.target.value)} required style={inputStyle} />
          <select value={discountType} onChange={e => setDiscountType(e.target.value)} style={inputStyle}>
            <option value="percentage">Percentage (%)</option>
            <option value="flat">Flat ($)</option>
          </select>
          <input type="number" step="0.01" placeholder={discountType === 'percentage' ? '% off' : '$ off'} value={discountValue} onChange={e => setDiscountValue(e.target.value)} required style={inputStyle} />
        </div>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
          <input type="date" value={expiryDate} onChange={e => setExpiryDate(e.target.value)} style={inputStyle} />
          <input type="number" placeholder="Max uses" value={maxUses} onChange={e => setMaxUses(e.target.value)} style={inputStyle} />
          <input type="number" step="0.01" placeholder="Min order $" value={minOrder} onChange={e => setMinOrder(e.target.value)} style={inputStyle} />
        </div>
        <button type="submit" style={{ padding: '8px 20px', background: '#007bff', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>Create</button>
      </form>

      {/* promo codes list */}
      <h3 style={{ borderBottom: '1px solid #333', paddingBottom: '10px' }}>Promo Codes</h3>
      {promoCodes.length === 0 ? (
        <p style={{ color: '#555' }}>No promo codes yet</p>
      ) : (
        promoCodes.map(promo => (
          <div key={promo.id} style={{ ...cardStyle, marginBottom: '10px', opacity: promo.active ? 1 : 0.5 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <strong>{promo.code}</strong>
                <span style={{ color: '#aaa', marginLeft: '10px', fontSize: '0.85rem' }}>
                  {promo.discount_type === 'percentage' ? `${promo.discount_value}% off` : `$${promo.discount_value} off`}
                </span>
                <span style={{ color: '#666', marginLeft: '10px', fontSize: '0.8rem' }}>
                  used {promo.usage_count}{promo.max_uses ? `/${promo.max_uses}` : ''} times
                </span>
              </div>
              <div>
                {promo.active ? (
                  <button onClick={() => handleDeactivate(promo.code)} style={{ padding: '4px 10px', background: 'transparent', color: '#f44336', border: '1px solid #f44336', borderRadius: '6px', cursor: 'pointer', fontSize: '0.8rem' }}>
                    Deactivate
                  </button>
                ) : (
                  <span style={{ color: '#f44336', fontSize: '0.8rem' }}>Inactive</span>
                )}
              </div>
            </div>
            {(promo.expiry_date || promo.min_order_amount) && (
              <div style={{ color: '#555', fontSize: '0.8rem', marginTop: '5px' }}>
                {promo.expiry_date && `expires ${promo.expiry_date.split('T')[0]}`}
                {promo.expiry_date && promo.min_order_amount && ' · '}
                {promo.min_order_amount && `min order $${promo.min_order_amount}`}
              </div>
            )}
          </div>
        ))
      )}

      {/* orders */}
      <h3 style={{ borderBottom: '1px solid #333', paddingBottom: '10px', marginTop: '30px' }}>Orders</h3>
      <div style={{ marginBottom: '15px', display: 'flex', gap: '8px' }}>
        {['all', 'draft', 'confirmed', 'completed', 'cancelled', 'refunded'].map(f => (
          <button key={f} onClick={() => setOrderFilter(f)} style={{
            padding: '5px 12px', background: orderFilter === f ? '#333' : 'transparent',
            color: orderFilter === f ? 'white' : '#888', border: '1px solid #333', borderRadius: '6px', cursor: 'pointer', fontSize: '0.8rem',
          }}>
            {f}
          </button>
        ))}
      </div>
      {filteredOrders.length === 0 ? (
        <p style={{ color: '#555' }}>No orders</p>
      ) : (
        filteredOrders.map(order => (
          <div key={order.id} style={{ ...cardStyle, marginBottom: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span><strong>{order.id.slice(0, 8)}</strong> · {order.items.length} items · customer {order.customer_id}</span>
              <span style={{ color: order.status === 'confirmed' ? '#2196f3' : order.status === 'cancelled' ? '#f44336' : '#888' }}>{order.status}</span>
            </div>
            {order.promo_code && <div style={{ color: '#888', fontSize: '0.8rem', marginTop: '4px' }}>promo: {order.promo_code} (-${order.discount})</div>}
          </div>
        ))
      )}

      {/* revenue by restaurant */}
      {report && report.revenue_per_restaurant.length > 0 && (
        <>
          <h3 style={{ borderBottom: '1px solid #333', paddingBottom: '10px', marginTop: '30px' }}>Revenue by Restaurant</h3>
          {report.revenue_per_restaurant.map((r, i) => (
            <div key={i} style={{ ...cardStyle, marginBottom: '8px', display: 'flex', justifyContent: 'space-between' }}>
              <span>Restaurant {r.restaurant_id} ({r.order_count} orders)</span>
              <span style={{ color: '#4caf50' }}>${r.total_revenue.toFixed(2)}</span>
            </div>
          ))}
        </>
      )}
    </div>
  );
};

const cardStyle = { backgroundColor: '#1e1e1e', padding: '15px', borderRadius: '10px', border: '1px solid #333' };
const inputStyle = { padding: '8px', backgroundColor: '#1e1e1e', color: 'white', border: '1px solid #333', borderRadius: '8px', flex: 1 };

export default AdminDashboard;
