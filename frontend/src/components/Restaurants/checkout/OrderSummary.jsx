import React from "react";

const OrderSummary = ({ orderTotal, discount }) => {
  if (!orderTotal) return null;

  const subtotal = Number(orderTotal.subtotal);
  const tax = Number(orderTotal.tax);
  const deliveryFee = Number(orderTotal.delivery_fee);
  const discountAmount = discount ? Number(discount) : 0;
  const total = subtotal + tax + deliveryFee - discountAmount;

  return (
    <div>
      <h3>Order Summary</h3>
      <p>Subtotal: ${subtotal.toFixed(2)}</p>
      <p>Tax Rate: {(Number(orderTotal.tax_rate)*100).toFixed(2)}%</p>
      <p>Tax: ${tax.toFixed(2)}</p>
      <p>Delivery Fee: ${deliveryFee.toFixed(2)}</p>
      {discountAmount > 0 && (
        <p style={{ color: '#2e7d32' }}>Discount: -${discountAmount.toFixed(2)}</p>
      )}
      <h4>Total: ${(total < 0 ? 0 : total).toFixed(2)}</h4>
    </div>
  );
};

export default OrderSummary;
