import React from 'react';
import './App.css';
import RestaurantList from './components/Restaurants/Restaurants';

const App = () => {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Food Delivery App</h1>
      </header>
      <main>
        <RestaurantList />
      </main>
    </div>
  );
};

export default App;