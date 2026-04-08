import React from 'react';
import { useCustomerSearch } from '../hooks/useCustomerSearch';

const CustomerDashboard = () => {
  const { state, setSearchTerm, setCuisine, setMaxPrice, setSearchType, setPage, actions } = useCustomerSearch();

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Customer Dashboard</h1>
      
      <form onSubmit={actions.executeNewSearch} style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}>
        <div style={{ display: 'flex', gap: '10px' }}>
          <select 
            value={state.searchType} 
            onChange={(e) => {
              setSearchType(e.target.value);
              setPage(1);
            }}
            style={{ padding: '8px' }}
          >
            <option value="restaurants">Search Restaurants</option>
            <option value="items">Search Dishes</option>
          </select>
          
          <input 
            placeholder={state.searchType === 'restaurants' ? "Restaurant Name..." : "Dish Name..."}
            value={state.searchTerm} 
            onChange={(e) => setSearchTerm(e.target.value)} 
            style={{ flex: 1, padding: '8px' }}
          />
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          {state.searchType === 'restaurants' ? (
            <input 
              placeholder="Cuisine (e.g. Italian, Burgers)" 
              value={state.cuisine} 
              onChange={(e) => setCuisine(e.target.value)}
              style={{ flex: 1, padding: '8px' }}
            />
          ) : (
            <input 
              type="number"
              placeholder="Max Price ($)" 
              value={state.maxPrice} 
              onChange={(e) => setMaxPrice(e.target.value)}
              style={{ flex: 1, padding: '8px' }}
            />
          )}
          <button type="submit" style={{ padding: '8px 20px', background: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}>
            Search
          </button>
        </div>
      </form>

      <div className="results-container" style={{ minHeight: '400px' }}>
        {state.loading ? (
          <p>Loading...</p>
        ) : state.results && state.results.length > 0 ? (
          state.results.map(item => (
            <div key={item.id} style={{ border: '1px solid #444', padding: '15px', marginBottom: '10px', borderRadius: '8px', background: '#1e1e1e' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <strong style={{ fontSize: '1.2rem' }}>{item.name}</strong>
                <span style={{ color: '#ffc107' }}>⭐ {item.rating ?? 'N/A'}</span>
              </div>
              
              <p style={{ margin: '5px 0', color: '#bbb' }}>
                {state.searchType === 'restaurants' ? item.address : item.description}
              </p>

              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', alignItems: 'center' }}>
                {state.searchType === 'restaurants' ? (
                  <div style={{ display: 'flex', gap: '5px' }}>
                    {item.tags?.map(tag => (
                      <span key={tag} style={{ background: '#333', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem' }}>
                        {tag}
                      </span>
                    ))}
                  </div>
                ) : (
                  <span style={{ color: '#44aa44', fontWeight: 'bold' }}>
                    {/* FIXED: Check if price exists before calling toFixed */}
                    {typeof item.price === 'number' ? `$${item.price.toFixed(2)}` : 'N/A'}
                  </span>
                )}
                
                {item.max_prep_time_minutes && (
                  <span style={{ fontSize: '0.8rem', color: '#888' }}>🕒 {item.max_prep_time_minutes} min prep</span>
                )}
              </div>
            </div>
          ))
        ) : (
          <div style={{ textAlign: 'center', marginTop: '50px', color: '#888' }}>
            <h3>No results found</h3>
          </div>
        )}
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '20px', marginTop: '30px', paddingBottom: '40px' }}>
        <button disabled={state.page === 1 || state.loading} onClick={() => setPage(prev => prev - 1)}>
          ← Previous
        </button>
        <span>Page {state.page}</span>
        <button disabled={!state.hasMore || state.loading} onClick={() => setPage(prev => prev + 1)}>
          Next →
        </button>
      </div>
    </div>
  );
};

export default CustomerDashboard;