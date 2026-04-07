const CART_KEY = "cart";

export const getCart = () => {
  const cart = localStorage.getItem(CART_KEY);
  return cart ? JSON.parse(cart) : [];
};

export const saveCart = (cart) => {
  localStorage.setItem(CART_KEY, JSON.stringify(cart));
};

export const addToCart = (item) => {
  const cart = getCart();
  const existingItem = cart.find(
    (cartItem) => cartItem.food_item === item.food_item && cartItem.restaurant_id === item.restaurant_id
  );
  if (existingItem) {
    existingItem.quantity += 1;
  } else {
    cart.push({
      ...item,
      quantity: 1,
    });
  }
  saveCart(cart);
};

export const removeFromCart = (food_item, restaurant_id) => {
  const cart = getCart().filter(
    (item) => !(item.food_item === food_item && item.restaurant_id === restaurant_id)
  );
  saveCart(cart);
};

export const updateQuantity = (food_item, restaurant_id, quantity) => {
  const cart = getCart().map(
    (item) => item.food_item === food_item && item.restaurant_id === restaurant_id ? { ...item, quantity: Math.max(1, quantity) } : item
  );

  saveCart(cart);
};

export const clearCart = () => {
  localStorage.removeItem(CART_KEY);
};

export const getCartSubtotal = () => {
  const cart = getCart();
  return cart.reduce((sum, item) => sum + item.unit_price * item.quantity, 0);
};