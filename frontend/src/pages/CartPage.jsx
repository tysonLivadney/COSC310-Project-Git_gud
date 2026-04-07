import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import CartItem from "../components/Restaurants/cart/CartItem.jsx";
import {
  getCart,
  removeFromCart,
  updateQuantity,
  getCartSubtotal,
} from "../utils/cartUtils.js";

const CartPage = () => {
  const [cartItems, setCartItems] = useState([]);
  const navigate = useNavigate();
  const loadCart = () => {
    setCartItems(getCart());
  };
  useEffect(() => {
    loadCart();
  }, []);
  const handleRemove = (food_item, restaurant_id) => {
    removeFromCart(food_item, restaurant_id);
    loadCart();
  };
  const handleQuantityChange = (food_item, restaurant_id, quantity) => {
    updateQuantity(food_item, restaurant_id, quantity);
    loadCart();
  };

  const handleCheckout = () => {
    if (cartItems.length === 0) {
      alert("Your cart is empty.");
      return;
    }
    const firstRestaurantId = cartItems[0].restaurant_id;
    const mixedRestaurant = cartItems.some(
      (item) => item.restaurant_id !== firstRestaurantId
    );
    if (mixedRestaurant) {
      alert("Please order from one restaurant at a time.");
      return;
    }
    navigate("/checkout");
  };

  const subtotal = getCartSubtotal(cartItems);

  return (
    <div>
      <h2>Your Cart</h2>
      {cartItems.length === 0 ? (
        <p>Your cart is empty.</p>
      ) : (
        <div>
          <ul style={{ listStyle: "none", padding: 0 }}>
            {cartItems.map((item, index) => (
              <CartItem
                key={`${item.food_item}-${item.restaurant_id}-${index}`}
                item={item}
                onRemove={handleRemove}
                onQuantityChange={handleQuantityChange}
              />
            ))}
          </ul>
          <h3>Subtotal: ${subtotal.toFixed(2)}</h3>
          <button onClick={handleCheckout}>Proceed to Checkout</button>
        </div>
      )}
    </div>
  );
};
export default CartPage;