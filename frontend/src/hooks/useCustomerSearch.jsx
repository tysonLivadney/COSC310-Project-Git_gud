import { useState, useEffect } from 'react';
import api from "../api.js";

export const useCustomerSearch = (initialType = "restaurants") => {
  const [searchTerm, setSearchTerm] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [searchType, setSearchType] = useState(initialType);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Pagination State
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const LIMIT = 10;

  const handleSearch = async () => {
    setLoading(true);
    // Calculate offset based on current page
    const currentOffset = (page - 1) * LIMIT;
    
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append("name", searchTerm);
      params.append("limit", LIMIT);
      params.append("offset", currentOffset);
      
      let endpoint = searchType === "items" ? "/menu-items/search" : "/restaurants/search";
      if (searchType === "items" && maxPrice) params.append("max_price", maxPrice);

      const response = await api.get(`${endpoint}?${params.toString()}`);
      
      // REPLACE results instead of appending
      setResults(response.data);
      
      // If we got exactly LIMIT, assume there's a next page
      setHasMore(response.data.length === LIMIT);
    } catch (error) {
      console.error("Search failed", error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  // Trigger search whenever page or searchType changes
  useEffect(() => {
    handleSearch();
  }, [page, searchType]);

  // Reset to page 1 when user types a new search or changes tabs
  const executeNewSearch = (e) => {
    if (e) e.preventDefault();
    if (page === 1) {
      handleSearch(); // Already on page 1, just refresh
    } else {
      setPage(1); // Setting this triggers the useEffect above
    }
  };

  return {
    state: { searchTerm, maxPrice, searchType, results, loading, page, hasMore },
    setSearchTerm, setMaxPrice, setSearchType, setPage,
    actions: { executeNewSearch }
  };
};