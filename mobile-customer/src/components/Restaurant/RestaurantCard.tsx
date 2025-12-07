// src/components/restaurants/RestaurantCard.tsx
import React from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Restaurant } from '../../api/restaurants';
import RatingStars from './RatingStars';

interface RestaurantCardProps {
  restaurant: Restaurant;
  onPress: () => void;
  horizontal?: boolean;
}

const RestaurantCard: React.FC<RestaurantCardProps> = ({
  restaurant,
  onPress,
  horizontal = false,
}) => {
  const containerStyle = horizontal ? styles.horizontalCard : styles.card;

  return (
    <TouchableOpacity style={containerStyle} onPress={onPress} activeOpacity={0.7}>
      <Image
        source={{
          uri: restaurant.logo || 'https://via.placeholder.com/150',
        }}
        style={horizontal ? styles.horizontalImage : styles.image}
      />

      {/* Badges */}
      <View style={styles.badges}>
        {restaurant.is_new && (
          <View style={[styles.badge, styles.newBadge]}>
            <Text style={styles.badgeText}>Nuevo</Text>
          </View>
        )}
        {restaurant.has_promotion && (
          <View style={[styles.badge, styles.promoBadge]}>
            <Text style={styles.badgeText}>{restaurant.promotion_text}</Text>
          </View>
        )}
      </View>

      <View style={styles.info}>
        <Text style={styles.name} numberOfLines={1}>
          {restaurant.name}
        </Text>

        <Text style={styles.cuisine} numberOfLines={1}>
          {restaurant.cuisine_name}
        </Text>

        <View style={styles.ratingRow}>
          <RatingStars rating={restaurant.rating} size={14} />
          <Text style={styles.ratingText}>
            {restaurant.rating} ({restaurant.total_reviews})
          </Text>
        </View>

        <View style={styles.detailsRow}>
          <View style={styles.detailItem}>
            <Ionicons name="time-outline" size={14} color="#666" />
            <Text style={styles.detailText}>
              {restaurant.delivery_time_min}-{restaurant.delivery_time_max} min
            </Text>
          </View>

          <View style={styles.detailItem}>
            <Ionicons name="cash-outline" size={14} color="#666" />
            <Text style={styles.detailText}>
              ${restaurant.delivery_fee === 0 ? 'Gratis' : restaurant.delivery_fee}
            </Text>
          </View>

          {restaurant.distance && (
            <View style={styles.detailItem}>
              <Ionicons name="location-outline" size={14} color="#666" />
              <Text style={styles.detailText}>{restaurant.distance} km</Text>
            </View>
          )}
        </View>

        {/* Estado */}
        {!restaurant.is_open_now && (
          <View style={styles.closedBanner}>
            <Text style={styles.closedText}>Cerrado</Text>
          </View>
        )}
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginHorizontal: 16,
    marginBottom: 16,
    overflow: 'hidden',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  horizontalCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginRight: 16,
    overflow: 'hidden',
    width: 280,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  image: {
    width: '100%',
    height: 150,
    backgroundColor: '#f0f0f0',
  },
  horizontalImage: {
    width: '100%',
    height: 120,
    backgroundColor: '#f0f0f0',
  },
  badges: {
    position: 'absolute',
    top: 8,
    left: 8,
    flexDirection: 'row',
    gap: 4,
  },
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  newBadge: {
    backgroundColor: '#4CAF50',
  },
  promoBadge: {
    backgroundColor: '#FF6B6B',
  },
  badgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  info: {
    padding: 12,
  },
  name: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  cuisine: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  ratingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  ratingText: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
  },
  detailsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  detailItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  detailText: {
    fontSize: 12,
    color: '#666',
  },
  closedBanner: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  closedText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});

export default RestaurantCard;