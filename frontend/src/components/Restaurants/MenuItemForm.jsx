import React, { useState } from 'react';

const MenuItemForm = ({ menuId, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: 0,
    in_stock: true,
    menu_id: menuId
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ ...formData, price: Number(formData.price) });
    setFormData({ name: '', description: '', price: 0, in_stock: true, menu_id: menuId });
  };

  return (
    <form onSubmit={handleSubmit} style={{ border: '1px solid #666', padding: '10px', borderRadius: '4px', marginTop: '10px' }}>
      <h5>Add Item</h5>
      <div style={{ display: 'grid', gap: '8px' }}>
        <input 
          value={formData.name} 
          onChange={(e) => setFormData({...formData, name: e.target.value})} 
          placeholder="Item Name" 
          required 
        />
        <input 
          type="number" 
          value={formData.price} 
          onChange={(e) => setFormData({...formData, price: e.target.value})} 
          placeholder="Price" 
          step="0.01"
          required 
        />
        <textarea 
          value={formData.description} 
          onChange={(e) => setFormData({...formData, description: e.target.value})} 
          placeholder="Description" 
          required 
        />
        <label>
          <input 
            type="checkbox" 
            checked={formData.in_stock} 
            onChange={(e) => setFormData({...formData, in_stock: e.target.checked})} 
          /> In Stock
        </label>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button type="submit" style={{ fontSize: '0.8rem' }}>Add Item</button>
          <button type="button" onClick={onCancel} style={{ fontSize: '0.8rem' }}>Cancel</button>
        </div>
      </div>
    </form>
  );
};

export default MenuItemForm;