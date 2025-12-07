// src/screens/restaurants/RestaurantDetailScreen.tsx
import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Text,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as Location from 'expo-location';
import { restaurantAPI, RestaurantDetail } from '../../api/restaurants';
import RestaurantHeader from '../../components/Restaurant/RestaurantHeader';
import RestaurantInfo from '../../components/Restaurant/RestaurantInfo';
import RestaurantSchedule from '../../components/Restaurant/RestaurantSchedule';
import ReviewCard from '../../components/Restaurant/ReviewCard';

const RestaurantDetailScreen = ({ route, navigation }: any) => {
  const { restaurantId } = route.params;
  const [restaurant, setRestaurant] = useState<RestaurantDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { 
    loadRestaurant();
  }, []);

  const loadRestaurant = async () => {
    try {
      setLoading(true);

      // Obtener ubicación del usuario
      const { status } = await Location.requestForegroundPermissionsAsync();
      let latitude, longitude;

      if (status === 'granted') {
        const location = await Location.getCurrentPositionAsync({});
        latitude = location.coords.latitude;
        longitude = location.coords.longitude;
      }

      const data = await restaurantAPI.getDetail(restaurantId, latitude, longitude);
      setRestaurant(data);
    } catch (error) {
      console.error('Error cargando restaurante:', error);
      Alert.alert('Error', 'No se pudo cargar el restaurante');
      navigation.goBack();
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#FF6B6B" />
      </View>
    );
  }

  if (!restaurant) return null;

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <ScrollView showsVerticalScrollIndicator={false}>
        <RestaurantHeader restaurant={restaurant} navigation={navigation} />

        <View style={styles.content}>
          <RestaurantInfo restaurant={restaurant} />

          {/* Horarios */}
          {restaurant.schedules.length > 0 && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Horarios de Atención</Text>
              <RestaurantSchedule schedules={restaurant.schedules} />
            </View>
          )}

          {/* Reseñas Recientes */}
          {restaurant.recent_reviews.length > 0 && (
            <View style={styles.section}>
              <View style={styles.reviewsHeader}>
                <Text style={styles.sectionTitle}>
                  Reseñas ({restaurant.total_reviews})
                </Text>
                <TouchableOpacity
                  onPress={() =>
                    navigation.navigate('RestaurantReviews', { restaurantId })
                  }
                >
                  <Text style={styles.seeAllText}>Ver todas</Text>
                </TouchableOpacity>
              </View>

              {restaurant.recent_reviews.map((review) => (
                <ReviewCard key={review.id} review={review} />
              ))}
            </View>
          )}

          {/* Botón para ver menú (próximamente) */}
          <TouchableOpacity
            style={styles.menuButton}
            onPress={() => Alert.alert('Próximamente', 'Menú en desarrollo')}
          >
            <Text style={styles.menuButtonText}>Ver Menú</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    padding: 16,
  },
  section: {
    marginTop: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  reviewsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  seeAllText: {
    color: '#FF6B6B',
    fontSize: 14,
    fontWeight: '600',
  },
  menuButton: {
    backgroundColor: '#FF6B6B',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 24,
    marginBottom: 16,
  },
  menuButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default RestaurantDetailScreen;