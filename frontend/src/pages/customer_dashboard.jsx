import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCustomerSearch } from '../hooks/useCustomerSearch';
import api from '../api';

const CustomerDashboard = () => {
  const { balance, user } = useAuth();
  const navigate = useNavigate();
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [notification, setNotification] = useState(null);

  // REFS - Logic for persistence and preventing crashes
  const seenNotifications = useRef(new Set());
  const isInitialLoad = useRef(true);
  const notificationTimer = useRef(null);

  const { state, setSearchTerm, setCuisine, setMaxPrice, setSearchType, setPage, actions } = useCustomerSearch();

  // Helper to trigger the popup UI
  const triggerPopup = (message) => {
    if (notificationTimer.current) clearTimeout(notificationTimer.current);
    setNotification(message);
    notificationTimer.current = setTimeout(() => {
      setNotification(null);
    }, 5000);
  };

  // --- STEP 1: LOAD DELIVERIES (UI RENDERING) ---
  useEffect(() => {
    const loadUI = async () => {
      try {
        const ordersRes = await api.get('/orders/');
        const userOrderIds = ordersRes.data
          .filter(o => o.customer_id === user?.id)
          .map(o => o.id);

        const deliveriesRes = await api.get('/deliveries/');
        const active = deliveriesRes.data.filter(d => userOrderIds.includes(d.order_id));
        
        setDeliveries(active);
      } catch (err) {
        console.error("UI Load failed", err);
      } finally {
        setLoading(false);
      }
    };

    if (user?.id) loadUI();
  }, [user?.id]);

  // --- STEP 2: NOTIFICATION WATCHER (EVENT POLLING) ---
  useEffect(() => {
    if (!user?.id) return;

    const checkNotifications = async () => {
      try {
        // 1. Get ONLY this user's delivery IDs to keep polling private and efficient
        const ordersRes = await api.get('/orders/');
        const userOrderIds = ordersRes.data
          .filter(o => o.customer_id === user?.id)
          .map(o => o.id);

        const deliveriesRes = await api.get('/deliveries/');
        const idsToCheck = deliveriesRes.data
          .filter(d => userOrderIds.includes(d.order_id))
          .map(d => d.id);

        // 2. Poll each delivery for new messages
        for (const id of idsToCheck) {
          const res = await api.get(`/notifications/${id}`);
          if (!Array.isArray(res.data)) continue;

          const unread = res.data.filter(n => {
            const isNotSeenLocally = !seenNotifications.current.has(n.id);
            const isNotReadOnServer = n.read === false; // Matches your Pydantic schema
            
            // On refresh, ignore notifications older than 1 minute
            if (isInitialLoad.current && n.created_at) {
              const createdAt = new Date(n.created_at).getTime();
              const oneMinuteAgo = Date.now() - 60000;
              if (isNaN(createdAt) || createdAt < oneMinuteAgo) return false;
            }

            return isNotReadOnServer && isNotSeenLocally;
          });

          if (unread.length > 0) {
            const latest = unread[0];
            
            // Mark seen locally immediately
            seenNotifications.current.add(latest.id);
            
            // Mark read on backend
            await api.patch(`/notifications/${id}/${latest.id}/read`);
            
            // Trigger UI
            triggerPopup(latest.message);
            break; 
          }
        }
        // First pass complete
        isInitialLoad.current = false;
      } catch (e) {
        console.error("Notification Poller Error:", e);
      }
    };

    const pollID = setInterval(checkNotifications, 5000); 
    return () => clearInterval(pollID);
  }, [user?.id]);

  return (
    <div style={containerStyle}>
      {/* HEADER */}
      <header style={headerStyle}>
        <div>
          <h1 style={{ margin: 10 }}>Hello, {user?.name || 'Customer'}</h1>
          <p style={{ color: '#aaa' }}>Track your food and manage your account.</p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={balanceCard}>
            <span style={{ fontSize: '0.75rem', color: '#888', fontWeight: 'bold' }}>WALLET BALANCE</span>
            <h2 style={{ margin: '5px 0', color: '#4caf50' }}>${balance?.toFixed(2) || '0.00'}</h2>
          </div>
          <button onClick={() => navigate('/my-orders')} style={orderBtnStyle}>
            View My Orders →
          </button>
        </div>
      </header>

      {/* ACTIVE DELIVERIES SECTION */}
      <section style={{ marginBottom: '40px' }}>
        <h3 style={{ borderBottom: '1px solid #333', paddingBottom: '10px' }}>Active Deliveries</h3>
        {loading ? (
          <p>Loading your orders...</p>
        ) : deliveries.length > 0 ? (
          <div style={gridStyle}>
            {deliveries.map((delivery) => (
              <div key={delivery.id} style={cardStyle} onClick={() => navigate(`/delivery/${delivery.id}`)}>
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

      {/* SEARCH SECTION */}
      <section>
        <h3 style={{ borderBottom: '1px solid #333', paddingBottom: '10px' }}>Search Food</h3>
        <form onSubmit={actions.executeNewSearch} style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}>
          <div style={{ display: 'flex', gap: '10px' }}>
            <select 
              value={state.searchType} 
              onChange={(e) => { setSearchType(e.target.value); setPage(1); }}
              style={inputStyle}
            >
              <option value="restaurants">Search Restaurants</option>
              <option value="items">Search Dishes</option>
            </select>
            <input 
              placeholder={state.searchType === 'restaurants' ? "Restaurant Name..." : "Dish Name..."}
              value={state.searchTerm} 
              onChange={(e) => setSearchTerm(e.target.value)} 
              style={{ ...inputStyle, flex: 1 }}
            />
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            {state.searchType === 'restaurants' ? (
              <input 
                placeholder="Cuisine (e.g. Italian, Burgers)" 
                value={state.cuisine} 
                onChange={(e) => setCuisine(e.target.value)}
                style={{ ...inputStyle, flex: 1 }}
              />
            ) : (
              <input 
                type="number"
                placeholder="Max Price ($)" 
                value={state.maxPrice} 
                onChange={(e) => setMaxPrice(e.target.value)}
                style={{ ...inputStyle, flex: 1 }}
              />
            )}
            <button type="submit" style={searchBtnStyle}>Search</button>
          </div>
        </form>

        <div className="results-container" style={{ minHeight: '400px' }}>
          {state.loading ? (
            <p>Loading...</p>
          ) : state.results?.length > 0 ? (
            state.results.map(item => (
              <div key={item.id} style={resultCardStyle}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong style={{ fontSize: '1.2rem' }}>{item.name}</strong>
                  <span style={{ color: '#ffc107' }}>⭐ {item.rating ?? 'N/A'}</span>
                </div>
                <p style={{ margin: '5px 0', color: '#bbb' }}>
                  {state.searchType === 'restaurants' ? item.address : item.description}
                </p>
              </div>
            ))
          ) : (
            <div style={emptyState}><h3>No results found</h3></div>
          )}
        </div>
      </section>

      {/* POPUP NOTIFICATION */}
      {notification && (
        <div style={popupContainerStyle}>
          <div style={popupStyle}>
            <div style={{ fontSize: '1.5rem' }}>🚚</div>
            <div style={{ flex: 1 }}>
              <strong style={{ display: 'block', fontSize: '0.8rem', color: '#007bff' }}>UPDATE</strong>
              <p style={{ margin: 0, fontSize: '0.95rem' }}>{notification}</p>
            </div>
            <button onClick={() => setNotification(null)} style={closeBtnStyle}>✕</button>
          </div>
        </div>
      )}
    </div>
  );
};

// --- STYLES ---
const containerStyle = { padding: '30px', color: 'white', backgroundColor: '#121212', minHeight: '100vh', fontFamily: 'sans-serif' };
const headerStyle = { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '40px' };
const balanceCard = { backgroundColor: '#1e1e1e', padding: '15px 25px', borderRadius: '12px', border: '1px solid #333' };
const orderBtnStyle = { marginTop: '12px', backgroundColor: '#1e1e1e', color: '#007bff', border: '1px solid #333', padding: '10px 20px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' };
const gridStyle = { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' };
const cardStyle = { backgroundColor: '#1e1e1e', padding: '20px', borderRadius: '12px', border: '1px solid #333', cursor: 'pointer' };
const cardHeader = { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' };
const addressText = { margin: '4px 0', fontSize: '0.9rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' };
const cardFooter = { marginTop: '15px', color: '#007bff', fontSize: '0.85rem', fontWeight: 'bold' };
const emptyState = { padding: '40px', textAlign: 'center', color: '#555', backgroundColor: '#1a1a1a', borderRadius: '12px' };
const inputStyle = { padding: '8px', backgroundColor: '#1e1e1e', color: 'white', border: '1px solid #333', borderRadius: '8px' };
const searchBtnStyle = { padding: '8px 20px', background: '#007bff', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' };
const resultCardStyle = { border: '1px solid #444', padding: '15px', marginBottom: '10px', borderRadius: '8px', background: '#1e1e1e' };

const popupContainerStyle = { position: 'fixed', bottom: '20px', right: '20px', zIndex: 9999 };
const popupStyle = { backgroundColor: '#1e1e1e', color: 'white', padding: '15px 20px', borderRadius: '12px', border: '1px solid #007bff', boxShadow: '0 10px 30px rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', gap: '15px', minWidth: '280px' };
const closeBtnStyle = { background: 'none', border: 'none', color: '#666', cursor: 'pointer', fontSize: '1.2rem' };
const statusBadge = (s) => ({ backgroundColor: s === 'delivered' ? '#4caf50' : s === 'cancelled' ? '#f44336' : '#ff9800', color: 'white', padding: '4px 10px', borderRadius: '20px', fontSize: '0.7rem', fontWeight: 'bold' });

export default CustomerDashboard;