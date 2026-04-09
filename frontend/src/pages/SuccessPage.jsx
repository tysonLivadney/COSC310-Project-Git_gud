import React from "react";
import { useLocation, Link } from "react-router-dom";

const SuccessPage = () => {
  const location = useLocation();
  const { orderId, total, status, promoCode, discount } = location.state || {};

  return (
    <div>
      <h2>Order Confirmed</h2>
      <p>Order ID: {orderId}</p>
      <p>Status: {status}</p>
      {promoCode && <p>Promo Code: {promoCode} (-${Number(discount || 0).toFixed(2)})</p>}
      <p>Total: ${Number(total || 0).toFixed(2)}</p>
      <Link to="/customer-dashboard">Back to Home</Link>
    </div>
  );
};

export default SuccessPage;
