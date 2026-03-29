import React, { useEffect, useState } from 'react';
import api from "../../api.js";
import AddRestaurantForm from './AddResaurantForm.jsx';

const RestaurantList = () => {
  const [restaurants, setRestaurants] = useState([]);

  const fetchRestaurants = async () => {
    try {
      const response = await api.get('/restaurants');
      setRestaurants(response.data.restaurants);
    } catch (error) {
      console.error("Error fetching restaurants", error);
    }
  };

  const addRestaurant = async (restaurantName) => {
    try {
      await api.post('/restaurants', { name: restaurantName });
      fetchRestaurants();  // Refresh the list after adding a restaurant
    } catch (error) {
      console.error("Error adding fruit", error);
    }
  };

  useEffect(() => {
    fetchRestaurants();
  }, []);

  return (
    <div>
      <h2>Restaurants List</h2>
      <ul>
        {restaurants.map((restaurant, index) => (
          <li key={index}>{restaurant.name}</li>
        ))}
      </ul>
      <AddRestaurantForm addRestaurant={addRestaurant} />
    </div>
  );
};

export default RestaurantList;