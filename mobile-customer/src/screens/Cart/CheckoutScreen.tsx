// src/screens/Cart/CheckoutScreen.tsx
import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    TouchableOpacity,
    TextInput,
    Alert,
    ActivityIndicator,
} from 'react-native';
import { useCart } from '../../context/CartContext';
import { useNavigation } from '@react-navigation/native';
import { orderAPI, CreateOrderData } from '../../api/orders';

export const CheckoutScreen = () => {
    const navigation = useNavigation<any>();
    const { cart, restaurantId, clearCart, getCartSubtotal } = useCart();

    const [loading, setLoading] = useState(false);
    const [deliveryAddress, setDeliveryAddress] = useState('');
    const [deliveryReference, setDeliveryReference] = useState('');
    const [specialInstructions, setSpecialInstructions] = useState('');
    const [paymentMethod, setPaymentMethod] = useState<'CASH' | 'CARD' | 'ONLINE'>('CASH');
    const [tip, setTip] = useState(0);

    // Valores estimados (en producción vendrían del backend)
    const subtotal = getCartSubtotal();
    const deliveryFee = 2.5;
    const serviceFee = 0.5;
    const tax = subtotal * 0.12; // 12% IVA
    const total = subtotal + deliveryFee + serviceFee + tax + tip;

    // Coordenadas de ejemplo (en producción se obtendrían del GPS o mapa)
    const [latitude] = useState(0.812440);
    const [longitude] = useState(-77.717239);

    const handlePlaceOrder = async () => {
        // Validaciones
        if (!deliveryAddress.trim()) {
            Alert.alert('Error', 'Por favor ingresa tu dirección de entrega');
            return;
        }

        if (!restaurantId) {
            Alert.alert('Error', 'No se pudo identificar el restaurante');
            return;
        }

        if (cart.length === 0) {
            Alert.alert('Error', 'El carrito está vacío');
            return;
        }

        setLoading(true);

        try {
            const orderData: CreateOrderData = {
                restaurant_id: restaurantId,
                items: cart.map((item) => ({
                    product_id: item.product_id,
                    quantity: item.quantity,
                    selected_extras: item.selected_extras || [],
                    selected_options: item.selected_options || [],
                    special_notes: item.special_notes || '',
                })),
                delivery_address: deliveryAddress,
                delivery_reference: deliveryReference,
                delivery_latitude: latitude,
                delivery_longitude: longitude,
                payment_method: paymentMethod,
                special_instructions: specialInstructions,
                tip: tip,
            };

            const order = await orderAPI.create(orderData);

            // Limpiar carrito
            await clearCart();

            // Navegar a la pantalla de orden exitosa
            Alert.alert(
                '¡Orden creada!',
                `Tu orden #${order.order_number} ha sido creada exitosamente`,
                [
                    {
                        text: 'Ver orden',
                        onPress: () => navigation.navigate('OrderDetail', { orderId: order.id }),
                    },
                ]
            );
        } catch (error: any) {
            console.error('Error creating order:', error);
            const errorMessage =
                error.response?.data?.error ||
                error.response?.data?.message ||
                'No se pudo crear la orden. Intenta nuevamente.';
            Alert.alert('Error', errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const renderPaymentMethod = (method: 'CASH' | 'CARD' | 'ONLINE', label: string, icon: string) => (
        <TouchableOpacity
            style={[styles.paymentOption, paymentMethod === method && styles.paymentOptionSelected]}
            onPress={() => setPaymentMethod(method)}
        >
            <Text style={styles.paymentIcon}>{icon}</Text>
            <Text
                style={[
                    styles.paymentLabel,
                    paymentMethod === method && styles.paymentLabelSelected,
                ]}
            >
                {label}
            </Text>
            {paymentMethod === method && <Text style={styles.checkmark}>✓</Text>}
        </TouchableOpacity>
    );

    const renderTipOption = (amount: number) => (
        <TouchableOpacity
            style={[styles.tipOption, tip === amount && styles.tipOptionSelected]}
            onPress={() => setTip(amount)}
        >
            <Text style={[styles.tipText, tip === amount && styles.tipTextSelected]}>
                ${amount.toFixed(2)}
            </Text>
        </TouchableOpacity>
    );

    return (
        <View style={styles.container}>
            <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
                {/* Dirección de entrega */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>📍 Dirección de entrega</Text>
                    <TextInput
                        style={styles.input}
                        placeholder="Ej: Av. Principal 123, Tulcán"
                        value={deliveryAddress}
                        onChangeText={setDeliveryAddress}
                        multiline
                    />
                    <TextInput
                        style={styles.input}
                        placeholder="Referencia (opcional)"
                        value={deliveryReference}
                        onChangeText={setDeliveryReference}
                    />
                </View>

                {/* Método de pago */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>💳 Método de pago</Text>
                    <View style={styles.paymentMethods}>
                        {renderPaymentMethod('CASH', 'Efectivo', '💵')}
                        {renderPaymentMethod('CARD', 'Tarjeta', '💳')}
                        {renderPaymentMethod('ONLINE', 'En línea', '📱')}
                    </View>
                </View>

                {/* Propina */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>⭐ Propina para el repartidor</Text>
                    <View style={styles.tipOptions}>
                        {renderTipOption(0)}
                        {renderTipOption(0.5)}
                        {renderTipOption(1.0)}
                        {renderTipOption(2.0)}
                    </View>
                </View>

                {/* Instrucciones especiales */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>📝 Instrucciones especiales (opcional)</Text>
                    <TextInput
                        style={[styles.input, styles.textArea]}
                        placeholder="Ej: Sin cebolla, tocar el timbre 2 veces..."
                        value={specialInstructions}
                        onChangeText={setSpecialInstructions}
                        multiline
                        numberOfLines={3}
                    />
                </View>

                {/* Resumen del pedido */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>📋 Resumen del pedido</Text>
                    <View style={styles.summaryRow}>
                        <Text style={styles.summaryLabel}>Subtotal</Text>
                        <Text style={styles.summaryValue}>${subtotal.toFixed(2)}</Text>
                    </View>
                    <View style={styles.summaryRow}>
                        <Text style={styles.summaryLabel}>Envío</Text>
                        <Text style={styles.summaryValue}>${deliveryFee.toFixed(2)}</Text>
                    </View>
                    <View style={styles.summaryRow}>
                        <Text style={styles.summaryLabel}>Tarifa de servicio</Text>
                        <Text style={styles.summaryValue}>${serviceFee.toFixed(2)}</Text>
                    </View>
                    <View style={styles.summaryRow}>
                        <Text style={styles.summaryLabel}>IVA (12%)</Text>
                        <Text style={styles.summaryValue}>${tax.toFixed(2)}</Text>
                    </View>
                    {tip > 0 && (
                        <View style={styles.summaryRow}>
                            <Text style={styles.summaryLabel}>Propina</Text>
                            <Text style={styles.summaryValue}>${tip.toFixed(2)}</Text>
                        </View>
                    )}
                    <View style={[styles.summaryRow, styles.totalRow]}>
                        <Text style={styles.totalLabel}>Total</Text>
                        <Text style={styles.totalValue}>${total.toFixed(2)}</Text>
                    </View>
                </View>
            </ScrollView>

            {/* Botón de confirmar */}
            <View style={styles.footer}>
                <TouchableOpacity
                    style={[styles.confirmButton, loading && styles.confirmButtonDisabled]}
                    onPress={handlePlaceOrder}
                    disabled={loading}
                >
                    {loading ? (
                        <ActivityIndicator color="#fff" />
                    ) : (
                        <>
                            <Text style={styles.confirmButtonText}>Confirmar pedido</Text>
                            <Text style={styles.confirmButtonPrice}>${total.toFixed(2)}</Text>
                        </>
                    )}
                </TouchableOpacity>
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    scrollView: {
        flex: 1,
    },
    scrollContent: {
        padding: 16,
    },
    section: {
        backgroundColor: '#fff',
        borderRadius: 12,
        padding: 16,
        marginBottom: 16,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: '600',
        color: '#333',
        marginBottom: 12,
    },
    input: {
        backgroundColor: '#f5f5f5',
        borderRadius: 8,
        padding: 12,
        fontSize: 16,
        color: '#333',
        marginBottom: 8,
    },
    textArea: {
        minHeight: 80,
        textAlignVertical: 'top',
    },
    paymentMethods: {
        flexDirection: 'row',
        justifyContent: 'space-between',
    },
    paymentOption: {
        flex: 1,
        backgroundColor: '#f5f5f5',
        borderRadius: 8,
        padding: 12,
        marginHorizontal: 4,
        alignItems: 'center',
        borderWidth: 2,
        borderColor: 'transparent',
    },
    paymentOptionSelected: {
        backgroundColor: '#E8F5E9',
        borderColor: '#4CAF50',
    },
    paymentIcon: {
        fontSize: 24,
        marginBottom: 4,
    },
    paymentLabel: {
        fontSize: 14,
        color: '#666',
    },
    paymentLabelSelected: {
        color: '#4CAF50',
        fontWeight: '600',
    },
    checkmark: {
        fontSize: 16,
        color: '#4CAF50',
        marginTop: 4,
    },
    tipOptions: {
        flexDirection: 'row',
        justifyContent: 'space-between',
    },
    tipOption: {
        flex: 1,
        backgroundColor: '#f5f5f5',
        borderRadius: 8,
        padding: 12,
        marginHorizontal: 4,
        alignItems: 'center',
        borderWidth: 2,
        borderColor: 'transparent',
    },
    tipOptionSelected: {
        backgroundColor: '#E8F5E9',
        borderColor: '#4CAF50',
    },
    tipText: {
        fontSize: 16,
        color: '#666',
        fontWeight: '600',
    },
    tipTextSelected: {
        color: '#4CAF50',
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
    footer: {
        backgroundColor: '#fff',
        padding: 16,
        borderTopWidth: 1,
        borderTopColor: '#e0e0e0',
    },
    confirmButton: {
        backgroundColor: '#4CAF50',
        borderRadius: 12,
        padding: 16,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    confirmButtonDisabled: {
        backgroundColor: '#ccc',
    },
    confirmButtonText: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#fff',
    },
    confirmButtonPrice: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#fff',
    },
});
