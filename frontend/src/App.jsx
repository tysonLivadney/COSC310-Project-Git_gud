import React from 'react';
import './App.css';
import RestaurantList from './components/Restaurants/Restaurants';

const App = () => {
  return (
    <BrowserRouter>
      <routes>
        <Route path="/restaurants" element={<RestaurantList />} />
      </routes>
    </BrowserRouter>
  );
};

export default App;