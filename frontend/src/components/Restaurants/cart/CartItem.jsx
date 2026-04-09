import React from "react";

const CartItem = ({ item, onRemove, onQuantityChange }) => {
  return (
    <li style={{ marginBottom: "16px", borderBottom: "1px solid #b56868", paddingBottom: "12px" }}>
      <p><strong>{item.food_item}</strong></p>
      {item.description && <p>{item.description}</p>}
      <p>Price: ${Number(item.unit_price).toFixed(2)}</p>
      <label>
        Quantity:
        <input
          type="number"
          min="1"
          value={item.quantity}
          onChange={(e) =>
            onQuantityChange(item.food_item, item.restaurant_id, Number(e.target.value))
          }
          style={{ marginLeft: "8px", width: "60px" }}
        />
      </label>
      <p>Item Total: ${(Number(item.unit_price) * item.quantity).toFixed(2)}</p>
      <button onClick={() => onRemove(item.food_item, item.restaurant_id)}>
        Remove
      </button>
    </li>
  );
};

export default CartItem;