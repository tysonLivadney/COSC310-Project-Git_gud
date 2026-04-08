import React, { useEffect, useState } from 'react';
import api from "../api.js";
import AddRestaurantForm from '../components/Restaurants/AddRestaurantForm';
import Restaurant from '../components/Restaurants/Restaurants';

const ManagerDashboard = () => {
  const [restaurants, setRestaurants] = useState([]);
  const [menus, setMenus] = useState({}); 
  const [menuItems, setMenuItems] = useState([]);
  const [editingRestaurant, setEditingRestaurant] = useState(null);
  const [error, setError] = useState("");

  const fetchData = async () => {
    try {
      const me = await api.get('/auth/me');
      const resResponse = await api.get('/restaurants');
      const myRestaurants = resResponse.data.filter(r => r.owner_id === me.data.id);
      setRestaurants(myRestaurants);

      const menuPromises = myRestaurants.map(res => api.get(`/restaurants/${res.id}/menus`));
      const menuResults = await Promise.all(menuPromises);
      
      const menusMap = {};
      menuResults.forEach((result, index) => {
        menusMap[myRestaurants[index].id] = result.data;
      });
      setMenus(menusMap);

      const itemResponse = await api.get('/menu-items'); 
      setMenuItems(itemResponse.data);
      setError("");
    } catch (err) {
      setError("Failed to load dashboard data.");
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleDeleteRestaurant = async (id) => {
    if (!window.confirm("Delete this restaurant? This will remove all menus and items.")) return;
    try {
      await api.delete(`/restaurants/${id}`);
      fetchData();
    } catch (err) { setError("Failed to delete restaurant."); }
  };

  const handleDeleteMenu = async (id) => {
    if (!window.confirm("Delete this menu?")) return;
    try {
      await api.delete(`/menus/${id}`);
      fetchData();
    } catch (err) { setError("Failed to delete menu."); }
  };

  const handleDeleteMenuItem = async (id) => {
    if (!window.confirm("Delete this item?")) return;
    try {
      await api.delete(`/menu-items/${id}`);
      fetchData();
    } catch (err) { setError("Failed to delete item."); }
  };

  const handleAddMenu = async (menuData) => {
    try {
      await api.post('/menus', menuData);
      fetchData();
    } catch (err) { setError("Error saving menu."); }
  };

  const handleAddMenuItem = async (itemData) => {
    try {
      await api.post('/menu-items', itemData);
      fetchData();
    } catch (err) { setError("Error saving item."); }
  };

  const handleAddOrUpdateRes = async (data) => {
    try {
      if (editingRestaurant) {
        await api.put(`/restaurants/${data.id}`, data);
      } else {
        await api.post('/restaurants', data);
      }
      setEditingRestaurant(null);
      fetchData();
    } catch (err) { setError("Error saving restaurant."); }
  };

  return (
    <div className="dashboard-container">
      <h1>Manager Dashboard</h1>
      {error && <div style={{ color: '#ff4444', marginBottom: '20px', fontWeight: 'bold' }}>{error}</div>}

      <AddRestaurantForm 
        onSubmit={handleAddOrUpdateRes} 
        restaurantToEdit={editingRestaurant}
        onCancel={() => setEditingRestaurant(null)}
      />

      <hr style={{ margin: '30px 0', border: '0.5px solid #444' }} />

      <div className="restaurant-list">
        {restaurants.map(res => (
          <Restaurant 
            key={res.id} 
            restaurant={res} 
            menus={menus[res.id] || []}
            menuItems={menuItems}
            onDelete={() => handleDeleteRestaurant(res.id)}
            onDeleteMenu={handleDeleteMenu}
            onDeleteMenuItem={handleDeleteMenuItem}
            onAddMenu={handleAddMenu}
            onAddMenuItem={handleAddMenuItem}
            onEdit={(res) => {
              setEditingRestaurant(res);
              window.scrollTo(0, 0);
            }} 
          />
        ))}
      </div>
    </div>
  );
};

export default ManagerDashboard;