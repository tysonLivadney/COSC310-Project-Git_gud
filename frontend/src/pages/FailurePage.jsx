import React from "react";
import { Link, useLocation } from "react-router-dom";

const FailurePage = () => {
  const location = useLocation();
  const error = location.state?.error || "Payment failed.";
  const orderId = location.state?.orderId;

  return (
    <div>
      <h2>Payment Failed</h2>
      {orderId && <p>Order ID: {orderId}</p>}
      <p style={{ color: "red" }}>{error}</p>
      <Link to="/cart">Back to Cart</Link>
    </div>
  );
};

export default FailurePage;