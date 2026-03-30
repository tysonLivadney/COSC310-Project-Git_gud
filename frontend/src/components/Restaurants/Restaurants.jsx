import React, { useEffect, useState } from 'react';
import api from "../../api.js";
import AddRestaurantForm from './AddRestaurantForm.jsx';

const Restaurants = () => {
  const [restaurants, setRestaurants] = useState([]);

  const fetchRestaurants = async () => {
    try {
      const me = await api.get('/auth/me');
      const response = await api.get('/restaurants');
      const myRestaurants = response.data.filter(r => r.owner_id === me.data.id);
      setRestaurants(myRestaurants);
    } catch (error) {
      console.error("Error fetching restaurants", error);
    }
  };

  const addRestaurant = async (restaurantData) => {
    try {
      await api.post('/restaurants', restaurantData);
      fetchRestaurants(); 
    } catch (error) {
      console.error("Error adding restaurant", error);
    }
  };

  useEffect(() => {
    fetchRestaurants();
  }, []);

  return (
    <div>
      <h2>Owned Restaurants</h2>
      <ul>
        {restaurants.map((restaurant, index) => (
          <li key={index}>{restaurant.name} - {restaurant.address} - {restaurant.description} - {restaurant.phone} - {restaurant.rating} - {restaurant.tags}</li>
        ))}
      </ul>
      <AddRestaurantForm addRestaurant={addRestaurant} />
    </div>
  );
};

export default Restaurants;