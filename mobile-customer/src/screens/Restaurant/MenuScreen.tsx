// src/screens/Restaurant/MenuScreen.tsx
import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    FlatList,
    TouchableOpacity,
    Image,
    ActivityIndicator,
    Alert,
} from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { useCart } from '../../context/CartContext';
import api from '../../api/index';

interface Product {
    id: number;
    name: string;
    description: string;
    price: string | number;
    image?: string;
    category: string;
    is_available: boolean;
    is_vegetarian?: boolean;
    is_vegan?: boolean;
    preparation_time?: number;
}

interface Restaurant {
    id: number;
    name: string;
    logo?: string;
}

export const MenuScreen = () => {
    const route = useRoute<any>();
    const navigation = useNavigation<any>();
    const { restaurantId } = route.params;

    const { addToCart, getCartItemsCount, restaurantId: cartRestaurantId } = useCart();

    const [restaurant, setRestaurant] = useState<Restaurant | null>(null);
    const [products, setProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState(true);
    const [categories, setCategories] = useState<string[]>([]);
    const [selectedCategory, setSelectedCategory] = useState<string>('all');

    useEffect(() => {
        loadMenu();
    }, []);

    const loadMenu = async () => {
        try {
            setLoading(true);

            // Cargar restaurante
            const restaurantData = await api.get(`/restaurants/${restaurantId}/`);
            setRestaurant(restaurantData.data);

            // Cargar menú usando la API correcta
            const { restaurantAPI } = await import('../../api/restaurants');
            const menuItems = await restaurantAPI.getMenu(restaurantId);

            setProducts(menuItems);

            // Extraer categorías únicas
            const uniqueCategories = [...new Set(menuItems.map((p: Product) => p.category))];
            setCategories(['all', ...uniqueCategories]);
        } catch (error) {
            console.error('Error loading menu:', error);
            Alert.alert('Error', 'No se pudo cargar el menú');
        } finally {
            setLoading(false);
        }
    };

    const handleAddToCart = (product: Product) => {
        if (!product.is_available) {
            Alert.alert('No disponible', 'Este producto no está disponible en este momento');
            return;
        }

        // Verificar si hay productos de otro restaurante
        if (cartRestaurantId && cartRestaurantId !== restaurantId) {
            Alert.alert(
                'Cambiar restaurante',
                'Tu carrito tiene productos de otro restaurante. ¿Deseas vaciar el carrito y agregar este producto?',
                [
                    { text: 'Cancelar', style: 'cancel' },
                    {
                        text: 'Sí, vaciar',
                        onPress: () => {
                            addItemToCart(product);
                        },
                    },
                ]
            );
        } else {
            addItemToCart(product);
        }
    };

    const addItemToCart = (product: Product) => {
        const cartItem = {
            product_id: product.id,
            product_name: product.name,
            product_description: product.description,
            product_image: product.image,
            unit_price: parseFloat(product.price.toString()),
            quantity: 1,
            selected_extras: [],
            selected_options: [],
            special_notes: '',
        };

        addToCart(cartItem, restaurantId, restaurant?.name || '');
        Alert.alert('¡Agregado!', `${product.name} agregado al carrito`, [
            { text: 'Seguir comprando', style: 'cancel' },
            { text: 'Ver carrito', onPress: () => navigation.navigate('Cart') },
        ]);
    };

    const filteredProducts = selectedCategory === 'all'
        ? products
        : products.filter(p => p.category === selectedCategory);

    const renderProduct = ({ item }: { item: Product }) => (
        <TouchableOpacity
            style={[styles.productCard, !item.is_available && styles.productCardDisabled]}
            onPress={() => handleAddToCart(item)}
            disabled={!item.is_available}
        >
            <Image
                source={{ uri: item.image || 'https://via.placeholder.com/100' }}
                style={styles.productImage}
            />
            <View style={styles.productInfo}>
                <View style={styles.productHeader}>
                    <Text style={styles.productName} numberOfLines={1}>
                        {item.name}
                    </Text>
                    <View style={styles.badges}>
                        {item.is_vegetarian && <Text style={styles.badge}>🌱</Text>}
                        {item.is_vegan && <Text style={styles.badge}>🥬</Text>}
                    </View>
                </View>

                <Text style={styles.productDescription} numberOfLines={2}>
                    {item.description}
                </Text>

                <View style={styles.productFooter}>
                    <Text style={styles.productPrice}>${parseFloat(item.price || 0).toFixed(2)}</Text>
                    {item.preparation_time && (
                        <Text style={styles.prepTime}>⏱️ {item.preparation_time} min</Text>
                    )}
                </View>

                {!item.is_available && (
                    <View style={styles.unavailableBadge}>
                        <Text style={styles.unavailableText}>No disponible</Text>
                    </View>
                )}
            </View>

            <TouchableOpacity
                style={[styles.addButton, !item.is_available && styles.addButtonDisabled]}
                onPress={() => handleAddToCart(item)}
                disabled={!item.is_available}
            >
                <Text style={styles.addButtonText}>+</Text>
            </TouchableOpacity>
        </TouchableOpacity>
    );

    const renderCategory = (category: string) => (
        <TouchableOpacity
            key={category}
            style={[
                styles.categoryChip,
                selectedCategory === category && styles.categoryChipActive,
            ]}
            onPress={() => setSelectedCategory(category)}
        >
            <Text
                style={[
                    styles.categoryText,
                    selectedCategory === category && styles.categoryTextActive,
                ]}
            >
                {category === 'all' ? 'Todos' : category}
            </Text>
        </TouchableOpacity>
    );

    if (loading) {
        return (
            <View style={styles.centerContainer}>
                <ActivityIndicator size="large" color="#4CAF50" />
                <Text style={styles.loadingText}>Cargando menú...</Text>
            </View>
        );
    }

    const cartItemCount = getCartItemsCount();

    return (
        <View style={styles.container}>
            {/* Header del restaurante */}
            <View style={styles.header}>
                <View style={styles.restaurantInfo}>
                    {restaurant?.logo && (
                        <Image source={{ uri: restaurant.logo }} style={styles.restaurantLogo} />
                    )}
                    <Text style={styles.restaurantName}>{restaurant?.name}</Text>
                </View>
            </View>

            {/* Categorías */}
            <View style={styles.categoriesContainer}>
                <FlatList
                    horizontal
                    data={categories}
                    renderItem={({ item }) => renderCategory(item)}
                    keyExtractor={(item) => item}
                    showsHorizontalScrollIndicator={false}
                    contentContainerStyle={styles.categoriesList}
                />
            </View>

            {/* Lista de productos */}
            <FlatList
                data={filteredProducts}
                renderItem={renderProduct}
                keyExtractor={(item) => item.id.toString()}
                contentContainerStyle={styles.productsList}
                ListEmptyComponent={
                    <View style={styles.emptyContainer}>
                        <Text style={styles.emptyText}>No hay productos disponibles</Text>
                    </View>
                }
            />

            {/* Botón flotante del carrito */}
            {cartItemCount > 0 && cartRestaurantId === restaurantId && (
                <TouchableOpacity
                    style={styles.cartButton}
                    onPress={() => navigation.navigate('Cart')}
                >
                    <View style={styles.cartBadge}>
                        <Text style={styles.cartBadgeText}>{cartItemCount}</Text>
                    </View>
                    <Text style={styles.cartButtonText}>Ver carrito</Text>
                    <Text style={styles.cartButtonIcon}>🛒</Text>
                </TouchableOpacity>
            )}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    centerContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#f5f5f5',
    },
    loadingText: {
        marginTop: 16,
        fontSize: 16,
        color: '#666',
    },
    header: {
        backgroundColor: '#fff',
        padding: 16,
        borderBottomWidth: 1,
        borderBottomColor: '#e0e0e0',
    },
    restaurantInfo: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    restaurantLogo: {
        width: 40,
        height: 40,
        borderRadius: 20,
        marginRight: 12,
        backgroundColor: '#f0f0f0',
    },
    restaurantName: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
    },
    categoriesContainer: {
        backgroundColor: '#fff',
        borderBottomWidth: 1,
        borderBottomColor: '#e0e0e0',
    },
    categoriesList: {
        paddingHorizontal: 16,
        paddingVertical: 12,
    },
    categoryChip: {
        paddingHorizontal: 16,
        paddingVertical: 8,
        borderRadius: 20,
        backgroundColor: '#f5f5f5',
        marginRight: 8,
    },
    categoryChipActive: {
        backgroundColor: '#4CAF50',
    },
    categoryText: {
        fontSize: 14,
        color: '#666',
        fontWeight: '500',
    },
    categoryTextActive: {
        color: '#fff',
    },
    productsList: {
        padding: 16,
    },
    productCard: {
        flexDirection: 'row',
        backgroundColor: '#fff',
        borderRadius: 12,
        padding: 12,
        marginBottom: 12,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    productCardDisabled: {
        opacity: 0.6,
    },
    productImage: {
        width: 100,
        height: 100,
        borderRadius: 8,
        backgroundColor: '#f0f0f0',
    },
    productInfo: {
        flex: 1,
        marginLeft: 12,
        marginRight: 8,
    },
    productHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 4,
    },
    productName: {
        fontSize: 16,
        fontWeight: '600',
        color: '#333',
        flex: 1,
    },
    badges: {
        flexDirection: 'row',
        marginLeft: 8,
    },
    badge: {
        fontSize: 16,
        marginLeft: 4,
    },
    productDescription: {
        fontSize: 14,
        color: '#666',
        marginBottom: 8,
    },
    productFooter: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    productPrice: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#4CAF50',
    },
    prepTime: {
        fontSize: 12,
        color: '#999',
    },
    unavailableBadge: {
        position: 'absolute',
        top: 0,
        right: 0,
        backgroundColor: '#F44336',
        paddingHorizontal: 8,
        paddingVertical: 4,
        borderRadius: 4,
    },
    unavailableText: {
        fontSize: 10,
        color: '#fff',
        fontWeight: '600',
    },
    addButton: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: '#4CAF50',
        justifyContent: 'center',
        alignItems: 'center',
        alignSelf: 'center',
    },
    addButtonDisabled: {
        backgroundColor: '#ccc',
    },
    addButtonText: {
        fontSize: 24,
        color: '#fff',
        fontWeight: 'bold',
    },
    emptyContainer: {
        padding: 32,
        alignItems: 'center',
    },
    emptyText: {
        fontSize: 16,
        color: '#999',
    },
    cartButton: {
        position: 'absolute',
        bottom: 16,
        left: 16,
        right: 16,
        backgroundColor: '#4CAF50',
        borderRadius: 12,
        padding: 16,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 8,
        elevation: 8,
    },
    cartBadge: {
        backgroundColor: '#fff',
        width: 24,
        height: 24,
        borderRadius: 12,
        justifyContent: 'center',
        alignItems: 'center',
    },
    cartBadgeText: {
        fontSize: 12,
        fontWeight: 'bold',
        color: '#4CAF50',
    },
    cartButtonText: {
        flex: 1,
        fontSize: 18,
        fontWeight: 'bold',
        color: '#fff',
        marginLeft: 12,
    },
    cartButtonIcon: {
        fontSize: 24,
    },
});
