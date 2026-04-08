import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCustomerSearch } from '../hooks/useCustomerSearch';
import api from '../api';

const CustomerDashboard = () => {
  const { balance, user } = useAuth();
  const navigate = useNavigate();
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const { state, setSearchTerm, setCuisine, setMaxPrice, setSearchType, setPage, actions } = useCustomerSearch();

  useEffect(() => {
    const fetchDeliveries = async () => {
      try {
        const response = await api.get('/deliveries/');
        // Filter deliveries by current user's ID
        const userDeliveries = response.data.filter(
          delivery => delivery.customer_id === user?.id
        );
        setDeliveries(userDeliveries);
      } catch (err) {
        console.error("Failed to fetch deliveries", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDeliveries();
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
            <h2 style={{ margin: '5px 0', color: '#4caf50' }}>${balance.toFixed(2)}</h2>
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
              onChange={(e) => {
                setSearchType(e.target.value);
                setPage(1);
              }}
              style={{ padding: '8px', backgroundColor: '#1e1e1e', color: 'white', border: '1px solid #333', borderRadius: '8px' }}
            >
              <option value="restaurants">Search Restaurants</option>
              <option value="items">Search Dishes</option>
            </select>
            
            <input 
              placeholder={state.searchType === 'restaurants' ? "Restaurant Name..." : "Dish Name..."}
              value={state.searchTerm} 
              onChange={(e) => setSearchTerm(e.target.value)} 
              style={{ flex: 1, padding: '8px', backgroundColor: '#1e1e1e', color: 'white', border: '1px solid #333', borderRadius: '8px' }}
            />
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            {state.searchType === 'restaurants' ? (
              <input 
                placeholder="Cuisine (e.g. Italian, Burgers)" 
                value={state.cuisine} 
                onChange={(e) => setCuisine(e.target.value)}
                style={{ flex: 1, padding: '8px', backgroundColor: '#1e1e1e', color: 'white', border: '1px solid #333', borderRadius: '8px' }}
              />
            ) : (
              <input 
                type="number"
                placeholder="Max Price ($)" 
                value={state.maxPrice} 
                onChange={(e) => setMaxPrice(e.target.value)}
                style={{ flex: 1, padding: '8px', backgroundColor: '#1e1e1e', color: 'white', border: '1px solid #333', borderRadius: '8px' }}
              />
            )}
            <button type="submit" style={{ padding: '8px 20px', background: '#007bff', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>
              Search
            </button>
          </div>
        </form>

        <div className="results-container" style={{ minHeight: '400px' }}>
          {state.loading ? (
            <p>Loading...</p>
          ) : state.results && state.results.length > 0 ? (
            state.results.map(item => (
              <div key={item.id} style={{ border: '1px solid #444', padding: '15px', marginBottom: '10px', borderRadius: '8px', background: '#1e1e1e' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong style={{ fontSize: '1.2rem' }}>{item.name}</strong>
                  <span style={{ color: '#ffc107' }}>⭐ {item.rating ?? 'N/A'}</span>
                </div>
                
                <p style={{ margin: '5px 0', color: '#bbb' }}>
                  {state.searchType === 'restaurants' ? item.address : item.description}
                </p>

                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', alignItems: 'center' }}>
                  {state.searchType === 'restaurants' ? (
                    <div style={{ display: 'flex', gap: '5px' }}>
                      {item.tags?.map(tag => (
                        <span key={tag} style={{ background: '#333', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem' }}>
                          {tag}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <span style={{ color: '#44aa44', fontWeight: 'bold' }}>
                      {typeof item.price === 'number' ? `$${item.price.toFixed(2)}` : 'N/A'}
                    </span>
                  )}
                  
                  {item.max_prep_time_minutes && (
                    <span style={{ fontSize: '0.8rem', color: '#888' }}>🕒 {item.max_prep_time_minutes} min prep</span>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div style={{ textAlign: 'center', marginTop: '50px', color: '#888' }}>
              <h3>No results found</h3>
            </div>
          )}
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '20px', marginTop: '30px', paddingBottom: '40px' }}>
          <button 
            disabled={state.page === 1 || state.loading} 
            onClick={() => setPage(prev => prev - 1)}
            style={{ padding: '8px 16px', backgroundColor: '#1e1e1e', color: '#007bff', border: '1px solid #333', borderRadius: '8px', cursor: state.page === 1 || state.loading ? 'not-allowed' : 'pointer' }}
          >
            ← Previous
          </button>
          <span>Page {state.page}</span>
          <button 
            disabled={!state.hasMore || state.loading} 
            onClick={() => setPage(prev => prev + 1)}
            style={{ padding: '8px 16px', backgroundColor: '#1e1e1e', color: '#007bff', border: '1px solid #333', borderRadius: '8px', cursor: !state.hasMore || state.loading ? 'not-allowed' : 'pointer' }}
          >
            Next →
          </button>
        </div>
      </section>
    </div>
  );
};

// STYLES
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