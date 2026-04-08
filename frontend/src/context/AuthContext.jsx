import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('user');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });

  const [token, setToken] = useState(() => localStorage.getItem('token'));

  // Initialize balance from localStorage
  const [balance, setBalance] = useState(() => {
    const storedBalance = localStorage.getItem('user_balance');
    return storedBalance ? parseFloat(storedBalance) : 0.00;
  });

  // Sync balance to localStorage
  useEffect(() => {
    localStorage.setItem('user_balance', balance.toFixed(2));
  }, [balance]);

  const login = useCallback((tokenValue, userData) => {
    localStorage.setItem('token', tokenValue);
    localStorage.setItem('user', JSON.stringify(userData));
    setToken(tokenValue);
    setUser(userData);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('user_balance');
    setToken(null);
    setUser(null);
    setBalance(0.00);
  }, []);

  const addToBalance = useCallback((amount) => {
    console.log("Context: Adding", amount);
    setBalance((prev) => {
      const current = parseFloat(prev) || 0;
      const add = parseFloat(amount) || 0;
      const result = current + add;
      console.log("Context: New Balance will be", result);
      return result;
    });
  }, []);

  const value = {
    user,
    token,
    balance,
    login,
    logout,
    addToBalance,
    isAuthenticated: !!token
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};


export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};