import React from "react";

const OrderSummary = ({ orderTotal }) => {
  if (!orderTotal) return null;

  return (
    <div>
      <h3>Order Summary</h3>
      <p>Subtotal: ${Number(orderTotal.subtotal).toFixed(2)}</p>
      <p>Tax Rate: {Number(orderTotal.tax_rate).toFixed(2)}</p>
      <p>Tax: ${Number(orderTotal.tax).toFixed(2)}</p>
      <p>Delivery Fee: ${Number(orderTotal.delivery_fee).toFixed(2)}</p>
      <h4>Total: ${Number(orderTotal.total).toFixed(2)}</h4>
    </div>
  );
};

export default OrderSummary;