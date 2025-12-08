// src/api/orders.ts
import api from './index';

export interface OrderItem {
    id?: number;
    product_id: number;
    product_name?: string;
    product_description?: string;
    product_image?: string;
    unit_price?: number;
    quantity: number;
    selected_extras?: Array<{
        id: number;
        name?: string;
        price?: string;
        quantity: number;
    }>;
    selected_options?: Array<{
        group_id: number;
        group?: string;
        option_id: number;
        option?: string;
        price_modifier?: string;
    }>;
    special_notes?: string;
    subtotal?: number;
    extras_total?: number;
    options_total?: number;
}

export interface Order {
    id: number;
    order_number: string;
    status: string;
    status_display: string;
    customer: number;
    customer_name: string;
    restaurant: number;
    restaurant_name: string;
    restaurant_logo?: string;
    driver?: number;
    driver_name?: string;
    delivery_address: string;
    delivery_reference?: string;
    delivery_latitude: number;
    delivery_longitude: number;
    delivery_distance?: number;
    subtotal: number;
    delivery_fee: number;
    service_fee: number;
    tax: number;
    discount: number;
    tip: number;
    total: number;
    total_items: number;
    payment_method: string;
    payment_method_display: string;
    is_paid: boolean;
    payment_date?: string;
    special_instructions?: string;
    coupon_code?: string;
    estimated_preparation_time?: number;
    estimated_delivery_time?: string;
    can_be_cancelled: boolean;
    can_be_rated: boolean;
    is_delayed: boolean;
    is_rated: boolean;
    created_at: string;
    updated_at: string;
    items?: OrderItem[];
    // Campos adicionales del detalle
    customer_phone?: string;
    customer_email?: string;
    restaurant_phone?: string;
    restaurant_address?: string;
    driver_phone?: string;
    driver_vehicle?: {
        type: string;
        plate: string;
        brand: string;
        model: string;
        color: string;
    };
    confirmed_at?: string;
    preparing_at?: string;
    ready_at?: string;
    picked_up_at?: string;
    delivered_at?: string;
    cancelled_at?: string;
    cancellation_reason?: string;
    cancellation_reason_display?: string;
    cancellation_notes?: string;
    status_history?: Array<{
        id: number;
        status: string;
        status_display: string;
        notes: string;
        changed_by_name: string;
        created_at: string;
    }>;
    rating?: OrderRating;
}

export interface OrderRating {
    id: number;
    order: number;
    overall_rating: number;
    food_rating: number;
    delivery_rating: number;
    driver_rating?: number;
    driver_comment?: string;
    comment: string;
    would_order_again: boolean;
    liked_aspects?: string[];
    disliked_aspects?: string[];
    created_at: string;
}

export interface CreateOrderData {
    restaurant_id: number;
    items: OrderItem[];
    delivery_address: string;
    delivery_reference?: string;
    delivery_latitude: number;
    delivery_longitude: number;
    payment_method: 'CASH' | 'CARD' | 'ONLINE';
    special_instructions?: string;
    coupon_code?: string;
    tip?: number;
}

export interface OrderStatistics {
    total_orders: number;
    active_orders: number;
    completed_orders: number;
    cancelled_orders: number;
    total_spent: number;
    average_order_value: number;
    favorite_restaurant?: {
        id: number;
        name: string;
        order_count: number;
    };
}

export const orderAPI = {
    /**
     * Crear una nueva orden
     */
    create: async (orderData: CreateOrderData): Promise<Order> => {
        const response = await api.post('/orders/', orderData);
        return response.data;
    },

    /**
     * Obtener todas las órdenes del usuario
     */
    getMyOrders: async (status?: string): Promise<Order[]> => {
        const params = status ? { status } : {};
        const response = await api.get('/orders/my_orders/', { params });
        return response.data;
    },

    /**
     * Obtener órdenes activas (no completadas ni canceladas)
     */
    getActiveOrders: async (): Promise<Order[]> => {
        const response = await api.get('/orders/active_orders/');
        return response.data;
    },

    /**
     * Obtener historial de órdenes (completadas y canceladas)
     */
    getOrderHistory: async (page: number = 1): Promise<{
        results: Order[];
        count: number;
        next: string | null;
        previous: string | null;
    }> => {
        const response = await api.get('/orders/order_history/', {
            params: { page },
        });
        return response.data;
    },

    /**
     * Obtener detalle de una orden
     */
    getById: async (orderId: number): Promise<Order> => {
        const response = await api.get(`/orders/${orderId}/`);
        return response.data;
    },

    /**
     * Actualizar una orden (solo campos permitidos)
     */
    update: async (
        orderId: number,
        data: {
            delivery_address?: string;
            delivery_reference?: string;
            special_instructions?: string;
            tip?: number;
        }
    ): Promise<Order> => {
        const response = await api.patch(`/orders/${orderId}/`, data);
        return response.data;
    },

    /**
     * Cancelar una orden
     */
    cancel: async (
        orderId: number,
        cancellationData: {
            cancellation_reason:
            | 'CUSTOMER_REQUEST'
            | 'RESTAURANT_UNAVAILABLE'
            | 'DRIVER_UNAVAILABLE'
            | 'PAYMENT_FAILED'
            | 'WRONG_ORDER'
            | 'LONG_WAIT'
            | 'OTHER';
            cancellation_notes?: string;
        }
    ): Promise<Order> => {
        const response = await api.post(`/orders/${orderId}/cancel/`, cancellationData);
        return response.data;
    },

    /**
     * Calificar una orden
     */
    rate: async (
        orderId: number,
        ratingData: {
            overall_rating: number;
            food_rating: number;
            delivery_rating: number;
            driver_rating?: number;
            driver_comment?: string;
            comment: string;
            would_order_again: boolean;
            liked_aspects?: string[];
            disliked_aspects?: string[];
        }
    ): Promise<OrderRating> => {
        const response = await api.post(`/orders/${orderId}/rate/`, ratingData);
        return response.data;
    },

    /**
     * Obtener la calificación de una orden
     */
    getRating: async (orderId: number): Promise<OrderRating> => {
        const response = await api.get(`/orders/${orderId}/rating/`);
        return response.data;
    },

    /**
     * Rastrear una orden en tiempo real
     */
    track: async (orderId: number): Promise<{
        order: Order;
        driver_location?: {
            latitude: number;
            longitude: number;
            heading?: number;
            speed?: number;
            updated_at: string;
        };
        estimated_arrival?: string;
        distance_to_customer?: number;
    }> => {
        const response = await api.get(`/orders/${orderId}/track/`);
        return response.data;
    },

    /**
     * Obtener estadísticas del usuario
     */
    getStatistics: async (): Promise<OrderStatistics> => {
        const response = await api.get('/orders/statistics/');
        return response.data;
    },

    /**
     * Reordenar (crear una nueva orden basada en una anterior)
     */
    reorder: async (orderId: number): Promise<Order> => {
        const response = await api.post(`/orders/${orderId}/reorder/`);
        return response.data;
    },
};
