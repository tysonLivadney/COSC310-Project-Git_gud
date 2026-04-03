import React, { useState } from 'react';

const AddRestaurantForm = ({ addRestaurant }) => {
  const [name, setName] = useState('');
  const [address, setAddress] = useState('');
  const [description, setDescription] = useState('');
  const [phone, setPhone] = useState('');
  const [rating, setRating] = useState(0);
  const [tags, setTags] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    if (name && address && description && phone) {
      addRestaurant(
        {
          name: name,
          address: address,
          description: description,
          phone: phone,
          rating: rating,
          tags: tags.split(',').map(t => t.trim())
        }
      );
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="text" value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Enter restaurant name"
      />
      <input type="text" value={address}
        onChange={(e) => setAddress(e.target.value)}
        placeholder="Enter restaurant address"
      />
      <input type="text" value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Enter restaurant description"
      />
      <input type="text" value={phone}
        onChange={(e) => setPhone(e.target.value)}
        placeholder="Enter restaurant phone"
      />
      <input type="number" value={rating}
        onChange={(e) => setRating(e.target.value)}
        placeholder="Enter restaurant rating"
      />
      <input type="text" value={tags}
        onChange={(e) => setTags(e.target.value)}
        placeholder="Enter restaurant tags"
      />
      <button type="submit">Add Restaurant</button>
    </form>
  );
};

export default AddRestaurantForm;