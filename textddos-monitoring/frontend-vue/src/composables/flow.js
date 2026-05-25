import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

export const getFlows = async (params) => {
  const response = await axios.get(`${API_BASE_URL}/flows`, { params });
  return response.data;
};


