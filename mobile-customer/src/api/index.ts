import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// URL del backend - Configurar según tu entorno:
// - Web/Expo Go en navegador: 'http://localhost:8000/api'
// - Emulador Android: 'http://10.0.2.2:8000/api'
// - Emulador iOS: 'http://localhost:8000/api'
// - Dispositivo físico: 'http://TU_IP_LOCAL:8000/api' ← USANDO ESTA
const API_URL = 'http://192.168.1.25:8000/api';

// Debug: Mostrar la URL que se está usando
console.log('🌐 API URL configurada:', API_URL);

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000, // 30 segundos para conexiones móviles
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

// Interceptor para manejar errores
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Debug: Mostrar detalles del error
    console.error('❌ Error de API:', {
      message: error.message,
      code: error.code,
      url: error.config?.url,
      baseURL: error.config?.baseURL,
      status: error.response?.status,
    });

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