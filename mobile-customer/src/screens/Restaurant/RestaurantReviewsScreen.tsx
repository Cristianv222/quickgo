// src/screens/restaurants/RestaurantReviewsScreen.tsx
import React, { useState, useEffect } from 'react';
import {
  View,
  FlatList,
  StyleSheet,
  Text,
  ActivityIndicator,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { restaurantAPI, Review, ReviewStatistics } from '../../api/restaurants';
import ReviewCard from '../../components/Restaurant/ReviewCard';
import RatingStars from '../../components/Restaurant/RatingStars';

const RestaurantReviewsScreen = ({ route, navigation }: any) => {
  const { restaurantId } = route.params;
  const [reviews, setReviews] = useState<Review[]>([]);
  const [statistics, setStatistics] = useState<ReviewStatistics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReviews();
  }, []);

  const loadReviews = async () => {
    try {
      setLoading(true);
      const data = await restaurantAPI.getReviews(restaurantId);
      setReviews(data.reviews);
      setStatistics(data.statistics);
    } catch (error) {
      console.error('Error cargando reseñas:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderHeader = () => (
    <View style={styles.header}>
      {statistics && (
        <>
          <View style={styles.overallRating}>
            <Text style={styles.ratingNumber}>{statistics.average_rating}</Text>
            <RatingStars rating={statistics.average_rating} size={24} />
            <Text style={styles.totalReviews}>
              {statistics.total_reviews} reseñas
            </Text>
          </View>

          <View style={styles.detailedRatings}>
            <View style={styles.ratingRow}>
              <Text style={styles.ratingLabel}>Calidad de comida</Text>
              <RatingStars rating={statistics.average_food_quality} size={16} />
              <Text style={styles.ratingValue}>
                {statistics.average_food_quality}
              </Text>
            </View>

            <View style={styles.ratingRow}>
              <Text style={styles.ratingLabel}>Tiempo de entrega</Text>
              <RatingStars rating={statistics.average_delivery_time} size={16} />
              <Text style={styles.ratingValue}>
                {statistics.average_delivery_time}
              </Text>
            </View>

            <View style={styles.ratingRow}>
              <Text style={styles.ratingLabel}>Empaquetado</Text>
              <RatingStars rating={statistics.average_packaging} size={16} />
              <Text style={styles.ratingValue}>
                {statistics.average_packaging}
              </Text>
            </View>
          </View>
        </>
      )}

      <TouchableOpacity
        style={styles.writeReviewButton}
        onPress={() =>
          navigation.navigate('CreateReview', { restaurantId })
        }
      >
        <Ionicons name="create-outline" size={20} color="#fff" />
        <Text style={styles.writeReviewText}>Escribir Reseña</Text>
      </TouchableOpacity>

      <Text style={styles.reviewsTitle}>Todas las Reseñas</Text>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#FF6B6B" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <FlatList
        data={reviews}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => <ReviewCard review={item} detailed />}
        ListHeaderComponent={renderHeader}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
      />
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
  header: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  overallRating: {
    alignItems: 'center',
    paddingVertical: 16,
  },
  ratingNumber: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  totalReviews: {
    fontSize: 14,
    color: '#666',
    marginTop: 8,
  },
  detailedRatings: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  ratingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  ratingLabel: {
    flex: 1,
    fontSize: 14,
    color: '#666',
  },
  ratingValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginLeft: 8,
    minWidth: 30,
    textAlign: 'right',
  },
  writeReviewButton: {
    flexDirection: 'row',
    backgroundColor: '#FF6B6B',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 16,
  },
  writeReviewText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  reviewsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 24,
  },
  listContent: {
    paddingBottom: 16,
  },
});

export default RestaurantReviewsScreen;