// src/components/restaurants/ReviewCard.tsx
import React from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';
import { Review } from '../../api/restaurants';
import RatingStars from './RatingStars';

interface ReviewCardProps {
  review: Review;
  detailed?: boolean;
}

const ReviewCard: React.FC<ReviewCardProps> = ({ review, detailed = false }) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Image
          source={{
            uri: review.customer_avatar || 'https://via.placeholder.com/40',
          }}
          style={styles.avatar}
        />
        <View style={styles.headerInfo}>
          <Text style={styles.customerName}>{review.customer_name}</Text>
          <Text style={styles.date}>{formatDate(review.created_at)}</Text>
        </View>
        <RatingStars rating={review.rating} size={16} />
      </View>

      {detailed && (
        <View style={styles.detailedRatings}>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Comida:</Text>
            <RatingStars rating={review.food_quality} size={12} />
          </View>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Entrega:</Text>
            <RatingStars rating={review.delivery_time} size={12} />
          </View>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Empaque:</Text>
            <RatingStars rating={review.packaging} size={12} />
          </View>
        </View>
      )}

      <Text style={styles.comment}>{review.comment}</Text>

      {review.restaurant_response && (
        <View style={styles.responseContainer}>
          <Text style={styles.responseLabel}>Respuesta del restaurante:</Text>
          <Text style={styles.responseText}>{review.restaurant_response}</Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#fff',
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#eee',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#f0f0f0',
  },
  headerInfo: {
    flex: 1,
    marginLeft: 12,
  },
  customerName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  date: {
    fontSize: 12,
    color: '#999',
    marginTop: 2,
  },
  detailedRatings: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 12,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  detailLabel: {
    fontSize: 11,
    color: '#666',
  },
  comment: {
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
  },
  responseContainer: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    backgroundColor: '#f9f9f9',
    padding: 12,
    borderRadius: 8,
  },
  responseLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
    marginBottom: 4,
  },
  responseText: {
    fontSize: 13,
    color: '#333',
    lineHeight: 18,
  },
});

export default ReviewCard;