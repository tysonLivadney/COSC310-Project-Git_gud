import React, { useState } from 'react';

const MenuForm = ({ restaurantId, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    restaurant_id: restaurantId
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
    setFormData({ name: '', description: '', restaurant_id: restaurantId });
  };

  return (
    <form onSubmit={handleSubmit} style={{ border: '1px solid #555', padding: '15px', borderRadius: '6px', marginTop: '10px' }}>
      <h4>Add New Menu</h4>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <input 
          value={formData.name} 
          onChange={(e) => setFormData({...formData, name: e.target.value})} 
          placeholder="Menu Name (e.g. Lunch Specials)" 
          required 
        />
        <textarea 
          value={formData.description} 
          onChange={(e) => setFormData({...formData, description: e.target.value})} 
          placeholder="Menu Description" 
          required 
        />
        <div style={{ display: 'flex', gap: '10px' }}>
          <button type="submit">Save Menu</button>
          <button type="button" onClick={onCancel}>Cancel</button>
        </div>
      </div>
    </form>
  );
};

export default MenuForm;