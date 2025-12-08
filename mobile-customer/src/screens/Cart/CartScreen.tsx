// src/screens/Cart/CartScreen.tsx
import React from 'react';
import {
    View,
    Text,
    StyleSheet,
    FlatList,
    TouchableOpacity,
    Image,
    Alert,
} from 'react-native';
import { useCart } from '../../context/CartContext';
import { useNavigation } from '@react-navigation/native';

export const CartScreen = () => {
    const navigation = useNavigation<any>();
    const {
        cart,
        restaurantName,
        removeFromCart,
        updateQuantity,
        clearCart,
        getCartSubtotal,
        getCartItemsCount,
    } = useCart();

    const handleCheckout = () => {
        if (cart.length === 0) {
            Alert.alert('Carrito vacío', 'Agrega productos para continuar');
            return;
        }
        navigation.navigate('Checkout');
    };

    const handleClearCart = () => {
        Alert.alert(
            'Vaciar carrito',
            '¿Estás seguro de que quieres vaciar el carrito?',
            [
                { text: 'Cancelar', style: 'cancel' },
                {
                    text: 'Vaciar',
                    style: 'destructive',
                    onPress: clearCart,
                },
            ]
        );
    };

    const renderCartItem = ({ item }: any) => {
        const itemTotal =
            item.unit_price * item.quantity +
            (item.selected_extras?.reduce(
                (sum: number, extra: any) => sum + parseFloat(extra.price || 0) * extra.quantity,
                0
            ) || 0) * item.quantity +
            (item.selected_options?.reduce(
                (sum: number, option: any) => sum + parseFloat(option.price_modifier || 0),
                0
            ) || 0) * item.quantity;

        return (
            <View style={styles.cartItem}>
                <Image
                    source={{ uri: item.product_image || 'https://via.placeholder.com/80' }}
                    style={styles.productImage}
                />
                <View style={styles.itemDetails}>
                    <Text style={styles.productName}>{item.product_name}</Text>
                    {item.product_description && (
                        <Text style={styles.productDescription} numberOfLines={2}>
                            {item.product_description}
                        </Text>
                    )}

                    {/* Extras */}
                    {item.selected_extras && item.selected_extras.length > 0 && (
                        <View style={styles.customizations}>
                            {item.selected_extras.map((extra: any, index: number) => (
                                <Text key={index} style={styles.customizationText}>
                                    + {extra.name} (x{extra.quantity})
                                </Text>
                            ))}
                        </View>
                    )}

                    {/* Opciones */}
                    {item.selected_options && item.selected_options.length > 0 && (
                        <View style={styles.customizations}>
                            {item.selected_options.map((option: any, index: number) => (
                                <Text key={index} style={styles.customizationText}>
                                    • {option.option}
                                </Text>
                            ))}
                        </View>
                    )}

                    {/* Notas especiales */}
                    {item.special_notes && (
                        <Text style={styles.specialNotes}>Nota: {item.special_notes}</Text>
                    )}

                    <View style={styles.priceRow}>
                        <Text style={styles.price}>${itemTotal.toFixed(2)}</Text>
                        <View style={styles.quantityControls}>
                            <TouchableOpacity
                                style={styles.quantityButton}
                                onPress={() => updateQuantity(item.product_id, item.quantity - 1)}
                            >
                                <Text style={styles.quantityButtonText}>-</Text>
                            </TouchableOpacity>
                            <Text style={styles.quantity}>{item.quantity}</Text>
                            <TouchableOpacity
                                style={styles.quantityButton}
                                onPress={() => updateQuantity(item.product_id, item.quantity + 1)}
                            >
                                <Text style={styles.quantityButtonText}>+</Text>
                            </TouchableOpacity>
                        </View>
                    </View>
                </View>

                <TouchableOpacity
                    style={styles.removeButton}
                    onPress={() => removeFromCart(item.product_id)}
                >
                    <Text style={styles.removeButtonText}>✕</Text>
                </TouchableOpacity>
            </View>
        );
    };

    if (cart.length === 0) {
        return (
            <View style={styles.emptyContainer}>
                <Text style={styles.emptyIcon}>🛒</Text>
                <Text style={styles.emptyTitle}>Tu carrito está vacío</Text>
                <Text style={styles.emptyText}>
                    Agrega productos de tus restaurantes favoritos
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
            {/* Header */}
            <View style={styles.header}>
                <Text style={styles.headerTitle}>Mi Carrito</Text>
                {restaurantName && (
                    <Text style={styles.restaurantName}>📍 {restaurantName}</Text>
                )}
                <TouchableOpacity onPress={handleClearCart}>
                    <Text style={styles.clearButton}>Vaciar carrito</Text>
                </TouchableOpacity>
            </View>

            {/* Lista de productos */}
            <FlatList
                data={cart}
                renderItem={renderCartItem}
                keyExtractor={(item, index) => `${item.product_id}-${index}`}
                contentContainerStyle={styles.listContent}
            />

            {/* Footer con totales */}
            <View style={styles.footer}>
                <View style={styles.summaryRow}>
                    <Text style={styles.summaryLabel}>Subtotal ({getCartItemsCount()} items)</Text>
                    <Text style={styles.summaryValue}>${getCartSubtotal().toFixed(2)}</Text>
                </View>

                <TouchableOpacity style={styles.checkoutButton} onPress={handleCheckout}>
                    <Text style={styles.checkoutButtonText}>Continuar al pago</Text>
                    <Text style={styles.checkoutButtonPrice}>${getCartSubtotal().toFixed(2)}</Text>
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
    restaurantName: {
        fontSize: 14,
        color: '#666',
        marginTop: 4,
    },
    clearButton: {
        fontSize: 14,
        color: '#ff4444',
        marginTop: 8,
    },
    listContent: {
        padding: 16,
    },
    cartItem: {
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
    productImage: {
        width: 80,
        height: 80,
        borderRadius: 8,
        backgroundColor: '#f0f0f0',
    },
    itemDetails: {
        flex: 1,
        marginLeft: 12,
    },
    productName: {
        fontSize: 16,
        fontWeight: '600',
        color: '#333',
        marginBottom: 4,
    },
    productDescription: {
        fontSize: 12,
        color: '#666',
        marginBottom: 8,
    },
    customizations: {
        marginBottom: 8,
    },
    customizationText: {
        fontSize: 12,
        color: '#888',
        marginBottom: 2,
    },
    specialNotes: {
        fontSize: 12,
        color: '#666',
        fontStyle: 'italic',
        marginBottom: 8,
    },
    priceRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    price: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#4CAF50',
    },
    quantityControls: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#f5f5f5',
        borderRadius: 20,
        paddingHorizontal: 4,
    },
    quantityButton: {
        width: 32,
        height: 32,
        borderRadius: 16,
        backgroundColor: '#fff',
        justifyContent: 'center',
        alignItems: 'center',
        margin: 4,
    },
    quantityButtonText: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#4CAF50',
    },
    quantity: {
        fontSize: 16,
        fontWeight: '600',
        marginHorizontal: 12,
        color: '#333',
    },
    removeButton: {
        width: 24,
        height: 24,
        justifyContent: 'center',
        alignItems: 'center',
    },
    removeButtonText: {
        fontSize: 20,
        color: '#999',
    },
    footer: {
        backgroundColor: '#fff',
        padding: 16,
        borderTopWidth: 1,
        borderTopColor: '#e0e0e0',
    },
    summaryRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 16,
    },
    summaryLabel: {
        fontSize: 16,
        color: '#666',
    },
    summaryValue: {
        fontSize: 16,
        fontWeight: '600',
        color: '#333',
    },
    checkoutButton: {
        backgroundColor: '#4CAF50',
        borderRadius: 12,
        padding: 16,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    checkoutButtonText: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#fff',
    },
    checkoutButtonPrice: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#fff',
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
