// src/screens/restaurants/CreateReviewScreen.tsx
import React, { useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { restaurantAPI } from '../../api/restaurants';

const CreateReviewScreen = ({ route, navigation }: any) => {
  const { restaurantId, orderId } = route.params;
  const [rating, setRating] = useState(5);
  const [foodQuality, setFoodQuality] = useState(5);
  const [deliveryTime, setDeliveryTime] = useState(5);
  const [packaging, setPackaging] = useState(5);
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (comment.trim().length < 10) {
      Alert.alert('Error', 'El comentario debe tener al menos 10 caracteres');
      return;
    }

    try {
      setLoading(true);
      await restaurantAPI.createReview({
        restaurant: restaurantId,
        rating,
        comment: comment.trim(),
        food_quality: foodQuality,
        delivery_time: deliveryTime,
        packaging,
        order: orderId,
      });

      Alert.alert('¡Éxito!', 'Tu reseña ha sido publicada', [
        {
          text: 'OK',
          onPress: () => navigation.goBack(),
        },
      ]);
    } catch (error: any) {
      console.error('Error creando reseña:', error);
      Alert.alert('Error', error.response?.data?.message || 'No se pudo crear la reseña');
    } finally {
      setLoading(false);
    }
  };

  const renderStars = (value: number, onChange: (val: number) => void) => (
    <View style={styles.starsContainer}>
      {[1, 2, 3, 4, 5].map((star) => (
        <TouchableOpacity key={star} onPress={() => onChange(star)}>
          <Ionicons
            name={star <= value ? 'star' : 'star-outline'}
            size={32}
            color="#FFD700"
          />
        </TouchableOpacity>
      ))}
    </View>
  );

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.title}>Califica tu Experiencia</Text>

        {/* Calificación General */}
        <View style={styles.ratingSection}>
          <Text style={styles.label}>Calificación General</Text>
          {renderStars(rating, setRating)}
        </View>

        {/* Calidad de Comida */}
        <View style={styles.ratingSection}>
          <Text style={styles.label}>Calidad de Comida</Text>
          {renderStars(foodQuality, setFoodQuality)}
        </View>

        {/* Tiempo de Entrega */}
        <View style={styles.ratingSection}>
          <Text style={styles.label}>Tiempo de Entrega</Text>
          {renderStars(deliveryTime, setDeliveryTime)}
        </View>

        {/* Empaquetado */}
        <View style={styles.ratingSection}>
          <Text style={styles.label}>Empaquetado</Text>
          {renderStars(packaging, setPackaging)}
        </View>

        {/* Comentario */}
        <View style={styles.commentSection}>
          <Text style={styles.label}>Cuéntanos más (mínimo 10 caracteres)</Text>
          <TextInput
            style={styles.commentInput}
            placeholder="Escribe tu opinión sobre el restaurante..."
            multiline
            numberOfLines={6}
            value={comment}
            onChangeText={setComment}
            textAlignVertical="top"
          />
          <Text style={styles.charCount}>{comment.length} caracteres</Text>
        </View>

        {/* Botón Enviar */}
        <TouchableOpacity
          style={[styles.submitButton, loading && styles.submitButtonDisabled]}
          onPress={handleSubmit}
          disabled={loading}
        >
          <Text style={styles.submitButtonText}>
            {loading ? 'Enviando...' : 'Publicar Reseña'}
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 24,
    textAlign: 'center',
  },
  ratingSection: {
    marginBottom: 24,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  starsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 8,
  },
  commentSection: {
    marginBottom: 24,
  },
  commentInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 12,
    padding: 12,
    fontSize: 16,
    minHeight: 120,
  },
  charCount: {
    textAlign: 'right',
    color: '#666',
    fontSize: 12,
    marginTop: 4,
  },
  submitButton: {
    backgroundColor: '#FF6B6B',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default CreateReviewScreen;