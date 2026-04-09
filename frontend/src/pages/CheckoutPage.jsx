import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import OrderSummary from "../components/Restaurants/checkout/OrderSummary.jsx";
import PaymentForm from "../components/Restaurants/checkout/PaymentForm.jsx";
import PromoCodeInput from "../components/PromoCodeInput.jsx";
import { getCart, clearCart } from "../utils/cartUtils.js";
import api from "../api.js";

const CheckoutPage = () => {
  const [cartItems, setCartItems] = useState([]);
  const [order, setOrder] = useState(null);
  const [orderTotal, setOrderTotal] = useState(null);
  const [deliveryAddress, setDeliveryAddress] = useState("");
  const [currentUser, setCurrentUser] = useState(null);
  const [isGuest, setIsGuest] = useState(true);
  const [authChecking, setAuthChecking] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [appliedPromo, setAppliedPromo] = useState(null);

  const navigate = useNavigate();

  const detectUserState = async () => {
    const token = localStorage.getItem("token");

    if (!token) {
      setCurrentUser(null);
      setIsGuest(true);
      setAuthChecking(false);
      return;
    }

    try {
      const response = await api.get("/auth/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = response.data;
      setCurrentUser(data);
      setIsGuest(false);

      if (data?.address) {
        setDeliveryAddress(data.address);
      }
    } catch (err) {
      console.error("detectUserState failed:", err);
      setCurrentUser(null);
      setIsGuest(true);
    } finally {
      setAuthChecking(false);
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

      const orderResponse = await api.post("/orders", orderPayload);
      const orderData = orderResponse.data;

      setOrder(orderData);

      const totalResponse = await api.get(`/orders/${orderData.id}/total`, {
        params: {
          province: "BC",
          distance_km: 1,
        },
      });

      setOrderTotal(totalResponse.data);
    } catch (err) {
      console.error("prepare checkout failed:", err);
      setError(
        err?.response?.data?.detail || err.message || "Could not prepare checkout."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmOrder = async (paymentInfo) => {
    if (loading || !order) return;

    try {
      setLoading(true);
      setError("");

      const confirmPayload = { payment_info: paymentInfo };
      if (appliedPromo) confirmPayload.promo_code = appliedPromo.code;

      const response = await api.post(`/orders/${order.id}/confirm`, confirmPayload);

      const result = response.data;

      clearCart();

      navigate("/success", {
        state: {
          orderId: result?.order_id || order.id,
          total: result?.total || orderTotal?.total,
          status: result?.status || "confirmed",
          promoCode: appliedPromo?.code || null,
          discount: result?.discount || null,
        },
      });
    } catch (err) {
      console.error("confirm order failed:", err);

      const result = err?.response?.data;
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
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Checkout</h2>

      {authChecking ? (
        <div>
          <p>Checking your account...</p>
        </div>
      ) : isGuest ? (
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

              <button onClick={handlePrepareCheckout} disabled={loading || authChecking}>
                {loading ? "Preparing..." : "Prepare Checkout"}
              </button>
            </div>
          )}

          {orderTotal && (
            <div>
              <OrderSummary orderTotal={orderTotal} discount={appliedPromo ? (
                appliedPromo.discount_type === 'percentage'
                  ? (Number(orderTotal.subtotal) * appliedPromo.discount_value / 100)
                  : appliedPromo.discount_value
              ) : 0} />
              <div style={{ margin: '16px 0' }}>
                <label>Promo Code</label>
                <PromoCodeInput
                  orderSubtotal={Number(orderTotal.subtotal) || 0}
                  onApply={(promo) => setAppliedPromo(promo)}
                  onRemove={() => setAppliedPromo(null)}
                />
              </div>
              <PaymentForm onSubmit={handleConfirmOrder} loading={loading} />
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default CheckoutPage;