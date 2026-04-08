import React, { useEffect, useState, useCallback } from 'react';
import api from "../api.js";
import AddRestaurantForm from '../components/Restaurants/AddRestaurantForm';
import Restaurant from '../components/Restaurants/Restaurant';

const ManagerDashboard = () => {
  const [restaurants, setRestaurants] = useState([]);
  const [menus, setMenus] = useState({});
  const [menuItems, setMenuItems] = useState([]);
  const [editingRestaurant, setEditingRestaurant] = useState(null);
  const [error, setError] = useState("");

  const fetchData = useCallback(async () => {
    try {
      const me = await api.get('/auth/me');
      const resResponse = await api.get('/restaurants');
      const myRestaurants = resResponse.data.filter(r => r.owner_id === me.data.id);
      setRestaurants(myRestaurants);

      const menuPromises = myRestaurants.map(res => api.get(`/restaurants/${res.id}/menus`));
      const menuResults = await Promise.all(menuPromises);
      
      const menusMap = {};
      const allMyMenuIds = [];
      
      menuResults.forEach((result, index) => {
        const restaurantId = myRestaurants[index].id;
        menusMap[restaurantId] = result.data;
        result.data.forEach(m => allMyMenuIds.push(m.id));
      });
      setMenus(menusMap);

      const itemPromises = allMyMenuIds.map(menuId => api.get(`/menus/${menuId}/items`));
      const itemResults = await Promise.all(itemPromises);
      setMenuItems(itemResults.flatMap(r => r.data));
      
      setError(""); 
    } catch (err) {
      setError("Failed to load dashboard data.");
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  // --- RESTAURANT HANDLERS ---
  const handleAddOrUpdateRes = async (data) => {
    try {
      if (editingRestaurant) {
        await api.put(`/restaurants/${data.id}`, data);
      } else {
        const { id, ...payload } = data;
        await api.post('/restaurants', payload);
      }
      setEditingRestaurant(null);
      setError("");
      fetchData();
    } catch (err) { setError("Error saving restaurant."); }
  };

  const handleDeleteRestaurant = async (id) => {
    if (!window.confirm("Delete restaurant and all its data?")) return;
    try {
      await api.delete(`/restaurants/${id}`);
      fetchData();
    } catch (err) { setError("Delete failed."); }
  };

  // --- MENU HANDLERS ---
  const handleAddMenu = async (menuData) => {
    try {
      const { id, ...payload } = menuData;
      await api.post('/menus', payload);
      setError("");
      fetchData();
    } catch (err) { setError("Failed to add menu."); }
  };

  const handleDeleteMenu = async (menuId) => {
    if (!window.confirm("Delete this menu?")) return;
    try {
      await api.delete(`/menus/${menuId}`);
      fetchData();
    } catch (err) { setError("Delete failed."); }
  };

  // --- ITEM HANDLERS ---
  const handleAddMenuItem = async (itemData) => {
    try {
      const { id, ...payload } = itemData;
      await api.post('/menu-items', payload);
      setError("");
      fetchData();
    } catch (err) { setError("Failed to add item."); }
  };

  const handleDeleteMenuItem = async (itemId) => {
    if (!window.confirm("Delete this item?")) return;
    try {
      await api.delete(`/menu-items/${itemId}`);
      fetchData();
    } catch (err) { setError("Delete failed."); }
  };

  return (
    <div className="dashboard-container">
      <h1>Manager Dashboard</h1>
      {error && <div style={{ color: 'white', background: '#d9534f', padding: '10px', marginBottom: '20px' }}>{error}</div>}

      <AddRestaurantForm 
        onSubmit={handleAddOrUpdateRes} 
        restaurantToEdit={editingRestaurant}
        onCancel={() => setEditingRestaurant(null)}
      />

      <div className="restaurant-list">
        {restaurants.map(res => (
          <Restaurant 
            key={res.id} 
            restaurant={res} 
            menus={menus[res.id] || []}
            menuItems={menuItems}
            onEdit={(r) => { setEditingRestaurant(r); window.scrollTo(0, 0); }}
            onDelete={() => handleDeleteRestaurant(res.id)}
            onAddMenu={handleAddMenu} 
            onDeleteMenu={handleDeleteMenu}
            onAddMenuItem={handleAddMenuItem}
            onDeleteMenuItem={handleDeleteMenuItem}
          />
        ))}
      </div>
    </div>
  );
};

export default ManagerDashboard;