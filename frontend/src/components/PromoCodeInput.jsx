import React, { useState } from 'react';
import api from '../api';

const PromoCodeInput = ({ orderSubtotal, onApply, onRemove }) => {
  const [code, setCode] = useState('');
  const [applied, setApplied] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleApply = async () => {
    if (!code.trim()) return;
    setError('');
    setLoading(true);
    try {
      const res = await api.post('/promo-codes/validate', {
        code: code.trim(),
        order_subtotal: orderSubtotal,
      });
      setApplied(res.data.promo_code);
      if (onApply) onApply(res.data.promo_code);
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid promo code');
      setApplied(null);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = () => {
    setApplied(null);
    setCode('');
    setError('');
    if (onRemove) onRemove();
  };

  if (applied) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px', background: '#1a2e1a', border: '1px solid #2e7d32', borderRadius: '8px' }}>
        <span style={{ color: '#4caf50' }}>✓ {applied.code}</span>
        <span style={{ color: '#aaa', fontSize: '0.85rem' }}>
          {applied.discount_type === 'percentage' ? `${applied.discount_value}% off` : `$${applied.discount_value} off`}
        </span>
        <button onClick={handleRemove} style={{ marginLeft: 'auto', background: 'transparent', color: '#f44336', border: 'none', cursor: 'pointer', fontSize: '0.85rem' }}>
          Remove
        </button>
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', gap: '8px' }}>
        <input
          placeholder="Promo code"
          value={code}
          onChange={e => setCode(e.target.value)}
          style={{ padding: '8px', backgroundColor: '#1e1e1e', color: 'white', border: '1px solid #333', borderRadius: '8px', flex: 1 }}
        />
        <button
          onClick={handleApply}
          disabled={loading || !code.trim()}
          style={{ padding: '8px 16px', background: '#007bff', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', opacity: loading ? 0.6 : 1 }}
        >
          {loading ? '...' : 'Apply'}
        </button>
      </div>
      {error && <p style={{ color: '#f44336', fontSize: '0.85rem', margin: '5px 0 0 0' }}>{error}</p>}
    </div>
  );
};

export default PromoCodeInput;
