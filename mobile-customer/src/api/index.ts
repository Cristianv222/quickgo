import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// URL del backend - Cambiar por tu IP local si usas teléfono físico
// Para emulador/navegador usa localhost
const API_URL = 'http://192.168.1.25:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

// Interceptor para agregar token (solo si existe y es válido)
api.interceptors.request.use(
  async (config) => {
    try {
      const token = await AsyncStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.log('Error obteniendo token:', error);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores 401 (token expirado)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido - limpiar storage
      try {
        await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
      } catch (e) {
        console.log('Error limpiando tokens:', e);
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: async (userData: any) => {
    const response = await api.post('/auth/register/customer/', userData);
    if (response.data.tokens) {
      await AsyncStorage.setItem('access_token', response.data.tokens.access);
      await AsyncStorage.setItem('refresh_token', response.data.tokens.refresh);
      await AsyncStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login/', { email, password });
    if (response.data.tokens) {
      await AsyncStorage.setItem('access_token', response.data.tokens.access);
      await AsyncStorage.setItem('refresh_token', response.data.tokens.refresh);
      await AsyncStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  logout: async () => {
    await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
  },

  getCurrentUser: async () => {
    const userStr = await AsyncStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
};

export const userAPI = {
  getProfile: async () => {
    const response = await api.get('/auth/profile/'); // ⚠️ TAMBIÉN CORREGIDO
    return response.data;
  },

  updateProfile: async (data: any) => {
    const response = await api.put('/auth/profile/update/', data); // ⚠️ TAMBIÉN CORREGIDO
    return response.data;
  },
};

export default api;