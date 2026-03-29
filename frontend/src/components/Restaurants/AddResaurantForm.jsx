import React, { useState } from 'react';

const AddRestaurantForm = ({ addRestaurant }) => {
  const [restaurantName, setRestaurantName] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    if (restaurantName) {
      addRestaurant(restaurantName);
      setRestaurantName('');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={restaurantName}
        onChange={(e) => setRestaurantName(e.target.value)}
        placeholder="Enter restaurant name"
      />
      <button type="submit">Add Restaurant</button>
    </form>
  );
};

export default AddRestaurantForm;