import React, { useState } from "react";

const PaymentForm = ({ onSubmit, loading }) => {
  const [paymentInfo, setPaymentInfo] = useState({
    card_number: "",
    expiry: "",
    cvv: "",
  });

  const handleChange = (e) => {
    setPaymentInfo({ ...paymentInfo, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (loading) return;
    onSubmit({
      card_number: paymentInfo.card_number.trim(),
      expiry: paymentInfo.expiry.trim(),
      cvv: paymentInfo.cvv.trim(),
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3>Payment Information</h3>

      <div>
        <label htmlFor="card_number">Card Number</label>
        <input
          id="card_number"
          name="card_number"
          type="text"
          value={paymentInfo.card_number}
          onChange={handleChange}
          placeholder="Enter card number"
          required
        />
      </div>

      <div>
        <label htmlFor="expiry">Expiry (MM/YY)</label>
        <input
          id="expiry"
          name="expiry"
          type="text"
          value={paymentInfo.expiry}
          onChange={handleChange}
          placeholder="MM/YY"
          required
        />
      </div>

      <div>
        <label htmlFor="cvv">CVV</label>
        <input
          id="cvv"
          name="cvv"
          type="text"
          value={paymentInfo.cvv}
          onChange={handleChange}
          placeholder="123"
          required
        />
      </div>

      <button type="submit" disabled={loading}>
        {loading ? "Processing..." : "Confirm Order"}
      </button>
    </form>
  );
};

export default PaymentForm;