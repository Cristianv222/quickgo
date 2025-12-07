// src/components/restaurants/RatingStars.tsx
import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface RatingStarsProps {
  rating: number;
  size?: number;
  color?: string;
}

const RatingStars: React.FC<RatingStarsProps> = ({
  rating,
  size = 16,
  color = '#FFD700',
}) => {
  const stars = [];
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;

  // Estrellas llenas
  for (let i = 0; i < fullStars; i++) {
    stars.push(
      <Ionicons key={`full-${i}`} name="star" size={size} color={color} />
    );
  }

  // Media estrella
  if (hasHalfStar) {
    stars.push(
      <Ionicons
        key="half"
        name="star-half"
        size={size}
        color={color}
      />
    );
  }

  // Estrellas vacías
  const emptyStars = 5 - stars.length;
  for (let i = 0; i < emptyStars; i++) {
    stars.push(
      <Ionicons
        key={`empty-${i}`}
        name="star-outline"
        size={size}
        color={color}
      />
    );
  }

  return <View style={styles.container}>{stars}</View>;
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    gap: 2,
  },
});

export default RatingStars;