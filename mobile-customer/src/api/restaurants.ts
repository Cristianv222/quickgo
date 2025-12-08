// src/api/restaurants.ts
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
  // Campos adicionales
  email?: string;
  latitude?: number;
  longitude?: number;
  cuisine_type_display?: string;
  delivery_time_range?: string;
  free_delivery_above?: number;
  has_promotion?: boolean;
  promotion_text?: string;
  accepts_cash?: boolean;
  accepts_card?: boolean;
  has_parking?: boolean;
  has_wifi?: boolean;
  is_eco_friendly?: boolean;
}

export interface RestaurantReview {
  id: number;
  restaurant: number;
  customer: {
    id: number;
    first_name: string;
    last_name: string;
    avatar?: string;
  };
  rating: number;
  comment: string;
  food_quality: number;
  delivery_time: number;
  packaging: number;
  restaurant_response?: string;
  response_date?: string;
  is_verified: boolean;
  created_at: string;
}

export interface MenuItem {
  id: number;
  restaurant: number;
  name: string;
  description: string;
  price: number;
  category: string;
  image?: string;
  is_available: boolean;
  is_vegetarian?: boolean;
  is_vegan?: boolean;
  is_gluten_free?: boolean;
  preparation_time?: number;
}

export const restaurantAPI = {
  /**
   * Obtiene todos los restaurantes
   */
  getAll: async (params?: any): Promise<Restaurant[]> => {
    const response = await api.get('/restaurants/', { params });
    return response.data;
  },

  /**
   * Obtiene un restaurante por ID
   */
  getById: async (id: number | string): Promise<Restaurant> => {
    const response = await api.get(`/restaurants/${id}/`);
    return response.data;
  },

  /**
   * Obtiene un restaurante por ID (alias de getById para compatibilidad)
   */
  getDetail: async (id: number | string): Promise<Restaurant> => {
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
  search: async (query: string, filters?: any): Promise<Restaurant[]> => {
    const response = await api.get('/restaurants/search/', {
      params: { q: query, ...filters },
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

  /**
   * Obtiene el menú de un restaurante
   */
  getMenu: async (restaurantId: number | string): Promise<MenuItem[]> => {
    const response = await api.get(`/restaurants/${restaurantId}/menu/`);
    return response.data;
  },

  /**
   * Obtiene las reseñas de un restaurante
   */
  getReviews: async (
    restaurantId: number | string,
    page: number = 1
  ): Promise<{ results: RestaurantReview[]; count: number; next: string | null; previous: string | null }> => {
    const response = await api.get(`/restaurants/${restaurantId}/reviews/`, {
      params: { page },
    });
    return response.data;
  },

  /**
   * Crea una reseña para un restaurante
   */
  createReview: async (
    restaurantId: number | string,
    reviewData: {
      rating: number;
      comment: string;
      food_quality: number;
      delivery_time: number;
      packaging: number;
      order_id?: number;
    }
  ): Promise<RestaurantReview> => {
    const response = await api.post(
      `/restaurants/${restaurantId}/reviews/`,
      reviewData
    );
    return response.data;
  },

  /**
   * Actualiza una reseña
   */
  updateReview: async (
    restaurantId: number | string,
    reviewId: number,
    reviewData: Partial<{
      rating: number;
      comment: string;
      food_quality: number;
      delivery_time: number;
      packaging: number;
    }>
  ): Promise<RestaurantReview> => {
    const response = await api.patch(
      `/restaurants/${restaurantId}/reviews/${reviewId}/`,
      reviewData
    );
    return response.data;
  },

  /**
   * Elimina una reseña
   */
  deleteReview: async (restaurantId: number | string, reviewId: number): Promise<void> => {
    await api.delete(`/restaurants/${restaurantId}/reviews/${reviewId}/`);
  },

  /**
   * Obtiene horarios de un restaurante
   */
  getSchedule: async (restaurantId: number | string): Promise<any> => {
    const response = await api.get(`/restaurants/${restaurantId}/schedule/`);
    return response.data;
  },

  /**
   * Verifica si el restaurante hace entregas en una ubicación
   */
  checkDeliveryAvailability: async (
    restaurantId: number | string,
    latitude: number,
    longitude: number
  ): Promise<{ available: boolean; distance?: number; message?: string }> => {
    const response = await api.get(`/restaurants/${restaurantId}/check-delivery/`, {
      params: { latitude, longitude },
    });
    return response.data;
  },

  /**
   * Obtiene restaurantes por filtros múltiples
   */
  filter: async (filters: {
    cuisine_type?: string;
    is_open?: boolean;
    is_featured?: boolean;
    min_rating?: number;
    max_delivery_fee?: number;
    accepts_card?: boolean;
    has_promotion?: boolean;
    search?: string;
  }): Promise<Restaurant[]> => {
    const response = await api.get('/restaurants/', {
      params: filters,
    });
    return response.data;
  },
};