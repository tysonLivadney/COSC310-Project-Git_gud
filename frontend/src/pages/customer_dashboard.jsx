import React from 'react';
import { useCustomerSearch } from '../hooks/useCustomerSearch';

const CustomerDashboard = () => {
  const { state, setSearchTerm, setMaxPrice, setSearchType, setPage, actions } = useCustomerSearch();

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <form onSubmit={actions.executeNewSearch} style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <select value={state.searchType} onChange={(e) => setSearchType(e.target.value)}>
          <option value="restaurants">Restaurants</option>
          <option value="items">Dishes</option>
        </select>
        <input 
          placeholder="Search..." 
          value={state.searchTerm} 
          onChange={(e) => setSearchTerm(e.target.value)} 
          style={{ flex: 1 }}
        />
        <button type="submit">Search</button>
      </form>

      <div className="results-container" style={{ minHeight: '400px' }}>
        {state.loading ? (
          <p>Loading...</p>
        ) : (
          state.results.map(item => (
            <div key={item.id} style={{ border: '1px solid #444', padding: '15px', marginBottom: '10px', borderRadius: '8px' }}>
              <strong>{item.name}</strong>
              <p style={{ margin: '5px 0', fontSize: '0.9rem', color: '#888' }}>
                {state.searchType === 'restaurants' ? item.address : item.description}
              </p>
            </div>
          ))
        )}
      </div>

      {/* PAGINATION CONTROLS */}
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '20px', marginTop: '30px' }}>
        <button 
          disabled={state.page === 1 || state.loading} 
          onClick={() => setPage(prev => prev - 1)}
        >
          ← Previous
        </button>

        <span>Page {state.page}</span>

        <button 
          disabled={!state.hasMore || state.loading} 
          onClick={() => setPage(prev => prev + 1)}
        >
          Next →
        </button>
      </div>
    </div>
  );
};

export default CustomerDashboard;