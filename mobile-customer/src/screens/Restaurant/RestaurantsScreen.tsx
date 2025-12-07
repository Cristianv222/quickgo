// src/screens/restaurants/RestaurantsScreen.tsx
import React, { useState, useEffect } from 'react';
import {
  View,
  FlatList,
  StyleSheet,
  RefreshControl,
  TextInput,
  TouchableOpacity,
  Text,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as Location from 'expo-location';
import { Ionicons } from '@expo/vector-icons';
import { restaurantAPI, Restaurant } from '../../api/restaurants';
import RestaurantCard from '../../components/Restaurant/RestaurantCard';

const RestaurantsScreen = ({ navigation }: any) => {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [featuredRestaurants, setFeaturedRestaurants] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [userLocation, setUserLocation] = useState<{
    latitude: number;
    longitude: number;
  } | null>(null);

  useEffect(() => {
    loadUserLocation();
  }, []);

  useEffect(() => {
    if (userLocation) {
      loadRestaurants();
      loadFeatured();
    }
  }, [userLocation]);

  const loadUserLocation = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        console.error('Permiso de ubicación denegado');
        return;
      }

      const location = await Location.getCurrentPositionAsync({});
      setUserLocation({
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
      });
    } catch (error) {
      console.error('Error obteniendo ubicación:', error);
    }
  };

  const loadRestaurants = async () => {
    if (!userLocation) return;

    try {
      setLoading(true);
      const data = await restaurantAPI.getNearby(
        userLocation.latitude,
        userLocation.longitude,
        10
      );
      setRestaurants(data);
    } catch (error) {
      console.error('Error cargando restaurantes:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadFeatured = async () => {
    try {
      const data = await restaurantAPI.getFeatured();
      setFeaturedRestaurants(data);
    } catch (error) {
      console.error('Error cargando destacados:', error);
    }
  };

  const handleSearch = async (text: string) => {
    setSearchQuery(text);

    if (text.length >= 2) {
      try {
        const data = await restaurantAPI.search(text);
        setRestaurants(data);
      } catch (error) {
        console.error('Error en búsqueda:', error);
      }
    } else if (text.length === 0 && userLocation) {
      loadRestaurants();
    }
  };

  const renderHeader = () => (
    <View style={styles.header}>
      <View style={styles.searchContainer}>
        <Ionicons name="search" size={20} color="#666" style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Buscar restaurantes..."
          value={searchQuery}
          onChangeText={handleSearch}
        />
        {searchQuery.length > 0 && (
          <TouchableOpacity onPress={() => handleSearch('')}>
            <Ionicons name="close-circle" size={20} color="#666" />
          </TouchableOpacity>
        )}
      </View>

      {featuredRestaurants.length > 0 && searchQuery.length === 0 && (
        <View style={styles.featuredSection}>
          <Text style={styles.sectionTitle}>Destacados</Text>
          <FlatList
            horizontal
            data={featuredRestaurants}
            keyExtractor={(item) => `featured-${item.id}`}
            renderItem={({ item }) => (
              <RestaurantCard
                restaurant={item}
                onPress={() =>
                  navigation.navigate('RestaurantDetail', { restaurantId: item.id })
                }
                horizontal
              />
            )}
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.featuredList}
          />
        </View>
      )}

      {searchQuery.length === 0 && (
        <Text style={styles.sectionTitle}>Restaurantes Cercanos</Text>
      )}
    </View>
  );

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <FlatList
        data={restaurants}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <RestaurantCard
            restaurant={item}
            onPress={() =>
              navigation.navigate('RestaurantDetail', { restaurantId: item.id })
            }
          />
        )}
        ListHeaderComponent={renderHeader}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={loadRestaurants} />
        }
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    paddingHorizontal: 16,
    paddingTop: 16,
    backgroundColor: '#fff',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
    borderRadius: 12,
    paddingHorizontal: 12,
    marginBottom: 16,
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    paddingVertical: 12,
    fontSize: 16,
  },
  featuredSection: {
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#333',
  },
  featuredList: {
    paddingRight: 16,
  },
  listContent: {
    paddingBottom: 16,
  },
});

export default RestaurantsScreen;