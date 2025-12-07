// src/components/restaurants/RestaurantHeader.tsx
import React from 'react';
import { View, Image, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { RestaurantDetail } from '../../api/restaurants';
import RatingStars from './RatingStars';

interface RestaurantHeaderProps {
  restaurant: RestaurantDetail;
  navigation: any;
}

const RestaurantHeader: React.FC<RestaurantHeaderProps> = ({
  restaurant,
  navigation,
}) => {
  return (
    <View style={styles.container}>
      <Image
        source={{
          uri: restaurant.banner || restaurant.logo || 'https://via.placeholder.com/400x200',
        }}
        style={styles.banner}
      />

      <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
        <Ionicons name="arrow-back" size={24} color="#fff" />
      </TouchableOpacity>

      <View style={styles.infoContainer}>
        <View style={styles.logoContainer}>
          <Image
            source={{
              uri: restaurant.logo || 'https://via.placeholder.com/80',
            }}
            style={styles.logo}
          />
        </View>

        <View style={styles.mainInfo}>
          <Text style={styles.name}>{restaurant.name}</Text>
          <Text style={styles.cuisine}>{restaurant.cuisine_name}</Text>

          <View style={styles.ratingContainer}>
            <RatingStars rating={restaurant.rating} size={16} />
            <Text style={styles.ratingText}>
              {restaurant.rating} ({restaurant.total_reviews} reseñas)
            </Text>
          </View>

          {!restaurant.is_open_now && (
            <View style={styles.closedBadge}>
              <Text style={styles.closedText}>Cerrado</Text>
            </View>
          )}
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'relative',
  },
  banner: {
    width: '100%',
    height: 200,
    backgroundColor: '#f0f0f0',
  },
  backButton: {
    position: 'absolute',
    top: 16,
    left: 16,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  infoContainer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: '#fff',
  },
  logoContainer: {
    width: 80,
    height: 80,
    marginTop: -40,
    marginRight: 16,
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: '#fff',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
  },
  logo: {
    width: '100%',
    height: '100%',
  },
  mainInfo: {
    flex: 1,
    justifyContent: 'center',
  },
  name: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  cuisine: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  ratingText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 8,
  },
  closedBadge: {
    alignSelf: 'flex-start',
    backgroundColor: '#FF6B6B',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 4,
    marginTop: 8,
  },
  closedText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
});

export default RestaurantHeader;