import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';
const AUTH_TOKEN_KEY = 'authToken';

axios.defaults.baseURL = API_BASE_URL;

export const createHoneypot = async (purpose: string) => {
  const response = await axios.post('/honeytrap/create', { purpose });
  return response.data;
};

export const getHoneypots = async () => {
  const response = await axios.get('/honeytrap/list');
  return response.data;
};