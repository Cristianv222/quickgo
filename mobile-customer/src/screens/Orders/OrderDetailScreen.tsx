// src/screens/Orders/OrderDetailScreen.tsx
import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    TouchableOpacity,
    ActivityIndicator,
    Alert,
    RefreshControl,
    Image,
} from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { orderAPI, Order } from '../../api/orders';

export const OrderDetailScreen = () => {
    const route = useRoute<any>();
    const navigation = useNavigation();
    const { orderId } = route.params;

    const [order, setOrder] = useState<Order | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [cancelling, setCancelling] = useState(false);

    useEffect(() => {
        loadOrderDetail();
        // Auto-refresh cada 30 segundos para órdenes activas
        const interval = setInterval(() => {
            if (order && !['DELIVERED', 'CANCELLED'].includes(order.status)) {
                loadOrderDetail(true);
            }
        }, 30000);

        return () => clearInterval(interval);
    }, [orderId]);

    const loadOrderDetail = async (silent = false) => {
        try {
            if (!silent) setLoading(true);
            const orderData = await orderAPI.getById(orderId);
            setOrder(orderData);
        } catch (error) {
            console.error('Error loading order:', error);
            Alert.alert('Error', 'No se pudo cargar el detalle de la orden');
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const handleRefresh = () => {
        setRefreshing(true);
        loadOrderDetail();
    };

    const handleCancelOrder = () => {
        if (!order) return;

        Alert.alert(
            'Cancelar orden',
            '¿Estás seguro de que quieres cancelar esta orden?',
            [
                { text: 'No', style: 'cancel' },
                {
                    text: 'Sí, cancelar',
                    style: 'destructive',
                    onPress: async () => {
                        try {
                            setCancelling(true);
                            await orderAPI.cancel(order.id, {
                                cancellation_reason: 'CUSTOMER_REQUEST',
                                cancellation_notes: 'Cancelado por el cliente',
                            });
                            Alert.alert('Orden cancelada', 'Tu orden ha sido cancelada exitosamente');
                            loadOrderDetail();
                        } catch (error: any) {
                            Alert.alert(
                                'Error',
                                error.response?.data?.error || 'No se pudo cancelar la orden'
                            );
                        } finally {
                            setCancelling(false);
                        }
                    },
                },
            ]
        );
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

    const renderStatusTimeline = () => {
        if (!order) return null;

        const statuses = [
            { key: 'PENDING', label: 'Pendiente', time: order.created_at },
            { key: 'CONFIRMED', label: 'Confirmado', time: order.confirmed_at },
            { key: 'PREPARING', label: 'Preparando', time: order.preparing_at },
            { key: 'READY', label: 'Listo', time: order.ready_at },
            { key: 'PICKED_UP', label: 'Recogido', time: order.picked_up_at },
            { key: 'IN_TRANSIT', label: 'En camino', time: null },
            { key: 'DELIVERED', label: 'Entregado', time: order.delivered_at },
        ];

        const currentStatusIndex = statuses.findIndex((s) => s.key === order.status);

        return (
            <View style={styles.timeline}>
                {statuses.map((status, index) => {
                    const isCompleted = index <= currentStatusIndex;
                    const isCurrent = index === currentStatusIndex;

                    return (
                        <View key={status.key} style={styles.timelineItem}>
                            <View style={styles.timelineLeft}>
                                <View
                                    style={[
                                        styles.timelineDot,
                                        isCompleted && styles.timelineDotCompleted,
                                        isCurrent && styles.timelineDotCurrent,
                                    ]}
                                >
                                    {isCompleted && <Text style={styles.timelineDotIcon}>✓</Text>}
                                </View>
                                {index < statuses.length - 1 && (
                                    <View
                                        style={[
                                            styles.timelineLine,
                                            isCompleted && styles.timelineLineCompleted,
                                        ]}
                                    />
                                )}
                            </View>
                            <View style={styles.timelineRight}>
                                <Text
                                    style={[
                                        styles.timelineLabel,
                                        isCompleted && styles.timelineLabelCompleted,
                                    ]}
                                >
                                    {status.label}
                                </Text>
                                {status.time && (
                                    <Text style={styles.timelineTime}>
                                        {new Date(status.time).toLocaleTimeString('es-EC', {
                                            hour: '2-digit',
                                            minute: '2-digit',
                                        })}
                                    </Text>
                                )}
                            </View>
                        </View>
                    );
                })}
            </View>
        );
    };

    if (loading) {
        return (
            <View style={styles.centerContainer}>
                <ActivityIndicator size="large" color="#4CAF50" />
                <Text style={styles.loadingText}>Cargando orden...</Text>
            </View>
        );
    }

    if (!order) {
        return (
            <View style={styles.centerContainer}>
                <Text style={styles.errorText}>No se pudo cargar la orden</Text>
            </View>
        );
    }

    return (
        <ScrollView
            style={styles.container}
            refreshControl={
                <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} colors={['#4CAF50']} />
            }
        >
            {/* Estado actual */}
            <View style={styles.statusCard}>
                <View style={[styles.statusHeader, { backgroundColor: getStatusColor(order.status) }]}>
                    <Text style={styles.statusIcon}>{getStatusIcon(order.status)}</Text>
                    <Text style={styles.statusTitle}>{order.status_display}</Text>
                </View>
                <View style={styles.statusBody}>
                    <Text style={styles.orderNumber}>Orden #{order.order_number}</Text>
                    <Text style={styles.orderDate}>
                        {new Date(order.created_at).toLocaleString('es-EC', {
                            day: '2-digit',
                            month: 'long',
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                        })}
                    </Text>
                </View>
            </View>

            {/* Timeline */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>📍 Estado de tu orden</Text>
                {renderStatusTimeline()}
            </View>

            {/* Información del restaurante */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>🏪 Restaurante</Text>
                <View style={styles.restaurantInfo}>
                    {order.restaurant_logo && (
                        <Image source={{ uri: order.restaurant_logo }} style={styles.restaurantLogo} />
                    )}
                    <View style={styles.restaurantDetails}>
                        <Text style={styles.restaurantName}>{order.restaurant_name}</Text>
                        {order.restaurant_phone && (
                            <Text style={styles.restaurantPhone}>📞 {order.restaurant_phone}</Text>
                        )}
                        {order.restaurant_address && (
                            <Text style={styles.restaurantAddress}>📍 {order.restaurant_address}</Text>
                        )}
                    </View>
                </View>
            </View>

            {/* Conductor (si está asignado) */}
            {order.driver_name && (
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>🏍️ Conductor</Text>
                    <View style={styles.driverInfo}>
                        <Text style={styles.driverName}>{order.driver_name}</Text>
                        {order.driver_phone && (
                            <Text style={styles.driverPhone}>📞 {order.driver_phone}</Text>
                        )}
                        {order.driver_vehicle && (
                            <Text style={styles.vehicleInfo}>
                                🚗 {order.driver_vehicle.brand} {order.driver_vehicle.model} -{' '}
                                {order.driver_vehicle.plate}
                            </Text>
                        )}
                    </View>
                </View>
            )}

            {/* Productos */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>🛍️ Productos ({order.total_items})</Text>
                {order.items?.map((item, index) => (
                    <View key={index} style={styles.productItem}>
                        <View style={styles.productInfo}>
                            <Text style={styles.productQuantity}>{item.quantity}x</Text>
                            <View style={styles.productDetails}>
                                <Text style={styles.productName}>{item.product_name}</Text>
                                {item.selected_extras && item.selected_extras.length > 0 && (
                                    <View style={styles.customizations}>
                                        {item.selected_extras.map((extra, i) => (
                                            <Text key={i} style={styles.customizationText}>
                                                + {extra.name} (x{extra.quantity})
                                            </Text>
                                        ))}
                                    </View>
                                )}
                                {item.selected_options && item.selected_options.length > 0 && (
                                    <View style={styles.customizations}>
                                        {item.selected_options.map((option, i) => (
                                            <Text key={i} style={styles.customizationText}>
                                                • {option.option}
                                            </Text>
                                        ))}
                                    </View>
                                )}
                            </View>
                        </View>
                        <Text style={styles.productPrice}>${item.subtotal?.toFixed(2)}</Text>
                    </View>
                ))}
            </View>

            {/* Dirección de entrega */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>📍 Dirección de entrega</Text>
                <Text style={styles.address}>{order.delivery_address}</Text>
                {order.delivery_reference && (
                    <Text style={styles.addressReference}>Ref: {order.delivery_reference}</Text>
                )}
            </View>

            {/* Resumen de pago */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>💰 Resumen de pago</Text>
                <View style={styles.summaryRow}>
                    <Text style={styles.summaryLabel}>Subtotal</Text>
                    <Text style={styles.summaryValue}>${order.subtotal.toFixed(2)}</Text>
                </View>
                <View style={styles.summaryRow}>
                    <Text style={styles.summaryLabel}>Envío</Text>
                    <Text style={styles.summaryValue}>${order.delivery_fee.toFixed(2)}</Text>
                </View>
                <View style={styles.summaryRow}>
                    <Text style={styles.summaryLabel}>Tarifa de servicio</Text>
                    <Text style={styles.summaryValue}>${order.service_fee.toFixed(2)}</Text>
                </View>
                <View style={styles.summaryRow}>
                    <Text style={styles.summaryLabel}>IVA</Text>
                    <Text style={styles.summaryValue}>${order.tax.toFixed(2)}</Text>
                </View>
                {order.tip > 0 && (
                    <View style={styles.summaryRow}>
                        <Text style={styles.summaryLabel}>Propina</Text>
                        <Text style={styles.summaryValue}>${order.tip.toFixed(2)}</Text>
                    </View>
                )}
                <View style={[styles.summaryRow, styles.totalRow]}>
                    <Text style={styles.totalLabel}>Total</Text>
                    <Text style={styles.totalValue}>${order.total.toFixed(2)}</Text>
                </View>
                <View style={styles.paymentMethod}>
                    <Text style={styles.paymentMethodLabel}>Método de pago:</Text>
                    <Text style={styles.paymentMethodValue}>{order.payment_method_display}</Text>
                </View>
            </View>

            {/* Botones de acción */}
            <View style={styles.actions}>
                {order.can_be_cancelled && (
                    <TouchableOpacity
                        style={[styles.actionButton, styles.cancelButton]}
                        onPress={handleCancelOrder}
                        disabled={cancelling}
                    >
                        {cancelling ? (
                            <ActivityIndicator color="#fff" />
                        ) : (
                            <Text style={styles.actionButtonText}>Cancelar orden</Text>
                        )}
                    </TouchableOpacity>
                )}

                {order.status === 'DELIVERED' && !order.is_rated && (
                    <TouchableOpacity
                        style={[styles.actionButton, styles.rateButton]}
                        onPress={() => navigation.navigate('RateOrder', { orderId: order.id })}
                    >
                        <Text style={styles.actionButtonText}>Calificar orden</Text>
                    </TouchableOpacity>
                )}
            </View>
        </ScrollView>
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
    errorText: {
        fontSize: 16,
        color: '#F44336',
    },
    statusCard: {
        backgroundColor: '#fff',
        marginBottom: 16,
        overflow: 'hidden',
    },
    statusHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: 20,
    },
    statusIcon: {
        fontSize: 32,
        marginRight: 12,
    },
    statusTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#fff',
    },
    statusBody: {
        padding: 16,
    },
    orderNumber: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 4,
    },
    orderDate: {
        fontSize: 14,
        color: '#666',
    },
    section: {
        backgroundColor: '#fff',
        padding: 16,
        marginBottom: 16,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: '600',
        color: '#333',
        marginBottom: 12,
    },
    timeline: {
        paddingLeft: 8,
    },
    timelineItem: {
        flexDirection: 'row',
        marginBottom: 8,
    },
    timelineLeft: {
        alignItems: 'center',
        marginRight: 16,
    },
    timelineDot: {
        width: 24,
        height: 24,
        borderRadius: 12,
        backgroundColor: '#e0e0e0',
        justifyContent: 'center',
        alignItems: 'center',
    },
    timelineDotCompleted: {
        backgroundColor: '#4CAF50',
    },
    timelineDotCurrent: {
        backgroundColor: '#2196F3',
    },
    timelineDotIcon: {
        color: '#fff',
        fontSize: 12,
        fontWeight: 'bold',
    },
    timelineLine: {
        width: 2,
        flex: 1,
        backgroundColor: '#e0e0e0',
        marginVertical: 4,
    },
    timelineLineCompleted: {
        backgroundColor: '#4CAF50',
    },
    timelineRight: {
        flex: 1,
        paddingTop: 2,
    },
    timelineLabel: {
        fontSize: 14,
        color: '#999',
    },
    timelineLabelCompleted: {
        color: '#333',
        fontWeight: '500',
    },
    timelineTime: {
        fontSize: 12,
        color: '#999',
        marginTop: 2,
    },
    restaurantInfo: {
        flexDirection: 'row',
    },
    restaurantLogo: {
        width: 60,
        height: 60,
        borderRadius: 30,
        backgroundColor: '#f0f0f0',
        marginRight: 12,
    },
    restaurantDetails: {
        flex: 1,
    },
    restaurantName: {
        fontSize: 16,
        fontWeight: '600',
        color: '#333',
        marginBottom: 4,
    },
    restaurantPhone: {
        fontSize: 14,
        color: '#666',
        marginBottom: 2,
    },
    restaurantAddress: {
        fontSize: 14,
        color: '#666',
    },
    driverInfo: {},
    driverName: {
        fontSize: 16,
        fontWeight: '600',
        color: '#333',
        marginBottom: 4,
    },
    driverPhone: {
        fontSize: 14,
        color: '#666',
        marginBottom: 2,
    },
    vehicleInfo: {
        fontSize: 14,
        color: '#666',
    },
    productItem: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        paddingVertical: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#f0f0f0',
    },
    productInfo: {
        flexDirection: 'row',
        flex: 1,
    },
    productQuantity: {
        fontSize: 16,
        fontWeight: '600',
        color: '#666',
        marginRight: 12,
        minWidth: 30,
    },
    productDetails: {
        flex: 1,
    },
    productName: {
        fontSize: 16,
        color: '#333',
        marginBottom: 4,
    },
    customizations: {
        marginTop: 4,
    },
    customizationText: {
        fontSize: 12,
        color: '#888',
        marginBottom: 2,
    },
    productPrice: {
        fontSize: 16,
        fontWeight: '600',
        color: '#4CAF50',
    },
    address: {
        fontSize: 16,
        color: '#333',
        marginBottom: 4,
    },
    addressReference: {
        fontSize: 14,
        color: '#666',
        fontStyle: 'italic',
    },
    summaryRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 8,
    },
    summaryLabel: {
        fontSize: 14,
        color: '#666',
    },
    summaryValue: {
        fontSize: 14,
        color: '#333',
        fontWeight: '500',
    },
    totalRow: {
        marginTop: 8,
        paddingTop: 12,
        borderTopWidth: 1,
        borderTopColor: '#e0e0e0',
    },
    totalLabel: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
    },
    totalValue: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#4CAF50',
    },
    paymentMethod: {
        flexDirection: 'row',
        marginTop: 12,
        paddingTop: 12,
        borderTopWidth: 1,
        borderTopColor: '#f0f0f0',
    },
    paymentMethodLabel: {
        fontSize: 14,
        color: '#666',
        marginRight: 8,
    },
    paymentMethodValue: {
        fontSize: 14,
        fontWeight: '600',
        color: '#333',
    },
    actions: {
        padding: 16,
        paddingBottom: 32,
    },
    actionButton: {
        borderRadius: 12,
        padding: 16,
        alignItems: 'center',
        marginBottom: 12,
    },
    cancelButton: {
        backgroundColor: '#F44336',
    },
    rateButton: {
        backgroundColor: '#4CAF50',
    },
    actionButtonText: {
        fontSize: 16,
        fontWeight: '600',
        color: '#fff',
    },
});
