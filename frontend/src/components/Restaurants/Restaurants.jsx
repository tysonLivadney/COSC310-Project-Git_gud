import React, { useState } from 'react';
import MenuForm from './MenuForm';
import MenuItemForm from './MenuItemForm';

const Restaurant = ({ 
  restaurant, onEdit, onDelete, 
  onAddMenu, onDeleteMenu, 
  onAddMenuItem, onDeleteMenuItem, 
  menus = [], menuItems = [] 
}) => {
  const [showMenuForm, setShowMenuForm] = useState(false);
  const [activeMenuFormId, setActiveMenuFormId] = useState(null);

  return (
    <div style={{ border: '1px solid #444', padding: '20px', margin: '15px 0', borderRadius: '10px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2 style={{ margin: 0 }}>{restaurant.name} ⭐ {restaurant.rating}</h2>
          <p style={{ color: '#aaa', fontSize: '0.9rem' }}>{restaurant.address}</p>
        </div>
        <div>
          <button onClick={() => onEdit(restaurant)} style={{ marginRight: '10px' }}>Edit</button>
          <button onClick={onDelete} style={{ color: '#ff4444', border: '1px solid #ff4444', background: 'transparent' }}>Delete Restaurant</button>
        </div>
      </div>

      <p>{restaurant.description}</p>

      <div style={{ background: 'rgba(255,255,255,0.05)', padding: '15px', borderRadius: '8px', marginTop: '15px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <h3 style={{ margin: 0 }}>Menus</h3>
          <button onClick={() => setShowMenuForm(!showMenuForm)}>
            {showMenuForm ? 'Close' : '+ Add Menu'}
          </button>
        </div>

        {menus.map(menu => (
          <div key={menu.id} style={{ borderLeft: '2px solid #555', paddingLeft: '15px', marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h4 style={{ margin: '0' }}>{menu.name}</h4>
                <p style={{ fontSize: '0.85rem', color: '#888', margin: '2px 0 10px 0' }}>{menu.description}</p>
              </div>
              <div style={{ display: 'flex', gap: '5px' }}>
                <button onClick={() => setActiveMenuFormId(activeMenuFormId === menu.id ? null : menu.id)} style={{ fontSize: '0.7rem' }}>+ Item</button>
                <button onClick={() => onDeleteMenu(menu.id)} style={{ fontSize: '0.7rem', color: '#ff4444', border: '1px solid #ff4444', background: 'transparent' }}>Delete Menu</button>
              </div>
            </div>

            <ul style={{ listStyle: 'none', padding: 0 }}>
              {menuItems.filter(item => item.menu_id === menu.id).map(item => (
                <li key={item.id} style={{ padding: '8px 0', borderBottom: '1px solid #333', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <span style={{ fontWeight: '500' }}>{item.name}</span>
                    <span style={{ marginLeft: '10px', color: '#44aa44' }}>${item.price.toFixed(2)}</span>
                    {!item.in_stock && <span style={{ color: '#ff4444', fontSize: '0.7rem', marginLeft: '10px' }}>(Sold Out)</span>}
                  </div>
                  <button onClick={() => onDeleteMenuItem(item.id)} style={{ padding: '2px 8px', color: '#ff4444', cursor: 'pointer', background: 'none', border: '1px solid #444' }}>
                    ✕
                  </button>
                </li>
              ))}
            </ul>

            {activeMenuFormId === menu.id && (
              <MenuItemForm 
                menuId={menu.id} 
                onCancel={() => setActiveMenuFormId(null)}
                onSubmit={(itemData) => {
                  onAddMenuItem(itemData);
                  setActiveMenuFormId(null);
                }}
              />
            )}
          </div>
        ))}

        {showMenuForm && (
          <MenuForm 
            restaurantId={restaurant.id} 
            onSubmit={(menuData) => {
              onAddMenu(menuData);
              setShowMenuForm(false);
            }}
            onCancel={() => setShowMenuForm(false)}
          />
        )}
      </div>
    </div>
  );
};

export default Restaurant;