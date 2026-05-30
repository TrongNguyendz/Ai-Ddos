import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

export const getAlerts = async (params) => {
  const response = await axios.get(`${API_BASE_URL}/alerts`, { params });
  return response.data;
};

export const toggleBlock = async (id) => {
  const response = await axios.post(`${API_BASE_URL}/alerts/${id}/toggle-block`);
  return response.data;
};