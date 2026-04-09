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

    // Helper to ensure backend gets "HH:MM" or "closed"
    const formatTime = (t) => (t && t.trim() !== "") ? t.slice(0, 5) : "closed";

    const finalData = {
      ...formData,
      id: restaurantToEdit?.id, 
      rating: Number(formData.rating),
      max_prep_time_minutes: Number(formData.max_prep_time_minutes),
      opening_hours: formData.opening_hours.map(formatTime),
      closing_hours: formData.closing_hours.map(formatTime),
      tags: typeof formData.tags === 'string' 
        ? formData.tags.split(',').map(t => t.trim()).filter(t => t !== "")
        : formData.tags
    };
    
    onSubmit(finalData);
  };

  return (
    <form onSubmit={handleSubmit} style={formStyle}>
      <h3 style={{ marginTop: 0 }}>
        {restaurantToEdit ? '✨ Update Restaurant' : 'plus Add New Restaurant'}
      </h3>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {/* Name: Min 3, Max 50 */}
        <input 
          name="name" 
          value={formData.name} 
          onChange={handleChange} 
          placeholder="Restaurant Name (3-50 chars)" 
          minLength="3" 
          maxLength="50" 
          required 
        />

        <input 
          name="address" 
          value={formData.address} 
          onChange={handleChange} 
          placeholder="Full Address" 
          required 
        />

        {/* Description: Min 10 */}
        <textarea 
          name="description" 
          value={formData.description} 
          onChange={handleChange} 
          placeholder="Description (Minimum 10 characters)" 
          minLength="10" 
          rows="3" 
          required 
        />

        {/* Phone: Strict Numeric Pattern */}
        <input 
          name="phone" 
          value={formData.phone} 
          onChange={handleChange} 
          placeholder="Phone (e.g. 1234567890)" 
          pattern="[0-9]{7,15}"
          title="Phone must be between 7 and 15 digits (no spaces or dashes)"
          required 
        />
        
        <div style={{ display: 'flex', gap: '15px' }}>
           <div style={{ flex: 1 }}>
             <label style={labelStyle}>Rating (0-5)</label>
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
             <label style={labelStyle}>Prep Time (min)</label>
             <input 
               type="number" 
               name="max_prep_time_minutes" 
               value={formData.max_prep_time_minutes} 
               onChange={handleChange} 
               style={{ width: '100%' }}
             />
           </div>
        </div>
        
        <input 
          name="tags" 
          value={formData.tags} 
          onChange={handleChange} 
          placeholder="Tags (e.g. Pizza, Italian, Cheap)" 
        />
      </div>

      <h4 style={{ margin: '20px 0 10px 0' }}>Operating Hours</h4>
      <div style={hoursGrid}>
        {days.map((day, i) => (
          <div key={day} style={hourRowStyle}>
            <label style={{ width: '40px', fontWeight: 'bold' }}>{day}</label>
            <input 
              type="time" 
              value={formData.opening_hours[i]} 
              onChange={(e) => handleTimeChange(i, 'open', e.target.value)} 
            />
            <span style={{ color: '#888' }}>to</span>
            <input 
              type="time" 
              value={formData.closing_hours[i]} 
              onChange={(e) => handleTimeChange(i, 'close', e.target.value)} 
            />
          </div>
        ))}
      </div>

      <div style={{ marginTop: '25px', display: 'flex', gap: '10px' }}>
        <button type="submit" style={submitBtnStyle}>
          {restaurantToEdit ? 'Save Changes' : 'Create Restaurant'}
        </button>
        {restaurantToEdit && (
          <button type="button" onClick={onCancel} style={cancelBtnStyle}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
};

// --- STYLES ---
const formStyle = { 
  padding: '25px', 
  border: '1px solid #333', 
  borderRadius: '12px', 
  background: '#1a1a1a',
  boxShadow: '0 4px 15px rgba(0,0,0,0.3)',
  marginBottom: '30px'
};

const labelStyle = { fontSize: '0.75rem', color: '#aaa', display: 'block', marginBottom: '4px', textTransform: 'uppercase' };

const hoursGrid = { display: 'flex', flexDirection: 'column', gap: '8px', background: '#222', padding: '15px', borderRadius: '8px' };

const hourRowStyle = { display: 'flex', gap: '10px', alignItems: 'center', fontSize: '0.9rem' };

const submitBtnStyle = { 
  padding: '10px 24px', 
  background: '#44aa44', 
  color: 'white', 
  border: 'none', 
  borderRadius: '6px', 
  cursor: 'pointer', 
  fontWeight: 'bold',
  flex: 1
};

const cancelBtnStyle = { 
  padding: '10px 24px', 
  background: '#444', 
  color: 'white', 
  border: 'none', 
  borderRadius: '6px', 
  cursor: 'pointer',
  fontWeight: 'bold'
};

export default AddRestaurantForm;