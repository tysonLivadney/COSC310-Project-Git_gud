import React, { useState, useEffect } from 'react';

const AddRestaurantForm = ({ onSubmit, restaurantToEdit = null, onCancel }) => {
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

  const initialFormState = {
    name: '',
    address: '',
    description: '',
    phone: '',
    rating: 0,
    tags: '',
    max_prep_time_minutes: 30,
    opening_hours: Array(7).fill(""),
    closing_hours: Array(7).fill("")
  };

  const [formData, setFormData] = useState(initialFormState);

  useEffect(() => {
    if (restaurantToEdit) {
      setFormData({
        ...restaurantToEdit,
        tags: Array.isArray(restaurantToEdit.tags) ? restaurantToEdit.tags.join(', ') : '',
      });
    }
  }, [restaurantToEdit]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleTimeChange = (index, type, value) => {
    const field = type === 'open' ? 'opening_hours' : 'closing_hours';
    const newTimes = [...formData[field]];
    newTimes[index] = value; 
    setFormData(prev => ({ ...prev, [field]: newTimes }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const finalData = {
      ...formData,
      id: restaurantToEdit?.id, 
      rating: Number(formData.rating),
      max_prep_time_minutes: Number(formData.max_prep_time_minutes),
      tags: typeof formData.tags === 'string' 
        ? formData.tags.split(',').map(t => t.trim()).filter(t => t !== "")
        : formData.tags
    };
    onSubmit(finalData);
  };

  return (
    <form onSubmit={handleSubmit} style={{ padding: '20px', border: '1px solid #444', borderRadius: '8px', background: '#1a1a1a' }}>
      <h3 style={{ marginTop: 0 }}>{restaurantToEdit ? 'Update Restaurant' : 'Add New Restaurant'}</h3>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <input name="name" value={formData.name} onChange={handleChange} placeholder="Name" required />
        <input name="address" value={formData.address} onChange={handleChange} placeholder="Address" required />
        <textarea name="description" value={formData.description} onChange={handleChange} placeholder="Description" rows="3" required />
        <input name="phone" value={formData.phone} onChange={handleChange} placeholder="Phone" required />
        
        <div style={{ display: 'flex', gap: '15px' }}>
           <div style={{ flex: 1 }}>
             <label style={{ fontSize: '0.8rem', display: 'block', marginBottom: '4px' }}>Rating (0-5)</label>
             <input 
               type="number" 
               name="rating"
               min="0" 
               max="5" 
               step="0.1" 
               value={formData.rating} 
               onChange={handleChange} 
               style={{ width: '100%' }}
             />
           </div>
           <div style={{ flex: 1 }}>
             <label style={{ fontSize: '0.8rem', display: 'block', marginBottom: '4px' }}>Prep Time (min)</label>
             <input 
               type="number" 
               name="max_prep_time_minutes" 
               value={formData.max_prep_time_minutes} 
               onChange={handleChange} 
               style={{ width: '100%' }}
             />
           </div>
        </div>
        
        <input name="tags" value={formData.tags} onChange={handleChange} placeholder="Tags (comma separated: Pizza, Italian, Cheap)" />
      </div>

      <h4 style={{ marginBottom: '10px' }}>Operating Hours</h4>
      {days.map((day, i) => (
        <div key={day} style={{ marginBottom: '5px', display: 'flex', gap: '5px', alignItems: 'center' }}>
          <label style={{ width: '45px', fontSize: '0.9rem' }}>{day}</label>
          <input type="time" value={formData.opening_hours[i]} onChange={(e) => handleTimeChange(i, 'open', e.target.value)} />
          <span>-</span>
          <input type="time" value={formData.closing_hours[i]} onChange={(e) => handleTimeChange(i, 'close', e.target.value)} />
        </div>
      ))}

      <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
        <button type="submit" style={{ padding: '8px 20px', background: '#44aa44', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          {restaurantToEdit ? 'Save Changes' : 'Add Restaurant'}
        </button>
        {restaurantToEdit && (
          <button type="button" onClick={onCancel} style={{ padding: '8px 20px', background: '#555', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
};

export default AddRestaurantForm;