import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCustomerSearch } from '../hooks/useCustomerSearch';
import api from '../api';
// NEW: Import the cart utilities from the contributor's PR
import { addToCart, getCart } from '../utils/cartUtils';

const CustomerDashboard = () => {
  const { balance, user } = useAuth();
  const navigate = useNavigate();
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cartCount, setCartCount] = useState(0); // Track cart size for UI feedback
  const { state, setSearchTerm, setCuisine, setMaxPrice, setSearchType, setPage, actions } = useCustomerSearch();

  // Update cart count on mount and whenever items are added
  useEffect(() => {
    const updateCartCount = () => {
      const cart = getCart();
      setCartCount(cart.reduce((sum, item) => sum + item.quantity, 0));
    };
    updateCartCount();
    
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

  const handleAddToCart = (item) => {
    // Note: This assumes your search API provides 'restaurant_id' and 'price'
    const cartItem = {
      food_item: item.name,
      restaurant_id: item.restaurant_id || "unknown_res", 
      unit_price: item.price || 0,
      description: item.description || ""
    };
    
    addToCart(cartItem);
    // Refresh count
    const cart = getCart();
    setCartCount(cart.reduce((sum, i) => sum + i.quantity, 0));
  };

  return (
    <div style={containerStyle}>
      {/* HEADER */}
      <header style={headerStyle}>
        <div>
          <h1 style={{ margin: 10 }}>Hello, {user?.name || 'Customer'}</h1>
          <p style={{ color: '#aaa' }}>Track your food and manage your account.</p>
        </div>
        <div style={{ textAlign: 'right', display: 'flex', gap: '15px', alignItems: 'flex-start' }}>
          <div style={balanceCard}>
            <span style={{ fontSize: '0.75rem', color: '#888', fontWeight: 'bold' }}>WALLET BALANCE</span>
            <h2 style={{ margin: '5px 0', color: '#4caf50' }}>${balance.toFixed(2)}</h2>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button onClick={() => navigate('/cart')} style={cartBtnStyle}>
              🛒 View Cart ({cartCount})
            </button>
            <button onClick={() => navigate('/my-orders')} style={orderBtnStyle}>
              My Orders →
            </button>
          </div>
        </div>
      </header>

      {/* SEARCH SECTION */}
      <section style={{ marginBottom: '40px' }}>
        <h3 style={{ borderBottom: '1px solid #333', paddingBottom: '10px' }}>Find Food</h3>
        <form onSubmit={actions.executeNewSearch} style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}>
          <div style={{ display: 'flex', gap: '10px' }}>
            <select
              value={state.searchType}
              onChange={(e) => { setSearchType(e.target.value); setPage(1); }}
              style={{ padding: '8px' }}
            >
              <option value="restaurants">Search Restaurants</option>
              <option value="items">Search Dishes</option>
            </select>
            <input
              placeholder={state.searchType === 'restaurants' ? "Restaurant Name..." : "Dish Name..."}
              value={state.searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ flex: 1, padding: '8px' }}
            />
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            {state.searchType === 'restaurants' ? (
              <input
                placeholder="Cuisine (e.g. Italian, Burgers)"
                value={state.cuisine}
                onChange={(e) => setCuisine(e.target.value)}
                style={{ flex: 1, padding: '8px' }}
              />
            ) : (
              <input
                type="number"
                placeholder="Max Price ($)"
                value={state.maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
                style={{ flex: 1, padding: '8px' }}
              />
            )}
            <button type="submit" style={{ padding: '8px 20px', background: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}>
              Search
            </button>
          </div>
        </form>

        <div style={{ minHeight: '200px' }}>
          {state.loading ? (
            <p>Loading...</p>
          ) : state.results?.length > 0 ? (
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
                        <span key={tag} style={{ background: '#333', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem' }}>{tag}</span>
                      ))}
                    </div>
                  ) : (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                      <span style={{ color: '#44aa44', fontWeight: 'bold' }}>
                        {typeof item.price === 'number' ? `$${item.price.toFixed(2)}` : 'N/A'}
                      </span>
                      {/* NEW: Add to Cart button for dishes */}
                      <button 
                        onClick={() => handleAddToCart(item)}
                        style={addCartBtnStyle}
                      >
                        + Add to Cart
                      </button>
                    </div>
                  )}
                  {item.max_prep_time_minutes && (
                    <span style={{ fontSize: '0.8rem', color: '#888' }}>🕒 {item.max_prep_time_minutes} min prep</span>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div style={{ textAlign: 'center', marginTop: '30px', color: '#888' }}>
              <h3>No results found</h3>
            </div>
          )}
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '20px', marginTop: '20px' }}>
          <button disabled={state.page === 1 || state.loading} onClick={() => setPage(prev => prev - 1)}>← Previous</button>
          <span>Page {state.page}</span>
          <button disabled={!state.hasMore || state.loading} onClick={() => setPage(prev => prev + 1)}>Next →</button>
        </div>
      </section>

      {/* ACTIVE DELIVERIES SECTION */}
      <section>
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
    </div>
  );
};

// --- STYLES ---
const cartBtnStyle = { backgroundColor: '#007bff', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', fontSize: '0.9rem' };
const addCartBtnStyle = { backgroundColor: '#28a745', color: 'white', border: 'none', padding: '5px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '0.85rem' };
const orderBtnStyle = { backgroundColor: '#1e1e1e', color: '#007bff', border: '1px solid #333', padding: '10px 20px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', fontSize: '0.9rem' };
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