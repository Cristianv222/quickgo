// src/context/CartContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { OrderItem } from '../api/orders';

interface CartItem extends OrderItem {
    product_name: string;
    product_description?: string;
    product_image?: string;
    unit_price: number;
}

interface CartContextType {
    cart: CartItem[];
    restaurantId: number | null;
    restaurantName: string | null;
    addToCart: (item: CartItem, restaurantId: number, restaurantName: string) => void;
    removeFromCart: (productId: number) => void;
    updateQuantity: (productId: number, quantity: number) => void;
    clearCart: () => void;
    getCartTotal: () => number;
    getCartSubtotal: () => number;
    getCartItemsCount: () => number;
    isInCart: (productId: number) => boolean;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

const CART_STORAGE_KEY = '@quickgo_cart';
const RESTAURANT_STORAGE_KEY = '@quickgo_cart_restaurant';

export const CartProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [cart, setCart] = useState<CartItem[]>([]);
    const [restaurantId, setRestaurantId] = useState<number | null>(null);
    const [restaurantName, setRestaurantName] = useState<string | null>(null);

    // Cargar carrito desde AsyncStorage al iniciar
    useEffect(() => {
        loadCart();
    }, []);

    // Guardar carrito en AsyncStorage cuando cambie
    useEffect(() => {
        saveCart();
    }, [cart, restaurantId, restaurantName]);

    const loadCart = async () => {
        try {
            const cartData = await AsyncStorage.getItem(CART_STORAGE_KEY);
            const restaurantData = await AsyncStorage.getItem(RESTAURANT_STORAGE_KEY);

            if (cartData) {
                setCart(JSON.parse(cartData));
            }

            if (restaurantData) {
                const { id, name } = JSON.parse(restaurantData);
                setRestaurantId(id);
                setRestaurantName(name);
            }
        } catch (error) {
            console.error('Error loading cart:', error);
        }
    };

    const saveCart = async () => {
        try {
            await AsyncStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
            if (restaurantId && restaurantName) {
                await AsyncStorage.setItem(
                    RESTAURANT_STORAGE_KEY,
                    JSON.stringify({ id: restaurantId, name: restaurantName })
                );
            }
        } catch (error) {
            console.error('Error saving cart:', error);
        }
    };

    const addToCart = (item: CartItem, newRestaurantId: number, newRestaurantName: string) => {
        // Si el carrito tiene items de otro restaurante, limpiar
        if (restaurantId && restaurantId !== newRestaurantId) {
            setCart([item]);
            setRestaurantId(newRestaurantId);
            setRestaurantName(newRestaurantName);
            return;
        }

        // Verificar si el producto ya está en el carrito
        const existingItemIndex = cart.findIndex((cartItem) => {
            // Comparar producto y personalizaciones
            const sameProduct = cartItem.product_id === item.product_id;
            const sameExtras =
                JSON.stringify(cartItem.selected_extras) === JSON.stringify(item.selected_extras);
            const sameOptions =
                JSON.stringify(cartItem.selected_options) === JSON.stringify(item.selected_options);
            const sameNotes = cartItem.special_notes === item.special_notes;

            return sameProduct && sameExtras && sameOptions && sameNotes;
        });

        if (existingItemIndex !== -1) {
            // Si ya existe, incrementar cantidad
            const updatedCart = [...cart];
            updatedCart[existingItemIndex].quantity += item.quantity;
            setCart(updatedCart);
        } else {
            // Si no existe, agregar nuevo item
            setCart([...cart, item]);
        }

        setRestaurantId(newRestaurantId);
        setRestaurantName(newRestaurantName);
    };

    const removeFromCart = (productId: number) => {
        const updatedCart = cart.filter((item) => item.product_id !== productId);
        setCart(updatedCart);

        // Si el carrito queda vacío, limpiar restaurante
        if (updatedCart.length === 0) {
            setRestaurantId(null);
            setRestaurantName(null);
        }
    };

    const updateQuantity = (productId: number, quantity: number) => {
        if (quantity <= 0) {
            removeFromCart(productId);
            return;
        }

        const updatedCart = cart.map((item) =>
            item.product_id === productId ? { ...item, quantity } : item
        );
        setCart(updatedCart);
    };

    const clearCart = async () => {
        setCart([]);
        setRestaurantId(null);
        setRestaurantName(null);
        try {
            await AsyncStorage.removeItem(CART_STORAGE_KEY);
            await AsyncStorage.removeItem(RESTAURANT_STORAGE_KEY);
        } catch (error) {
            console.error('Error clearing cart:', error);
        }
    };

    const calculateItemTotal = (item: CartItem): number => {
        let total = item.unit_price * item.quantity;

        // Sumar extras
        if (item.selected_extras && item.selected_extras.length > 0) {
            item.selected_extras.forEach((extra) => {
                const extraPrice = parseFloat(extra.price || '0');
                total += extraPrice * extra.quantity * item.quantity;
            });
        }

        // Sumar opciones
        if (item.selected_options && item.selected_options.length > 0) {
            item.selected_options.forEach((option) => {
                const optionPrice = parseFloat(option.price_modifier || '0');
                total += optionPrice * item.quantity;
            });
        }

        return total;
    };

    const getCartSubtotal = (): number => {
        return cart.reduce((total, item) => total + calculateItemTotal(item), 0);
    };

    const getCartTotal = (): number => {
        // Por ahora solo retorna el subtotal
        // En el checkout se agregarán delivery fee, service fee, etc.
        return getCartSubtotal();
    };

    const getCartItemsCount = (): number => {
        return cart.reduce((count, item) => count + item.quantity, 0);
    };

    const isInCart = (productId: number): boolean => {
        return cart.some((item) => item.product_id === productId);
    };

    return (
        <CartContext.Provider
            value={{
                cart,
                restaurantId,
                restaurantName,
                addToCart,
                removeFromCart,
                updateQuantity,
                clearCart,
                getCartTotal,
                getCartSubtotal,
                getCartItemsCount,
                isInCart,
            }}
        >
            {children}
        </CartContext.Provider>
    );
};

export const useCart = () => {
    const context = useContext(CartContext);
    if (context === undefined) {
        throw new Error('useCart must be used within a CartProvider');
    }
    return context;
};
