import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCustomerSearch } from '../hooks/useCustomerSearch';
import api from '../api';
import { addToCart, getCart } from '../utils/cartUtils';

const CustomerDashboard = () => {
  const { balance, user } = useAuth();
  const navigate = useNavigate();

  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cartCount, setCartCount] = useState(0);
  const [notification, setNotification] = useState(null);

  const seenNotifications = useRef(new Set());
  const isInitialLoad = useRef(true);
  const notificationTimer = useRef(null);

  const { state, setSearchTerm, setCuisine, setMaxPrice, setSearchType, setPage, actions } =
    useCustomerSearch();

  const [selectedRestaurantId, setSelectedRestaurantId] = useState(null);
  const [restaurantMenus, setRestaurantMenus] = useState([]);
  const [menuItems, setMenuItems] = useState({});
  const [expanding, setExpanding] = useState(false);

  const updateCartCount = () => {
    const cart = getCart();
    setCartCount(cart.reduce((sum, item) => sum + (item.quantity || 0), 0));
  };

  const triggerPopup = (message) => {
    if (notificationTimer.current) clearTimeout(notificationTimer.current);
    setNotification(message);
    notificationTimer.current = setTimeout(() => {
      setNotification(null);
    }, 5000);
  };

  useEffect(() => {
    updateCartCount();
  }, []);

  useEffect(() => {
    const loadUI = async () => {
      try {
        const ordersRes = await api.get('/orders/');
        const userOrderIds = ordersRes.data
          .filter((o) => o.customer_id === user?.id)
          .map((o) => o.id);

        const deliveriesRes = await api.get('/deliveries/');
        const active = deliveriesRes.data.filter((d) => userOrderIds.includes(d.order_id));

        setDeliveries(active);
      } catch (err) {
        console.error('UI Load failed', err);
      } finally {
        setLoading(false);
      }
    };

    if (user?.id) {
      loadUI();
    } else {
      setLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    if (!user?.id) return;

    const checkNotifications = async () => {
      try {
        const ordersRes = await api.get('/orders/');
        const userOrderIds = ordersRes.data
          .filter((o) => o.customer_id === user?.id)
          .map((o) => o.id);

        const deliveriesRes = await api.get('/deliveries/');
        const activeDeliveries = deliveriesRes.data.filter((d) => userOrderIds.includes(d.order_id));
        setDeliveries(activeDeliveries);
        const idsToCheck = activeDeliveries.map((d) => d.id);

        for (const id of idsToCheck) {
          const res = await api.get(`/notifications/${id}`);
          if (!Array.isArray(res.data)) continue;

          const unread = res.data.filter((n) => {
            const isNotSeenLocally = !seenNotifications.current.has(n.id);
            const isNotReadOnServer = n.read === false;

            if (isInitialLoad.current && n.created_at) {
              const createdAt = new Date(n.created_at).getTime();
              const oneMinuteAgo = Date.now() - 60000;
              if (isNaN(createdAt) || createdAt < oneMinuteAgo) return false;
            }

            return isNotReadOnServer && isNotSeenLocally;
          });

          if (unread.length > 0) {
            const latest = unread[0];
            seenNotifications.current.add(latest.id);
            await api.patch(`/notifications/${id}/${latest.id}/read`);
            triggerPopup(latest.message);
            break;
          }
        }

        isInitialLoad.current = false;
      } catch (e) {
        console.error('Notification Poller Error:', e);
      }
    };

    const pollID = setInterval(checkNotifications, 5000);
    return () => {
      clearInterval(pollID);
      if (notificationTimer.current) clearTimeout(notificationTimer.current);
    };
  }, [user?.id]);

  const handleRestaurantClick = async (restaurant) => {
    if (selectedRestaurantId === restaurant.id) {
      setSelectedRestaurantId(null);
      return;
    }

    setExpanding(true);
    try {
      const menuRes = await api.get(`/restaurants/${restaurant.id}/menus`);
      const menus = menuRes.data;
      setRestaurantMenus(menus);
      setSelectedRestaurantId(restaurant.id);

      const itemsMap = {};
      await Promise.all(
        menus.map(async (menu) => {
          const itemRes = await api.get(`/menus/${menu.id}/items`);
          itemsMap[menu.id] = itemRes.data;
        })
      );
      setMenuItems(itemsMap);
    } catch (err) {
      console.error('Error loading restaurant menus:', err);
    } finally {
      setExpanding(false);
    }
  };

  const handleAddToCart = (item) => {
    const cartItem = {
      food_item: item.name,
      restaurant_id: item.restaurant_id || 'unknown_res',
      unit_price: item.price || 0,
      description: item.description || '',
      quantity: 1
    };

    addToCart(cartItem);
    updateCartCount();
  };

  return (
    <div style={containerStyle}>
      <header style={headerStyle}>
        <div>
          <h1 style={{ margin: 10 }}>Hello, {user?.name || 'Customer'}</h1>
          <p style={{ color: '#aaa' }}>Track your food and manage your account.</p>
        </div>
        <div
          style={{
            textAlign: 'right',
            display: 'flex',
            gap: '15px',
            alignItems: 'flex-start'
          }}
        >
          <div style={balanceCard}>
            <span style={{ fontSize: '0.75rem', color: '#888', fontWeight: 'bold' }}>
              WALLET BALANCE
            </span>
            <h2 style={{ margin: '5px 0', color: '#4caf50' }}>
              ${balance?.toFixed(2) || '0.00'}
            </h2>
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

      <section style={{ marginBottom: '40px' }}>
        <h3 style={{ borderBottom: '1px solid #333', paddingBottom: '10px' }}>
          Active Deliveries
        </h3>
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
                  <p style={addressText}>
                    📍 <strong>From:</strong> {delivery.pickup_address}
                  </p>
                  <p style={addressText}>
                    🏠 <strong>To:</strong> {delivery.dropoff_address}
                  </p>
                </div>
                <div style={cardFooter}>View Details & Manage →</div>
              </div>
            ))}
          </div>
        ) : (
          <div style={emptyState}>No active deliveries found.</div>
        )}
      </section>

      <section>
        <h3 style={{ borderBottom: '1px solid #333', paddingBottom: '10px' }}>Search Food</h3>
        <form
          onSubmit={actions.executeNewSearch}
          style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}
        >
          <div style={{ display: 'flex', gap: '10px' }}>
            <select
              value={state.searchType}
              onChange={(e) => {
                setSearchType(e.target.value);
                setPage(1);
              }}
              style={inputStyle}
            >
              <option value="restaurants">Search Restaurants</option>
              <option value="items">Search Dishes</option>
            </select>
            <input
              placeholder={state.searchType === 'restaurants' ? 'Restaurant Name...' : 'Dish Name...'}
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
            <button type="submit" style={searchBtnStyle}>
              Search
            </button>
          </div>
        </form>

        <div className="results-container" style={{ minHeight: '400px' }}>
          {state.loading ? (
            <p>Searching...</p>
          ) : state.results?.length > 0 ? (
            state.results.map((item) => (
              <div
                key={item.id}
                onClick={() => state.searchType === 'restaurants' && handleRestaurantClick(item)}
                style={{
                  ...resultCardStyle,
                  cursor: state.searchType === 'restaurants' ? 'pointer' : 'default',
                  border:
                    selectedRestaurantId === item.id ? '1px solid #007bff' : '1px solid #444'
                }}
              >
                <div
                  style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                >
                  <strong style={{ fontSize: '1.2rem' }}>{item.name}</strong>
                  <span style={{ color: '#ffc107' }}>⭐ {item.rating ?? 'N/A'}</span>
                </div>
                <p style={{ margin: '5px 0', color: '#bbb' }}>
                  {state.searchType === 'restaurants' ? item.address : item.description}
                </p>

                {selectedRestaurantId === item.id && (
                  <div style={expandedMenuSection} onClick={(e) => e.stopPropagation()}>
                    <h4 style={{ color: '#007bff', marginTop: 0 }}>Menus</h4>
                    {expanding ? (
                      <p>Loading menus...</p>
                    ) : (
                      restaurantMenus.map((menu) => (
                        <div key={menu.id} style={{ marginBottom: '15px' }}>
                          <h5
                            style={{
                              margin: '5px 0',
                              color: '#eee',
                              textDecoration: 'underline'
                            }}
                          >
                            {menu.name}
                          </h5>
                          {menuItems[menu.id]?.map((dish) => (
                            <div key={dish.id} style={dishRowStyle}>
                              <span>{dish.name}</span>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <span style={{ color: '#44aa44' }}>
                                  ${dish.price.toFixed(2)}
                                </span>
                                <button
                                  onClick={() => handleAddToCart({ ...dish, restaurant_id: selectedRestaurantId })}
                                  style={addCartBtnStyle}
                                >
                                  + Add to Cart
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      ))
                    )}
                  </div>
                )}

                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    marginTop: '10px',
                    alignItems: 'center'
                  }}
                >
                  {state.searchType === 'restaurants' ? (
                    <div style={{ display: 'flex', gap: '5px' }}>
                      {item.tags?.map((tag) => (
                        <span key={tag} style={tagStyle}>
                          {tag}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                      <span style={{ color: '#44aa44', fontWeight: 'bold' }}>
                        {typeof item.price === 'number' ? `$${item.price.toFixed(2)}` : 'N/A'}
                      </span>
                      <button onClick={() => handleAddToCart(item)} style={addCartBtnStyle}>
                        + Add to Cart
                      </button>
                    </div>
                  )}
                  {item.max_prep_time_minutes && (
                    <span style={{ fontSize: '0.8rem', color: '#888' }}>
                      🕒 {item.max_prep_time_minutes} min prep
                    </span>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div style={emptyState}>
              <h3>No results found</h3>
            </div>
          )}
        </div>

        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: '20px',
            marginTop: '20px'
          }}
        >
          <button
            disabled={state.page === 1 || state.loading}
            onClick={() => setPage((prev) => prev - 1)}
          >
            ← Previous
          </button>
          <span>Page {state.page}</span>
          <button
            disabled={!state.hasMore || state.loading}
            onClick={() => setPage((prev) => prev + 1)}
          >
            Next →
          </button>
        </div>
      </section>

      {notification && (
        <div style={popupContainerStyle}>
          <div style={popupStyle}>
            <div style={{ fontSize: '1.5rem' }}>🚚</div>
            <div style={{ flex: 1 }}>
              <strong style={{ display: 'block', fontSize: '0.8rem', color: '#007bff' }}>
                UPDATE
              </strong>
              <p style={{ margin: 0, fontSize: '0.95rem' }}>{notification}</p>
            </div>
            <button onClick={() => setNotification(null)} style={closeBtnStyle}>
              ✕
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

const cartBtnStyle = {
  backgroundColor: '#007bff',
  color: 'white',
  border: 'none',
  padding: '10px 20px',
  borderRadius: '8px',
  cursor: 'pointer',
  fontWeight: 'bold',
  fontSize: '0.9rem'
};

const addCartBtnStyle = {
  backgroundColor: '#28a745',
  color: 'white',
  border: 'none',
  padding: '5px 12px',
  borderRadius: '4px',
  cursor: 'pointer',
  fontSize: '0.85rem'
};

const orderBtnStyle = {
  marginTop: '12px',
  backgroundColor: '#1e1e1e',
  color: '#007bff',
  border: '1px solid #333',
  padding: '10px 20px',
  borderRadius: '8px',
  cursor: 'pointer',
  fontWeight: 'bold',
  fontSize: '0.9rem'
};

const containerStyle = {
  padding: '30px',
  color: 'white',
  backgroundColor: '#121212',
  minHeight: '100vh',
  fontFamily: 'sans-serif'
};

const headerStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'flex-start',
  marginBottom: '40px'
};

const balanceCard = {
  backgroundColor: '#1e1e1e',
  padding: '15px 25px',
  borderRadius: '12px',
  border: '1px solid #333'
};

const gridStyle = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
  gap: '20px'
};

const cardStyle = {
  backgroundColor: '#1e1e1e',
  padding: '20px',
  borderRadius: '12px',
  border: '1px solid #333',
  cursor: 'pointer'
};

const cardHeader = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '10px'
};

const addressText = {
  margin: '4px 0',
  fontSize: '0.9rem',
  whiteSpace: 'nowrap',
  overflow: 'hidden',
  textOverflow: 'ellipsis'
};

const cardFooter = {
  marginTop: '15px',
  color: '#007bff',
  fontSize: '0.85rem',
  fontWeight: 'bold'
};

const emptyState = {
  padding: '40px',
  textAlign: 'center',
  color: '#555',
  backgroundColor: '#1a1a1a',
  borderRadius: '12px'
};

const inputStyle = {
  padding: '8px',
  backgroundColor: '#1e1e1e',
  color: 'white',
  border: '1px solid #333',
  borderRadius: '8px'
};

const searchBtnStyle = {
  padding: '8px 20px',
  background: '#007bff',
  color: 'white',
  border: 'none',
  borderRadius: '8px',
  cursor: 'pointer'
};

const resultCardStyle = {
  border: '1px solid #444',
  padding: '15px',
  marginBottom: '10px',
  borderRadius: '8px',
  background: '#1e1e1e',
  transition: 'all 0.2s'
};

const expandedMenuSection = {
  marginTop: '15px',
  padding: '15px',
  background: '#111',
  borderRadius: '6px'
};

const dishRowStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  padding: '5px 0',
  borderBottom: '1px solid #222',
  fontSize: '0.9rem'
};

const tagStyle = {
  background: '#333',
  padding: '2px 8px',
  borderRadius: '12px',
  fontSize: '0.75rem'
};

const popupContainerStyle = {
  position: 'fixed',
  bottom: '20px',
  right: '20px',
  zIndex: 9999
};

const popupStyle = {
  backgroundColor: '#1e1e1e',
  color: 'white',
  padding: '15px 20px',
  borderRadius: '12px',
  border: '1px solid #007bff',
  boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
  display: 'flex',
  alignItems: 'center',
  gap: '15px',
  minWidth: '280px'
};

const closeBtnStyle = {
  background: 'none',
  border: 'none',
  color: '#666',
  cursor: 'pointer',
  fontSize: '1.2rem'
};

const statusBadge = (s) => ({
  backgroundColor: s === 'delivered' ? '#4caf50' : s === 'cancelled' ? '#f44336' : '#ff9800',
  color: 'white',
  padding: '4px 10px',
  borderRadius: '20px',
  fontSize: '0.7rem',
  fontWeight: 'bold'
});

export default CustomerDashboard;