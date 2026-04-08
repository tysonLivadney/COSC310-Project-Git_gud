import { useState, useEffect } from 'react';
import api from "../api.js";

export const useCustomerSearch = (initialType = "restaurants") => {
  const [searchTerm, setSearchTerm] = useState("");
  const [cuisine, setCuisine] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [searchType, setSearchType] = useState(initialType);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const LIMIT = 10;

  const handleSearch = async () => {
    setLoading(true);
    const currentOffset = (page - 1) * LIMIT;
    
    try {
      const params = new URLSearchParams();
      params.append("limit", LIMIT);
      params.append("offset", currentOffset);

      if (searchType === "restaurants") {
        if (searchTerm) params.append("name", searchTerm);
        if (cuisine) params.append("cuisine", cuisine);
      } else {
        if (searchTerm) params.append("name", searchTerm);
        if (maxPrice) params.append("max_price", maxPrice);
      }

      const endpoint = searchType === "items" ? "/menu-items/search" : "/restaurants/search";
      const response = await api.get(`${endpoint}?${params.toString()}`);
      
      setResults(response.data || []);
      setHasMore(response.data?.length === LIMIT);
    } catch (error) {
      console.error("Search failed", error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleSearch();
  }, [page, searchType]);

  const executeNewSearch = (e) => {
    if (e) e.preventDefault();
    if (page === 1) {
      handleSearch();
    } else {
      setPage(1);
    }
  };

  return {
    state: { searchTerm, cuisine, maxPrice, searchType, results, loading, page, hasMore },
    setSearchTerm, setCuisine, setMaxPrice, setSearchType, setPage,
    actions: { executeNewSearch }
  };
};