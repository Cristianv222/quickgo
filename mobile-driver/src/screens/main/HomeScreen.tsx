import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { driverAPI, deliveryAPI } from '../../api/index';

interface DriverStats {
  total_deliveries: number;
  total_earnings: number;
  average_rating: number;
  deliveries_today: number;
  earnings_today: number;
}

const HomeScreen = ({ navigation }: any) => {
  const [isAvailable, setIsAvailable] = useState(false);
  const [isOnline, setIsOnline] = useState(false);
  const [stats, setStats] = useState<DriverStats | null>(null);
  const [activeDeliveries, setActiveDeliveries] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDriverData();
  }, []);

  const loadDriverData = async () => {
    try {
      setLoading(true);

      // Cargar perfil del conductor
      const profile = await driverAPI.getProfile();
      setIsAvailable(profile.is_available);
      setIsOnline(profile.is_online);

      // Cargar estadísticas
      const statistics = await driverAPI.getStatistics();
      setStats(statistics);

      // Cargar entregas activas
      const deliveries = await deliveryAPI.getActiveDeliveries();
      setActiveDeliveries(deliveries.results || deliveries);
    } catch (error) {
      console.error('Error loading driver data:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDriverData();
    setRefreshing(false);
  };

  const handleToggleAvailability = async (value: boolean) => {
    try {
      await driverAPI.updateAvailability(value);
      setIsAvailable(value);

      if (!value) {
        setIsOnline(false);
      }

      Alert.alert(
        'Disponibilidad Actualizada',
        value ? '¡Estás disponible para recibir pedidos!' : 'No recibirás nuevos pedidos'
      );
    } catch (error) {
      console.error('Error updating availability:', error);
      Alert.alert('Error', 'No se pudo actualizar tu disponibilidad');
    }
  };

  const handleToggleOnline = async (value: boolean) => {
    if (!isAvailable && value) {
      Alert.alert('Error', 'Primero debes activar tu disponibilidad');
      return;
    }

    try {
      await driverAPI.updateOnlineStatus(value);
      setIsOnline(value);

      Alert.alert(
        'Estado Actualizado',
        value ? '¡Estás en línea!' : 'Estás desconectado'
      );
    } catch (error) {
      console.error('Error updating online status:', error);
      Alert.alert('Error', 'No se pudo actualizar tu estado');
    }
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#FF6B6B']} />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>¡Hola, Conductor!</Text>
          <Text style={styles.subtitle}>¿Listo para hacer entregas?</Text>
        </View>
        <TouchableOpacity style={styles.notificationButton}>
          <Ionicons name="notifications-outline" size={24} color="#333" />
          <View style={styles.badge}>
            <Text style={styles.badgeText}>3</Text>
          </View>
        </TouchableOpacity>
      </View>

      {/* Estado del Conductor */}
      <View style={styles.statusCard}>
        <View style={styles.statusRow}>
          <View style={styles.statusInfo}>
            <Ionicons name="checkmark-circle" size={24} color="#4CAF50" />
            <Text style={styles.statusLabel}>Disponible</Text>
          </View>
          <Switch
            value={isAvailable}
            onValueChange={handleToggleAvailability}
            trackColor={{ false: '#E0E0E0', true: '#FF6B6B' }}
            thumbColor={isAvailable ? '#FFF' : '#FFF'}
          />
        </View>

        <View style={styles.statusRow}>
          <View style={styles.statusInfo}>
            <Ionicons name="wifi" size={24} color="#2196F3" />
            <Text style={styles.statusLabel}>En Línea</Text>
          </View>
          <Switch
            value={isOnline}
            onValueChange={handleToggleOnline}
            trackColor={{ false: '#E0E0E0', true: '#4CAF50' }}
            thumbColor={isOnline ? '#FFF' : '#FFF'}
            disabled={!isAvailable}
          />
        </View>
      </View>

      {/* Estadísticas del Día */}
      <View style={styles.statsContainer}>
        <Text style={styles.sectionTitle}>Hoy</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Ionicons name="bicycle" size={30} color="#FF6B6B" />
            <Text style={styles.statValue}>{stats?.deliveries_today || 0}</Text>
            <Text style={styles.statLabel}>Entregas</Text>
          </View>
          <View style={styles.statCard}>
            <Ionicons name="cash" size={30} color="#4CAF50" />
            <Text style={styles.statValue}>${stats?.earnings_today || 0}</Text>
            <Text style={styles.statLabel}>Ganancias</Text>
          </View>
        </View>
      </View>

      {/* Estadísticas Totales */}
      <View style={styles.statsContainer}>
        <Text style={styles.sectionTitle}>Total</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Ionicons name="stats-chart" size={30} color="#2196F3" />
            <Text style={styles.statValue}>{stats?.total_deliveries || 0}</Text>
            <Text style={styles.statLabel}>Entregas</Text>
          </View>
          <View style={styles.statCard}>
            <Ionicons name="wallet" size={30} color="#FF9800" />
            <Text style={styles.statValue}>${stats?.total_earnings || 0}</Text>
            <Text style={styles.statLabel}>Ganancias</Text>
          </View>
          <View style={styles.statCard}>
            <Ionicons name="star" size={30} color="#FFC107" />
            <Text style={styles.statValue}>{stats?.average_rating || 0}</Text>
            <Text style={styles.statLabel}>Calificación</Text>
          </View>
        </View>
      </View>

      {/* Entregas Activas */}
      {activeDeliveries.length > 0 && (
        <View style={styles.activeDeliveriesContainer}>
          <Text style={styles.sectionTitle}>Entregas Activas</Text>
          {activeDeliveries.map((delivery) => (
            <TouchableOpacity
              key={delivery.id}
              style={styles.deliveryCard}
              onPress={() => navigation.navigate('Orders')}
            >
              <View style={styles.deliveryHeader}>
                <Text style={styles.deliveryId}>#{delivery.order_number}</Text>
                <View style={styles.deliveryStatus}>
                  <Text style={styles.deliveryStatusText}>{delivery.status}</Text>
                </View>
              </View>
              <View style={styles.deliveryInfo}>
                <Ionicons name="location" size={16} color="#666" />
                <Text style={styles.deliveryAddress} numberOfLines={1}>
                  {delivery.delivery_address}
                </Text>
              </View>
              <View style={styles.deliveryFooter}>
                <Text style={styles.deliveryAmount}>${delivery.total}</Text>
                <Ionicons name="arrow-forward" size={20} color="#FF6B6B" />
              </View>
            </TouchableOpacity>
          ))}
        </View>
      )}

      {/* Acciones Rápidas */}
      <View style={styles.quickActionsContainer}>
        <Text style={styles.sectionTitle}>Acciones Rápidas</Text>
        <View style={styles.actionsGrid}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('Orders')}
          >
            <Ionicons name="list" size={30} color="#FF6B6B" />
            <Text style={styles.actionText}>Ver Pedidos</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('Earnings')}
          >
            <Ionicons name="trending-up" size={30} color="#4CAF50" />
            <Text style={styles.actionText}>Ganancias</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('Profile')}
          >
            <Ionicons name="settings" size={30} color="#2196F3" />
            <Text style={styles.actionText}>Configuración</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 60,
    paddingBottom: 20,
    backgroundColor: '#FFF',
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  notificationButton: {
    position: 'relative',
    width: 45,
    height: 45,
    borderRadius: 23,
    backgroundColor: '#F8F9FA',
    justifyContent: 'center',
    alignItems: 'center',
  },
  badge: {
    position: 'absolute',
    top: 0,
    right: 0,
    backgroundColor: '#FF6B6B',
    width: 18,
    height: 18,
    borderRadius: 9,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeText: {
    color: '#FFF',
    fontSize: 10,
    fontWeight: 'bold',
  },
  statusCard: {
    backgroundColor: '#FFF',
    marginHorizontal: 20,
    marginTop: 20,
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  statusInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginLeft: 10,
  },
  statsContainer: {
    marginHorizontal: 20,
    marginTop: 25,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statCard: {
    backgroundColor: '#FFF',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    width: '48%',
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 10,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  activeDeliveriesContainer: {
    marginHorizontal: 20,
    marginTop: 25,
  },
  deliveryCard: {
    backgroundColor: '#FFF',
    padding: 15,
    borderRadius: 12,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  deliveryHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  deliveryId: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  deliveryStatus: {
    backgroundColor: '#FF6B6B',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  deliveryStatusText: {
    color: '#FFF',
    fontSize: 12,
    fontWeight: '600',
  },
  deliveryInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  deliveryAddress: {
    fontSize: 14,
    color: '#666',
    marginLeft: 8,
    flex: 1,
  },
  deliveryFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  deliveryAmount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  quickActionsContainer: {
    marginHorizontal: 20,
    marginTop: 25,
    marginBottom: 30,
  },
  actionsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  actionButton: {
    backgroundColor: '#FFF',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    width: '31%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  actionText: {
    fontSize: 12,
    color: '#666',
    marginTop: 8,
    textAlign: 'center',
  },
});

export default HomeScreen;