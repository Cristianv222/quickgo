import api from './index';

// Tipos TypeScript
export interface Restaurant {
  id: number;
  slug: string;
  name: string;
  logo: string | null;
  cuisine_type: string;
  cuisine_name: string;
  rating: number;
  total_reviews: number;
  delivery_time_min: number;
  delivery_time_max: number;
  delivery_fee: number;
  min_order_amount: number;
  free_delivery_above: number | null;
  is_open: boolean;
  is_open_now: boolean;
  is_accepting_orders: boolean;
  is_featured: boolean;
  is_new: boolean;
  has_promotion: boolean;
  promotion_text: string;
  distance: number | null;
}

export interface RestaurantDetail extends Restaurant {
  description: string;
  banner: string | null;
  phone: string;
  email: string;
  address: string;
  address_reference: string;
  latitude: number;
  longitude: number;
  delivery_radius_km: number;
  accepts_cash: boolean;
  accepts_card: boolean;
  has_parking: boolean;
  has_wifi: boolean;
  is_eco_friendly: boolean;
  schedules: Schedule[];
  gallery: GalleryImage[];
  recent_reviews: Review[];
  average_ratings: {
    food_quality: number;
    delivery_time: number;
    packaging: number;
  } | null;
  created_at: string;
}

export interface Schedule {
  id: number;
  day_of_week: number;
  day_name: string;
  opening_time: string;
  closing_time: string;
  is_closed: boolean;
}

export interface GalleryImage {
  id: number;
  image: string;
  caption: string;
  is_featured: boolean;
  order: number;
}

export interface Review {
  id: number;
  customer_name: string;
  customer_avatar: string | null;
  rating: number;
  comment: string;
  food_quality: number;
  delivery_time: number;
  packaging: number;
  restaurant_response: string;
  response_date: string | null;
  created_at: string;
}

export interface ReviewStatistics {
  average_rating: number;
  average_food_quality: number;
  average_delivery_time: number;
  average_packaging: number;
  total_reviews: number;
}

// API Functions
export const restaurantAPI = {
  /**
   * Obtiene todos los restaurantes con filtros opcionales
   * @param params - Parámetros de filtrado y ubicación
   */
  getAll: async (params?: {
    latitude?: number;
    longitude?: number;
    cuisine_type?: string;
    is_open?: boolean;
    min_rating?: number;
    max_delivery_fee?: number;
    search?: string;
  }) => {
    const response = await api.get<Restaurant[]>('/restaurants/', { params });
    return response.data;
  },

  /**
   * Obtiene restaurantes cercanos ordenados por distancia
   * @param latitude - Latitud del usuario
   * @param longitude - Longitud del usuario
   * @param radius - Radio de búsqueda en km (default: 5)
   */
  getNearby: async (latitude: number, longitude: number, radius: number = 5) => {
    const response = await api.get<Restaurant[]>('/restaurants/nearby/', {
      params: { latitude, longitude, radius },
    });
    return response.data;
  },

  /**
   * Obtiene detalle completo de un restaurante
   * @param id - ID del restaurante
   * @param latitude - Latitud del usuario (opcional, para calcular distancia)
   * @param longitude - Longitud del usuario (opcional)
   */
  getDetail: async (id: number, latitude?: number, longitude?: number) => {
    const response = await api.get<RestaurantDetail>(`/restaurants/${id}/`, {
      params: { latitude, longitude },
    });
    return response.data;
  },

  /**
   * Obtiene restaurantes destacados
   */
  getFeatured: async () => {
    const response = await api.get<Restaurant[]>('/restaurants/featured/');
    return response.data;
  },

  /**
   * Busca restaurantes por nombre, descripción o tipo de cocina
   * @param query - Término de búsqueda (mínimo 2 caracteres)
   * @param filters - Filtros adicionales opcionales
   */
  search: async (query: string, filters?: {
    cuisine_type?: string;
    min_rating?: number;
    is_open?: boolean;
  }) => {
    const response = await api.get<Restaurant[]>('/restaurants/search/', {
      params: { q: query, ...filters },
    });
    return response.data;
  },

  /**
   * Obtiene todas las reseñas de un restaurante con estadísticas
   * @param restaurantId - ID del restaurante
   */
  getReviews: async (restaurantId: number) => {
    const response = await api.get<{
      reviews: Review[];
      statistics: ReviewStatistics;
    }>(`/restaurant-reviews/restaurant/${restaurantId}/`);
    return response.data;
  },

  /**
   * Crea una reseña para un restaurante (requiere autenticación)
   * @param data - Datos de la reseña
   */
  createReview: async (data: {
    restaurant: number;
    rating: number;
    comment: string;
    food_quality: number;
    delivery_time: number;
    packaging: number;
    order?: number;
  }) => {
    const response = await api.post<Review>('/restaurant-reviews/', data);
    return response.data;
  },
};