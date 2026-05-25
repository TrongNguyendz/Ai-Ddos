import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

export const getRules = async (params) => {
  const response = await axios.get(`${API_BASE_URL}/rules`, { params });
  return response.data;
};

export const createRule = async (ruleData) => {
  const response = await axios.post(`${API_BASE_URL}/rules`, ruleData);
  return response.data;
};

export const updateRule = async (id, ruleData) => {
  const response = await axios.put(`${API_BASE_URL}/rules/${id}`, ruleData);
  return response.data;
};

export const deleteRule = async (id) => {
  const response = await axios.delete(`${API_BASE_URL}/rules/${id}`);
  return response.data;
};

export const toggleRule = async (rule_id) => {
  const response = await axios.post(`${API_BASE_URL}/rules/${rule_id}/toggle`);
  return response.data;
};
export const getRuleHistory = async (rule_id, params) => {
  const response = await axios.get(`${API_BASE_URL}/rules/history/${rule_id}`, { params });
  return response.data;
}
