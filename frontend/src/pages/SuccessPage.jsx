import React from "react";
import { Link, useLocation } from "react-router-dom";

const SuccessPage = () => {
  const location = useLocation();
  const orderId = location.state?.orderId;
  const total = location.state?.total;
  const status = location.state?.status;
  const displayOrderId = orderId ? `ORD-${orderId.slice(-8).toUpperCase()}` : null;
  
  return (
    <div>
      <h2>Order Confirmed</h2>
      <p>Your order was successfully placed.</p>
      {status && <p>Status: {status}</p>}
      {displayOrderId && <p>Order ID: {displayOrderId}</p>}
      {total && <p>Total Paid: ${Number(total).toFixed(2)}</p>}
      <Link to="/cart">Back to Cart</Link>
    </div>
  );
};

export default SuccessPage;