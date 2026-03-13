import axios from 'axios'

const API = axios.create({
  baseURL: (window as any).__API_URL__ || 'http://localhost:8000/api/v1',
})

API.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default API
