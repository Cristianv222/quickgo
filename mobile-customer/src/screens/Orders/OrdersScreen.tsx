// src/screens/Orders/OrdersScreen.tsx
import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    FlatList,
    TouchableOpacity,
    RefreshControl,
    ActivityIndicator,
    Image,
} from 'react-native';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { orderAPI, Order } from '../../api/orders';

export const OrdersScreen = () => {
    const navigation = useNavigation<any>();
    const [activeOrders, setActiveOrders] = useState<Order[]>([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    useFocusEffect(
        React.useCallback(() => {
            loadOrders();
        }, [])
    );

    const loadOrders = async () => {
        try {
            setLoading(true);
            const orders = await orderAPI.getActiveOrders();
            setActiveOrders(orders);
        } catch (error) {
            console.error('Error loading orders:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleRefresh = async () => {
        setRefreshing(true);
        await loadOrders();
        setRefreshing(false);
    };

    const getStatusColor = (status: string) => {
        const colors: Record<string, string> = {
            PENDING: '#FF9800',
            CONFIRMED: '#2196F3',
            PREPARING: '#9C27B0',
            READY: '#4CAF50',
            PICKED_UP: '#00BCD4',
            IN_TRANSIT: '#3F51B5',
            DELIVERED: '#4CAF50',
            CANCELLED: '#F44336',
        };
        return colors[status] || '#757575';
    };

    const getStatusIcon = (status: string) => {
        const icons: Record<string, string> = {
            PENDING: '⏳',
            CONFIRMED: '✅',
            PREPARING: '👨‍🍳',
            READY: '📦',
            PICKED_UP: '🏍️',
            IN_TRANSIT: '🚚',
            DELIVERED: '✅',
            CANCELLED: '❌',
        };
        return icons[status] || '📋';
    };

    const renderOrderItem = ({ item }: { item: Order }) => (
        <TouchableOpacity
            style={styles.orderCard}
            onPress={() => navigation.navigate('OrderDetail', { orderId: item.id })}
        >
            <View style={styles.orderHeader}>
                <View style={styles.orderInfo}>
                    <Text style={styles.orderNumber}>Orden #{item.order_number}</Text>
                    <Text style={styles.restaurantName}>{item.restaurant_name}</Text>
                </View>
                {item.restaurant_logo && (
                    <Image source={{ uri: item.restaurant_logo }} style={styles.restaurantLogo} />
                )}
            </View>

            <View style={styles.orderStatus}>
                <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
                    <Text style={styles.statusIcon}>{getStatusIcon(item.status)}</Text>
                    <Text style={styles.statusText}>{item.status_display}</Text>
                </View>
                <Text style={styles.orderTime}>
                    {new Date(item.created_at).toLocaleString('es-EC', {
                        day: '2-digit',
                        month: 'short',
                        hour: '2-digit',
                        minute: '2-digit',
                    })}
                </Text>
            </View>

            <View style={styles.orderDetails}>
                <Text style={styles.itemsCount}>
                    {item.total_items} {item.total_items === 1 ? 'producto' : 'productos'}
                </Text>
                <Text style={styles.orderTotal}>${Number(item.total || 0).toFixed(2)}</Text>
            </View>

            {item.estimated_delivery_time && (
                <View style={styles.deliveryTime}>
                    <Text style={styles.deliveryTimeIcon}>🕐</Text>
                    <Text style={styles.deliveryTimeText}>
                        Entrega estimada:{' '}
                        {new Date(item.estimated_delivery_time).toLocaleTimeString('es-EC', {
                            hour: '2-digit',
                            minute: '2-digit',
                        })}
                    </Text>
                </View>
            )}

            <TouchableOpacity
                style={styles.trackButton}
                onPress={() => navigation.navigate('OrderDetail', { orderId: item.id })}
            >
                <Text style={styles.trackButtonText}>Ver detalles →</Text>
            </TouchableOpacity>
        </TouchableOpacity>
    );

    if (loading) {
        return (
            <View style={styles.centerContainer}>
                <ActivityIndicator size="large" color="#4CAF50" />
                <Text style={styles.loadingText}>Cargando órdenes...</Text>
            </View>
        );
    }

    if (activeOrders.length === 0) {
        return (
            <View style={styles.emptyContainer}>
                <Text style={styles.emptyIcon}>📦</Text>
                <Text style={styles.emptyTitle}>No tienes órdenes activas</Text>
                <Text style={styles.emptyText}>
                    Tus órdenes en proceso aparecerán aquí
                </Text>
                <TouchableOpacity
                    style={styles.browseButton}
                    onPress={() => navigation.navigate('Home')}
                >
                    <Text style={styles.browseButtonText}>Explorar restaurantes</Text>
                </TouchableOpacity>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.headerTitle}>Mis Órdenes</Text>
                <Text style={styles.headerSubtitle}>
                    {activeOrders.length} {activeOrders.length === 1 ? 'orden activa' : 'órdenes activas'}
                </Text>
            </View>

            <FlatList
                data={activeOrders}
                renderItem={renderOrderItem}
                keyExtractor={(item) => item.id.toString()}
                contentContainerStyle={styles.listContent}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} colors={['#4CAF50']} />
                }
            />
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
    headerTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#333',
    },
    headerSubtitle: {
        fontSize: 14,
        color: '#666',
        marginTop: 4,
    },
    listContent: {
        padding: 16,
    },
    orderCard: {
        backgroundColor: '#fff',
        borderRadius: 12,
        padding: 16,
        marginBottom: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    orderHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 12,
    },
    orderInfo: {
        flex: 1,
    },
    orderNumber: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 4,
    },
    restaurantName: {
        fontSize: 14,
        color: '#666',
    },
    restaurantLogo: {
        width: 50,
        height: 50,
        borderRadius: 25,
        backgroundColor: '#f0f0f0',
    },
    orderStatus: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 12,
    },
    statusBadge: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 20,
    },
    statusIcon: {
        fontSize: 16,
        marginRight: 6,
    },
    statusText: {
        fontSize: 14,
        fontWeight: '600',
        color: '#fff',
    },
    orderTime: {
        fontSize: 12,
        color: '#999',
    },
    orderDetails: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingVertical: 12,
        borderTopWidth: 1,
        borderTopColor: '#f0f0f0',
    },
    itemsCount: {
        fontSize: 14,
        color: '#666',
    },
    orderTotal: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#4CAF50',
    },
    deliveryTime: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#FFF3E0',
        padding: 8,
        borderRadius: 8,
        marginTop: 8,
    },
    deliveryTimeIcon: {
        fontSize: 16,
        marginRight: 8,
    },
    deliveryTimeText: {
        fontSize: 12,
        color: '#F57C00',
        fontWeight: '500',
    },
    trackButton: {
        marginTop: 12,
        alignItems: 'center',
    },
    trackButtonText: {
        fontSize: 14,
        fontWeight: '600',
        color: '#4CAF50',
    },
    emptyContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 32,
        backgroundColor: '#f5f5f5',
    },
    emptyIcon: {
        fontSize: 80,
        marginBottom: 16,
    },
    emptyTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 8,
    },
    emptyText: {
        fontSize: 16,
        color: '#666',
        textAlign: 'center',
        marginBottom: 24,
    },
    browseButton: {
        backgroundColor: '#4CAF50',
        borderRadius: 12,
        paddingVertical: 12,
        paddingHorizontal: 32,
    },
    browseButtonText: {
        fontSize: 16,
        fontWeight: '600',
        color: '#fff',
    },
});
