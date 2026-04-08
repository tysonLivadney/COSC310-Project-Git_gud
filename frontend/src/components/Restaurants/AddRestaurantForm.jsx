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
    } else {
      setFormData(initialFormState);
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
    if (!restaurantToEdit) setFormData(initialFormState);
  };

  return (
    <form onSubmit={handleSubmit} style={{ padding: '20px', border: '1px solid #444', borderRadius: '8px' }}>
      <h3>{restaurantToEdit ? 'Update Restaurant' : 'Add New Restaurant'}</h3>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <input name="name" value={formData.name} onChange={handleChange} placeholder="Name" required />
        <input name="address" value={formData.address} onChange={handleChange} placeholder="Address" required />
        <textarea name="description" value={formData.description} onChange={handleChange} placeholder="Description" rows="3" required />
        <input name="phone" value={formData.phone} onChange={handleChange} placeholder="Phone" required />
        <input type="number" name="rating" value={formData.rating} onChange={handleChange} placeholder="Rating" step="0.1" />
        <input type="number" name="max_prep_time_minutes" value={formData.max_prep_time_minutes} onChange={handleChange} placeholder="Prep Time" />
        <input name="tags" value={formData.tags} onChange={handleChange} placeholder="Tags (comma separated)" />
      </div>

      <h4>Hours</h4>
      {days.map((day, i) => (
        <div key={day} style={{ marginBottom: '5px', display: 'flex', gap: '5px', alignItems: 'center' }}>
          <label style={{ width: '45px' }}>{day}</label>
          <input type="time" value={formData.opening_hours[i]} onChange={(e) => handleTimeChange(i, 'open', e.target.value)} />
          <span>-</span>
          <input type="time" value={formData.closing_hours[i]} onChange={(e) => handleTimeChange(i, 'close', e.target.value)} />
        </div>
      ))}

      <div style={{ marginTop: '15px' }}>
        <button type="submit">{restaurantToEdit ? 'Save' : 'Add'}</button>
        {restaurantToEdit && <button type="button" onClick={onCancel} style={{ marginLeft: '10px' }}>Cancel</button>}
      </div>
    </form>
  );
};

export default AddRestaurantForm;