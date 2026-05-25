import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

export const getTotalFlows = async (params) => {
  const response = await axios.get(`${API_BASE_URL}/dashboard/stats`, { params });
  return response.data;
};

export const getpkrate = async (params) => {
  const response = await axios.get(`${API_BASE_URL}/dashboard/charts/pktrate-kbps`, { params });
  return response.data;
}

export const getnormal_attack = async (params) => {
  const response = await axios.get(`${API_BASE_URL}/dashboard/charts/normal-attack`, { params });
  return response.data;
}