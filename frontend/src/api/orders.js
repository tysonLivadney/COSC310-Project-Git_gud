import api from '../api';

export const getOrders = async (customerId) => {
  const response = await api.get('/orders', {
    params: { customer_id: customerId }
  });
  return response.data;
};

export const getOrderById = async (orderId) => {
  const response = await api.get(`/orders/${orderId}`);
  return response.data;
};

export const getDistance = async (userId, restaurantId) => {
  const response = await api.get(`/location/users/${userId}/restaurants/${restaurantId}/distance`);
  return response.data;
};

export const getOrderTotal = async (orderId, province, distanceKm) => {
  const response = await api.get(`/orders/${orderId}/total`, {
    params: { province, distance_km: distanceKm }
  });
  return response.data;
};

export const cancelOrder = async (orderId) => {
  await api.delete(`/orders/${orderId}`);
};