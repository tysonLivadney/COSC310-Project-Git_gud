import React from "react";
import { useLocation, Link } from "react-router-dom";

const PaymentFailedPage = () => {
  const location = useLocation();
  const error = location.state?.error || "Payment failed.";

  return (
    <div>
      <h2>Payment Failed</h2>
      <p>{error}</p>
      <Link to="/cart">Back to Cart</Link>
    </div>
  );
};

export default PaymentFailedPage;