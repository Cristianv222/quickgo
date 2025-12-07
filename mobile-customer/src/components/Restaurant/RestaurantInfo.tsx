// src/components/restaurants/RestaurantInfo.tsx
import React from 'react';
import { View, Text, StyleSheet, Linking, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { RestaurantDetail } from '../../api/restaurants';

interface RestaurantInfoProps {
  restaurant: RestaurantDetail;
}

const RestaurantInfo: React.FC<RestaurantInfoProps> = ({ restaurant }) => {
  const handleCall = () => {
    Linking.openURL(`tel:${restaurant.phone}`);
  };

  const handleOpenMaps = () => {
    const url = `https://www.google.com/maps/search/?api=1&query=${restaurant.latitude},${restaurant.longitude}`;
    Linking.openURL(url);
  };

  return (
    <View style={styles.container}>
      {/* Descripción */}
      <Text style={styles.description}>{restaurant.description}</Text>

      {/* Información de Entrega */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Información de Entrega</Text>

        <View style={styles.infoRow}>
          <Ionicons name="time-outline" size={20} color="#666" />
          <Text style={styles.infoText}>
            {restaurant.delivery_time_min}-{restaurant.delivery_time_max} min
          </Text>
        </View>

        <View style={styles.infoRow}>
          <Ionicons name="cash-outline" size={20} color="#666" />
          <Text style={styles.infoText}>
            Envío: ${restaurant.delivery_fee === 0 ? 'Gratis' : restaurant.delivery_fee}
          </Text>
        </View>

        <View style={styles.infoRow}>
          <Ionicons name="cart-outline" size={20} color="#666" />
          <Text style={styles.infoText}>
            Pedido mínimo: ${restaurant.min_order_amount}
          </Text>
        </View>

        {restaurant.free_delivery_above && (
          <View style={styles.infoRow}>
            <Ionicons name="gift-outline" size={20} color="#4CAF50" />
            <Text style={[styles.infoText, { color: '#4CAF50' }]}>
              Envío gratis desde ${restaurant.free_delivery_above}
            </Text>
          </View>
        )}

        {restaurant.distance && (
          <View style={styles.infoRow}>
            <Ionicons name="location-outline" size={20} color="#666" />
            <Text style={styles.infoText}>{restaurant.distance} km de distancia</Text>
          </View>
        )}
      </View>

      {/* Métodos de Pago */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Métodos de Pago</Text>
        <View style={styles.paymentMethods}>
          {restaurant.accepts_cash && (
            <View style={styles.paymentBadge}>
              <Ionicons name="cash-outline" size={16} color="#4CAF50" />
              <Text style={styles.paymentText}>Efectivo</Text>
            </View>
          )}
          {restaurant.accepts_card && (
            <View style={styles.paymentBadge}>
              <Ionicons name="card-outline" size={16} color="#2196F3" />
              <Text style={styles.paymentText}>Tarjeta</Text>
            </View>
          )}
        </View>
      </View>

      {/* Características */}
      {(restaurant.has_parking ||
        restaurant.has_wifi ||
        restaurant.is_eco_friendly) && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Características</Text>
          <View style={styles.features}>
            {restaurant.has_parking && (
              <View style={styles.featureBadge}>
                <Ionicons name="car-outline" size={16} color="#666" />
                <Text style={styles.featureText}>Parking</Text>
              </View>
            )}
            {restaurant.has_wifi && (
              <View style={styles.featureBadge}>
                <Ionicons name="wifi-outline" size={16} color="#666" />
                <Text style={styles.featureText}>WiFi</Text>
              </View>
            )}
            {restaurant.is_eco_friendly && (
              <View style={styles.featureBadge}>
                <Ionicons name="leaf-outline" size={16} color="#4CAF50" />
                <Text style={styles.featureText}>Eco-Friendly</Text>
              </View>
            )}
          </View>
        </View>
      )}

      {/* Contacto */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Contacto</Text>

        <TouchableOpacity style={styles.contactButton} onPress={handleCall}>
          <Ionicons name="call-outline" size={20} color="#FF6B6B" />
          <Text style={styles.contactText}>{restaurant.phone}</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.contactButton} onPress={handleOpenMaps}>
          <Ionicons name="location-outline" size={20} color="#FF6B6B" />
          <Text style={styles.contactText}>{restaurant.address}</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    gap: 16,
  },
  description: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  section: {
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 12,
  },
  paymentMethods: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  paymentBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    gap: 6,
  },
  paymentText: {
    fontSize: 14,
    color: '#333',
  },
  features: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  featureBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    gap: 6,
  },
  featureText: {
    fontSize: 14,
    color: '#333',
  },
  contactButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  contactText: {
    fontSize: 14,
    color: '#FF6B6B',
    marginLeft: 12,
  },
});

export default RestaurantInfo;