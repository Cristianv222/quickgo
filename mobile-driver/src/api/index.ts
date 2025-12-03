import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// URL del backend - Cambia esta IP por la tuya
const API_URL = 'http://192.168.1.2:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

// ============================================
// INTERCEPTOR PARA AGREGAR TOKEN
// ============================================
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores de respuesta
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si el error es 401 y no hemos intentado refresh aún
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = await AsyncStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          await AsyncStorage.setItem('access_token', access);

          // Reintentar la petición original con el nuevo token
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Si el refresh falla, limpiar tokens y redirigir al login
        await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error.response?.data || error.message);
  }
);

// ============================================
// AUTH API - Autenticación
// ============================================
export const authAPI = {
  /**
   * Registrar nuevo usuario (cliente o repartidor)
   */
  register: async (userData: {
    first_name: string;
    last_name: string;
    email: string;
    phone: string;
    password: string;
    password2: string;
    user_type: 'CUSTOMER' | 'DRIVER';
    // Campos adicionales para repartidores
    vehicle_type?: 'BIKE' | 'MOTORCYCLE' | 'CAR';
    vehicle_plate?: string;
    vehicle_brand?: string;
    vehicle_model?: string;
    vehicle_color?: string;
    license_number?: string;
  }) => {
    const endpoint = userData.user_type === 'DRIVER' 
      ? '/auth/register/driver/'
      : '/auth/register/customer/';
    
    const response = await api.post(endpoint, userData);
    
    if (response.data.tokens) {
      await AsyncStorage.setItem('access_token', response.data.tokens.access);
      await AsyncStorage.setItem('refresh_token', response.data.tokens.refresh);
      await AsyncStorage.setItem('user', JSON.stringify(response.data.user));
    }
    
    return response.data;
  },

  /**
   * Iniciar sesión
   */
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login/', { email, password });
    
    if (response.data.tokens) {
      await AsyncStorage.setItem('access_token', response.data.tokens.access);
      await AsyncStorage.setItem('refresh_token', response.data.tokens.refresh);
      await AsyncStorage.setItem('user', JSON.stringify(response.data.user));
    }
    
    return response.data;
  },

  /**
   * Cerrar sesión
   */
  logout: async () => {
    try {
      const refreshToken = await AsyncStorage.getItem('refresh_token');
      if (refreshToken) {
        await api.post('/auth/logout/', { refresh: refreshToken });
      }
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    } finally {
      await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
    }
  },

  /**
   * Obtener usuario actual desde AsyncStorage
   */
  getCurrentUser: async () => {
    const userStr = await AsyncStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  /**
   * Refrescar token
   */
  refreshToken: async () => {
    const refreshToken = await AsyncStorage.getItem('refresh_token');
    if (!refreshToken) throw new Error('No refresh token available');

    const response = await api.post('/auth/token/refresh/', {
      refresh: refreshToken,
    });

    await AsyncStorage.setItem('access_token', response.data.access);
    return response.data;
  },
};

