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

  // Search hook connection
  const { state, setSearchTerm, setCuisine, setMaxPrice, setSearchType, setPage, actions } = useCustomerSearch();

  // State for expanding restaurant menus
  const [selectedRestaurantId, setSelectedRestaurantId] = useState(null);
  const [restaurantMenus, setRestaurantMenus] = useState([]);
  const [menuItems, setMenuItems] = useState({}); // Stores { menuId: [items] }
  const [expanding, setExpanding] = useState(false);

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

  // Logic to fetch menus and items when a restaurant is clicked
  const handleRestaurantClick = async (restaurant) => {
    if (selectedRestaurantId === restaurant.id) {
      setSelectedRestaurantId(null); // Toggle close
      return;
    }

    setExpanding(true);
    try {
      const menuRes = await api.get(`/restaurants/${restaurant.id}/menus`);
      const menus = menuRes.data;
      setRestaurantMenus(menus);
      setSelectedRestaurantId(restaurant.id);

      // Fetch items for each menu in parallel
      const itemsMap = {};
      await Promise.all(
        menus.map(async (menu) => {
          const itemRes = await api.get(`/menus/${menu.id}/items`);
          itemsMap[menu.id] = itemRes.data;
        })
      );
      setMenuItems(itemsMap);
    } catch (err) {
      console.error("Error loading restaurant menus:", err);
    } finally {
      setExpanding(false);
    }
  };

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

      {/* SEARCH SECTION */}
      <section style={{ marginBottom: '40px' }}>
        <h3 style={{ borderBottom: '1px solid #333', paddingBottom: '10px' }}>Find Food</h3>
        <form onSubmit={actions.executeNewSearch} style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}>
          <div style={{ display: 'flex', gap: '10px' }}>
            <select
              value={state.searchType}
              onChange={(e) => { setSearchType(e.target.value); setPage(1); }}
              style={{ padding: '8px', borderRadius: '4px', background: '#222', color: 'white' }}
            >
              <option value="restaurants">Search Restaurants</option>
              <option value="items">Search Dishes</option>
            </select>
            <input
              placeholder={state.searchType === 'restaurants' ? "Restaurant Name..." : "Dish Name..."}
              value={state.searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid #444', background: '#111', color: 'white' }}
            />
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            {state.searchType === 'restaurants' ? (
              <input
                placeholder="Cuisine (e.g. Italian, Burgers)"
                value={state.cuisine}
                onChange={(e) => setCuisine(e.target.value)}
                style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid #444', background: '#111', color: 'white' }}
              />
            ) : (
              <input
                type="number"
                placeholder="Max Price ($)"
                value={state.maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
                style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid #444', background: '#111', color: 'white' }}
              />
            )}
            <button type="submit" style={{ padding: '8px 20px', background: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
              Search
            </button>
          </div>
        </form>

        {/* SEARCH RESULTS */}
        <div style={{ minHeight: '200px' }}>
          {state.loading ? (
            <p>Searching...</p>
          ) : state.results?.length > 0 ? (
            state.results.map(item => (
              <div 
                key={item.id} 
                onClick={() => state.searchType === 'restaurants' && handleRestaurantClick(item)}
                style={{ 
                  ...resultCardStyle, 
                  cursor: state.searchType === 'restaurants' ? 'pointer' : 'default',
                  border: selectedRestaurantId === item.id ? '1px solid #007bff' : '1px solid #444'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong style={{ fontSize: '1.2rem' }}>{item.name}</strong>
                  <span style={{ color: '#ffc107' }}>⭐ {item.rating ?? 'N/A'}</span>
                </div>
                <p style={{ margin: '5px 0', color: '#bbb' }}>
                  {state.searchType === 'restaurants' ? item.address : item.description}
                </p>
                
                {/* EXPANDED MENU SECTION */}
                {selectedRestaurantId === item.id && (
                  <div style={expandedMenuSection} onClick={(e) => e.stopPropagation()}>
                    <h4 style={{ color: '#007bff', marginTop: 0 }}>Menus</h4>
                    {expanding ? <p>Loading menus...</p> : (
                      restaurantMenus.map(menu => (
                        <div key={menu.id} style={{ marginBottom: '15px' }}>
                          <h5 style={{ margin: '5px 0', color: '#eee', textDecoration: 'underline' }}>{menu.name}</h5>
                          {menuItems[menu.id]?.map(dish => (
                            <div key={dish.id} style={dishRowStyle}>
                              <span>{dish.name}</span>
                              <span style={{ color: '#44aa44' }}>${dish.price.toFixed(2)}</span>
                            </div>
                          ))}
                        </div>
                      ))
                    )}
                  </div>
                )}

                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', alignItems: 'center' }}>
                  {state.searchType === 'restaurants' ? (
                    <div style={{ display: 'flex', gap: '5px' }}>
                      {item.tags?.map(tag => (
                        <span key={tag} style={tagStyle}>{tag}</span>
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
            <div style={{ textAlign: 'center', marginTop: '30px', color: '#888' }}>
              <h3>No results found</h3>
            </div>
          )}
        </div>

        {/* PAGINATION */}
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

// Styles
const resultCardStyle = { padding: '15px', marginBottom: '10px', borderRadius: '8px', background: '#1e1e1e', transition: 'all 0.2s' };
const expandedMenuSection = { marginTop: '15px', padding: '15px', background: '#111', borderRadius: '6px' };
const dishRowStyle = { display: 'flex', justifyContent: 'space-between', padding: '5px 0', borderBottom: '1px solid #222', fontSize: '0.9rem' };
const tagStyle = { background: '#333', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem' };
const orderBtnStyle = { marginTop: '12px', backgroundColor: '#1e1e1e', color: '#007bff', border: '1px solid #333', padding: '10px 20px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', fontSize: '0.9rem' };
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