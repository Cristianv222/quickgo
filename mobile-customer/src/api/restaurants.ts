import api from './index';

export interface Restaurant {
  id: number;
  name: string;
  description: string;
  cuisine_type: string;
  rating: number;
  total_reviews: number;
  delivery_time_min: number;
  delivery_time_max: number;
  delivery_fee: number;
  min_order_amount: number;
  is_open: boolean;
  is_accepting_orders: boolean;
  is_featured: boolean;
  logo?: string;
  banner?: string;
  address: string;
  phone: string;
  distance?: number;
}

export const restaurantAPI = {
  /**
   * Obtiene todos los restaurantes
   */
  getAll: async (): Promise<Restaurant[]> => {
    const response = await api.get('/restaurants/');
    return response.data;
  },

  /**
   * Obtiene un restaurante por ID
   */
  getById: async (id: number): Promise<Restaurant> => {
    const response = await api.get(`/restaurants/${id}/`);
    return response.data;
  },

  /**
   * Obtiene restaurantes cercanos
   */
  getNearby: async (
    latitude: number,
    longitude: number,
    radius: number = 5
  ): Promise<Restaurant[]> => {
    const response = await api.get('/restaurants/nearby/', {
      params: { latitude, longitude, radius },
    });
    return response.data;
  },

  /**
   * Obtiene restaurantes destacados
   */
  getFeatured: async (): Promise<Restaurant[]> => {
    const response = await api.get('/restaurants/featured/');
    return response.data;
  },

  /**
   * Busca restaurantes
   */
  search: async (query: string): Promise<Restaurant[]> => {
    const response = await api.get('/restaurants/search/', {
      params: { q: query },
    });
    return response.data;
  },

  /**
   * Filtra restaurantes por tipo de cocina
   */
  getByCuisineType: async (cuisineType: string): Promise<Restaurant[]> => {
    const response = await api.get('/restaurants/', {
      params: { cuisine_type: cuisineType },
    });
    return response.data;
  },

  /**
   * Obtiene restaurantes abiertos
   */
  getOpen: async (): Promise<Restaurant[]> => {
    const response = await api.get('/restaurants/', {
      params: { is_open: 'true' },
    });
    return response.data;
  },
};