// ============================================
// DRIVER API - Específico para Repartidores
// ============================================
export const driverAPI = {
  /**
   * Obtener perfil del repartidor
   */
  getProfile: async () => {
    const response = await api.get('/auth/driver/profile/');
    return response.data;
  },

  /**
   * Actualizar perfil del repartidor
   */
  updateProfile: async (data: {
    first_name?: string;
    last_name?: string;
    phone?: string;
    avatar?: any;
  }) => {
    const response = await api.put('/auth/driver/profile/update/', data);
    return response.data;
  },

  /**
   * Actualizar información del vehículo
   */
  updateVehicle: async (vehicleData: {
    vehicle_type?: 'BIKE' | 'MOTORCYCLE' | 'CAR';
    vehicle_plate?: string;
    vehicle_brand?: string;
    vehicle_model?: string;
    vehicle_color?: string;
  }) => {
    const response = await api.put('/deliveries/driver/vehicle/update/', vehicleData);
    return response.data;
  },

  /**
   * Actualizar disponibilidad
   */
  updateAvailability: async (isAvailable: boolean) => {
    const response = await api.post('/deliveries/driver/availability/', {
      is_available: isAvailable,
    });
    return response.data;
  },

  /**
   * Actualizar estado online/offline
   */
  updateOnlineStatus: async (isOnline: boolean) => {
    const response = await api.post('/deliveries/driver/online-status/', {
      is_online: isOnline,
    });
    return response.data;
  },

  /**
   * Actualizar ubicación del repartidor
   */
  updateLocation: async (latitude: number, longitude: number) => {
    const response = await api.post('/deliveries/driver/location/update/', {
      latitude,
      longitude,
    });
    return response.data;
  },

  /**
   * Obtener estadísticas del repartidor
   */
  getStatistics: async () => {
    const response = await api.get('/deliveries/driver/statistics/');
    return response.data;
  },

  /**
   * Subir documentos (licencia, foto del vehículo, cédula)
   */
  uploadDocuments: async (documents: FormData) => {
    const response = await api.post('/auth/driver/documents/upload/', documents, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// ============================================
// DELIVERY API - Gestión de Entregas
// ============================================
export const deliveryAPI = {
  /**
   * Obtener entregas disponibles (pendientes de aceptar)
   */
  getAvailableDeliveries: async () => {
    const response = await api.get('/deliveries/available/');
    return response.data;
  },

  /**
   * Obtener entregas activas del repartidor
   */
  getActiveDeliveries: async () => {
    const response = await api.get('/deliveries/driver/active/');
    return response.data;
  },

  /**
   * Obtener historial de entregas
   */
  getDeliveryHistory: async (page = 1) => {
    const response = await api.get(`/deliveries/driver/history/?page=${page}`);
    return response.data;
  },

  /**
   * Obtener detalles de una entrega específica
   */
  getDeliveryDetails: async (deliveryId: number) => {
    const response = await api.get(`/deliveries/${deliveryId}/`);
    return response.data;
  },

  /**
   * Aceptar una entrega
   */
  acceptDelivery: async (deliveryId: number) => {
    const response = await api.post(`/deliveries/${deliveryId}/accept/`);
    return response.data;
  },

  /**
   * Rechazar una entrega
   */
  rejectDelivery: async (deliveryId: number, reason?: string) => {
    const response = await api.post(`/deliveries/${deliveryId}/reject/`, { reason });
    return response.data;
  },

  /**
   * Marcar entrega como recogida del restaurante
   */
  markAsPickedUp: async (deliveryId: number) => {
    const response = await api.post(`/deliveries/${deliveryId}/picked-up/`);
    return response.data;
  },

  /**
   * Marcar entrega como en camino al cliente
   */
  markAsInTransit: async (deliveryId: number) => {
    const response = await api.post(`/deliveries/${deliveryId}/in-transit/`);
    return response.data;
  },

  /**
   * Completar entrega
   */
  completeDelivery: async (deliveryId: number, data?: {
    delivery_code?: string;
    signature?: string;
    photo?: any;
  }) => {
    const response = await api.post(`/deliveries/${deliveryId}/complete/`, data);
    return response.data;
  },

  /**
   * Reportar problema con la entrega
   */
  reportProblem: async (deliveryId: number, problem: {
    type: string;
    description: string;
    photos?: any[];
  }) => {
    const response = await api.post(`/deliveries/${deliveryId}/report-problem/`, problem);
    return response.data;
  },
};

// ============================================
// EARNINGS API - Ganancias
// ============================================
export const earningsAPI = {
  /**
   * Obtener resumen de ganancias
   */
  getSummary: async () => {
    const response = await api.get('/deliveries/driver/earnings/summary/');
    return response.data;
  },

  /**
   * Obtener ganancias por período
   */
  getByPeriod: async (startDate: string, endDate: string) => {
    const response = await api.get('/deliveries/driver/earnings/period/', {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data;
  },

  /**
   * Obtener historial de pagos
   */
  getPaymentHistory: async (page = 1) => {
    const response = await api.get(`/payments/driver/history/?page=${page}`);
    return response.data;
  },

  /**
   * Solicitar retiro de ganancias
   */
  requestWithdrawal: async (amount: number, bankAccount: string) => {
    const response = await api.post('/payments/driver/withdrawal/request/', {
      amount,
      bank_account: bankAccount,
    });
    return response.data;
  },
};

// ============================================
// NOTIFICATION API - Notificaciones
// ============================================
export const notificationAPI = {
  /**
   * Obtener notificaciones
   */
  getNotifications: async (page = 1) => {
    const response = await api.get(`/notifications/?page=${page}`);
    return response.data;
  },

  /**
   * Marcar notificación como leída
   */
  markAsRead: async (notificationId: number) => {
    const response = await api.post(`/notifications/${notificationId}/mark-as-read/`);
    return response.data;
  },

  /**
   * Marcar todas las notificaciones como leídas
   */
  markAllAsRead: async () => {
    const response = await api.post('/notifications/mark-all-as-read/');
    return response.data;
  },

  /**
   * Eliminar notificación
   */
  deleteNotification: async (notificationId: number) => {
    const response = await api.delete(`/notifications/${notificationId}/`);
    return response.data;
  },

  /**
   * Actualizar token de notificaciones push
   */
  updatePushToken: async (token: string) => {
    const response = await api.post('/notifications/push-token/update/', {
      push_token: token,
    });
    return response.data;
  },
};

// ============================================
// RATING API - Calificaciones
// ============================================
export const ratingAPI = {
  /**
   * Obtener calificaciones recibidas
   */
  getMyRatings: async (page = 1) => {
    const response = await api.get(`/deliveries/driver/ratings/?page=${page}`);
    return response.data;
  },

  /**
   * Calificar a un cliente
   */
  rateCustomer: async (orderId: number, rating: number, comment?: string) => {
    const response = await api.post(`/orders/${orderId}/rate-customer/`, {
      rating,
      comment,
    });
    return response.data;
  },
};

// ============================================
// SUPPORT API - Soporte
// ============================================
export const supportAPI = {
  /**
   * Enviar mensaje de soporte
   */
  sendMessage: async (subject: string, message: string) => {
    const response = await api.post('/support/messages/', {
      subject,
      message,
    });
    return response.data;
  },

  /**
   * Obtener mensajes de soporte
   */
  getMessages: async () => {
    const response = await api.get('/support/messages/');
    return response.data;
  },

  /**
   * Obtener preguntas frecuentes
   */
  getFAQ: async () => {
    const response = await api.get('/support/faq/');
    return response.data;
  },
};

export default api;