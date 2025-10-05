// src/api/lib

import axios from 'axios';

const axiosClient = axios.create({
  baseURL: process.env.AI_BACKEND_URL,
  headers: {
    'Content-type': 'application/json',
  },
});

export default axiosClient;
