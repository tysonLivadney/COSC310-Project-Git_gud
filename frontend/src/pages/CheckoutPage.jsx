import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import OrderSummary from "../components/Restaurants/checkout/OrderSummary.jsx";
import PaymentForm from "../components/Restaurants/checkout/PaymentForm.jsx";
import { getCart, clearCart } from "../utils/cartUtils.js";

const CheckoutPage = () => {
  const [cartItems, setCartItems] = useState([]);
  const [order, setOrder] = useState(null);
  const [orderTotal, setOrderTotal] = useState(null);
  const [deliveryAddress, setDeliveryAddress] = useState("");
  const [currentUser, setCurrentUser] = useState(null);
  const [isGuest, setIsGuest] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const detectUserState = async () => {
    const token = localStorage.getItem("token");

    if (!token) {
      setCurrentUser(null);
      setIsGuest(true);
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/auth/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        setCurrentUser(null);
        setIsGuest(true);
        return;
      }

      const data = await response.json();
      setCurrentUser(data);
      setIsGuest(false);

      if (data.address) {
        setDeliveryAddress(data.address);
      }
    } catch {
      setCurrentUser(null);
      setIsGuest(true);
    }
  };

  useEffect(() => {
    setCartItems(getCart());
    detectUserState();
  }, []);

  const getCustomerId = () => {
    if (currentUser?.id) {
      return String(currentUser.id);
    }
    return `guest-${Date.now()}`;
  };

  const handlePrepareCheckout = async () => {
    if (loading) return;

    if (cartItems.length === 0) {
      setError("Your cart is empty.");
      return;
    }

    const firstRestaurantId = cartItems[0].restaurant_id;
    const mixedRestaurant = cartItems.some(
      (item) => item.restaurant_id !== firstRestaurantId
    );

    if (mixedRestaurant) {
      setError("Please order from one restaurant at a time.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const orderPayload = {
        restaurant_id: String(firstRestaurantId),
        customer_id: getCustomerId(),
        delivery_address: deliveryAddress.trim() || null,
        items: cartItems.map((item) => ({
          food_item: item.food_item,
          quantity: item.quantity,
          unit_price: item.unit_price,
        })),
      };

      const orderResponse = await fetch("http://localhost:8000/orders", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(orderPayload),
      });

      const orderData = await orderResponse.json().catch(() => null);

      if (!orderResponse.ok) {
        throw new Error(orderData?.detail || "Failed to create order.");
      }

      setOrder(orderData);

      const totalResponse = await fetch(
        `http://localhost:8000/orders/${orderData.id}/total?province=BC&distance_km=1`
      );

      const totalData = await totalResponse.json().catch(() => null);

      if (!totalResponse.ok) {
        throw new Error(totalData?.detail || "Failed to load order total.");
      }

      setOrderTotal(totalData);
    } catch (err) {
      setError(err.message || "Could not prepare checkout.");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmOrder = async (paymentInfo) => {
    if (loading || !order) return;

    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        `http://localhost:8000/orders/${order.id}/confirm`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ payment_info: paymentInfo }),
        }
      );

      const result = await response.json().catch(() => null);

      if (!response.ok) {
        let apiMessage = "Payment failed or order confirmation failed.";

        if (Array.isArray(result?.detail) && result.detail.length > 0) {
          const item = result.detail[0];
          const field = item?.loc?.[item.loc.length - 1];

          if (field === "expiry") {
            apiMessage = "Expiry should have 5 characters";
          } else if (field === "cvv") {
            apiMessage = "CVV should have 3 or 4 characters";
          } else if (field === "card_number") {
            apiMessage = "Card number should have 13 to 19 digits";
          } else if (typeof item?.msg === "string") {
            apiMessage = item.msg;
          }
        } else if (typeof result?.detail === "string") {
          apiMessage = result.detail;
        }

        setError(apiMessage);
        return;
      }

      clearCart();

      navigate("/success", {
        state: {
          orderId: result?.order_id || order.id,
          total: result?.total || orderTotal?.total,
          status: result?.status || "confirmed",
        },
      });
    } catch {
      setError("Could not connect to server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Checkout</h2>

      {isGuest ? (
        <div>
          <p><strong>Guest Checkout</strong></p>
          <p>
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </div>
      ) : (
        <div>
          <p><strong>Checking out as:</strong></p>
          <p>{currentUser?.name || currentUser?.email || "User"}</p>
        </div>
      )}

      {error && <p style={{ color: "red" }}>{error}</p>}

      {cartItems.length === 0 ? (
        <div>
          <p>Your cart is empty.</p>
          <Link to="/cart">Back to Cart</Link>
        </div>
      ) : (
        <>
          {!order && (
            <div>
              <label htmlFor="delivery_address">Delivery Address</label>
              <input
                id="delivery_address"
                type="text"
                value={deliveryAddress}
                onChange={(e) => setDeliveryAddress(e.target.value)}
                placeholder="Enter your delivery address"
              />

              <button onClick={handlePrepareCheckout} disabled={loading}>
                {loading ? "Preparing..." : "Prepare Checkout"}
              </button>
            </div>
          )}

          {orderTotal && (
            <div>
              <OrderSummary orderTotal={orderTotal} />
              <PaymentForm onSubmit={handleConfirmOrder} loading={loading} />
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default CheckoutPage;