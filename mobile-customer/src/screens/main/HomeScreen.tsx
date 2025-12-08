import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,  // ✅ AGREGADO
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { authAPI } from '../../api';
import { Avatar, Card, Button } from 'react-native-paper';
import { useAuth } from '../../context/AuthContext';

export default function HomeScreen({ navigation }: any) {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { logout } = useAuth();

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const currentUser = await authAPI.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      console.error('Error al cargar usuario:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#FF6B35" />
        <Text style={styles.loadingText}>Cargando...</Text>
      </View>
    );
  }

  const menuOptions = [
    {
      id: 1,
      title: 'Mi Perfil',
      subtitle: 'Ver y editar información',
      icon: 'account',
      color: '#FF6B35',
      onPress: () => navigation.navigate('ProfileTab'),
    },
    {
      id: 2,
      title: 'Restaurantes',
      subtitle: 'Explora restaurantes cercanos',
      icon: 'store',
      color: '#34C759',
      onPress: () => navigation.navigate('RestaurantsTab'),
    },
    {
      id: 3,
      title: 'Mis Pedidos',
      subtitle: 'Próximamente disponible',
      icon: 'clipboard-text',
      color: '#5856D6',
      onPress: () => Alert.alert('Próximamente', 'Función en desarrollo'),  // ✅ CORREGIDO
    },
    {
      id: 4,
      title: 'Favoritos',
      subtitle: 'Próximamente disponible',
      icon: 'heart',
      color: '#FF2D55',
      onPress: () => Alert.alert('Próximamente', 'Función en desarrollo'),  // ✅ CORREGIDO
    },
    {
      id: 5,
      title: 'Configuración',
      subtitle: 'Próximamente disponible',
      icon: 'cog',
      color: '#8E8E93',
      onPress: () => Alert.alert('Próximamente', 'Función en desarrollo'),  // ✅ CORREGIDO
    },
    {
      id: 6,
      title: 'Ayuda',
      subtitle: 'Próximamente disponible',
      icon: 'help-circle',
      color: '#5AC8FA',
      onPress: () => Alert.alert('Próximamente', 'Función en desarrollo'),  // ✅ CORREGIDO
    },
  ];

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerContent}>
            <View style={styles.userInfo}>
              <Avatar.Text
                size={60}
                label={user?.first_name?.charAt(0) || 'U'}
                style={styles.avatar}
              />
              <View style={styles.userText}>
                <Text style={styles.greeting}>¡Hola,</Text>
                <Text style={styles.userName}>
                  {user?.first_name || 'Usuario'}!
                </Text>
                <Text style={styles.userEmail}>
                  {user?.email || 'usuario@email.com'}
                </Text>
              </View>
            </View>
          </View>
        </View>

        {/* Welcome Card */}
        <View style={styles.content}>
          <Card style={styles.welcomeCard}>
            <Card.Content>
              <Text style={styles.welcomeTitle}>¿Qué quieres comer hoy?</Text>
              <Text style={styles.welcomeSubtitle}>
                Descubre los mejores restaurantes cerca de ti
              </Text>
            </Card.Content>
          </Card>

          {/* Services Title */}
          <Text style={styles.sectionTitle}>Servicios</Text>

          {/* Menu Grid */}
          <View style={styles.menuGrid}>
            {menuOptions.map((option) => (
              <TouchableOpacity
                key={option.id}
                style={styles.menuItem}
                onPress={option.onPress}
              >
                <Card style={styles.menuCard}>
                  <Card.Content style={styles.cardContent}>
                    <Avatar.Icon
                      size={40}
                      icon={option.icon}
                      color="#fff"
                      style={{ backgroundColor: option.color }}
                    />
                    <Text style={styles.menuItemTitle}>{option.title}</Text>
                    <Text style={styles.menuItemSubtitle}>
                      {option.subtitle}
                    </Text>
                  </Card.Content>
                </Card>
              </TouchableOpacity>
            ))}
          </View>

          {/* Stats Section */}
          <Card style={styles.statsCard}>
            <Card.Content>
              <Text style={styles.statsTitle}>Tu actividad</Text>
              <View style={styles.statsRow}>
                <View style={styles.statItem}>
                  <Text style={styles.statNumber}>0</Text>
                  <Text style={styles.statLabel}>Pedidos</Text>
                </View>
                <View style={styles.statDivider} />
                <View style={styles.statItem}>
                  <Text style={styles.statNumber}>$0.00</Text>
                  <Text style={styles.statLabel}>Gastado</Text>
                </View>
                <View style={styles.statDivider} />
                <View style={styles.statItem}>
                  <Text style={styles.statNumber}>0</Text>
                  <Text style={styles.statLabel}>Favoritos</Text>
                </View>
              </View>
            </Card.Content>
          </Card>

          {/* Logout Button */}
          <Button
            mode="contained"
            onPress={handleLogout}
            style={styles.logoutButton}
            labelStyle={styles.logoutButtonText}
            icon="logout"
          >
            Cerrar Sesión
          </Button>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
  },
  loadingText: {
    marginTop: 10,
    color: '#666',
  },
  header: {
    backgroundColor: '#FF6B35',
    padding: 20,
    paddingTop: 20,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  userInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    backgroundColor: '#FF8C5A',
  },
  userText: {
    marginLeft: 15,
  },
  greeting: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.9)',
  },
  userName: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 2,
  },
  userEmail: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.7)',
    marginTop: 2,
  },
  content: {
    padding: 15,
  },
  welcomeCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 20,
    elevation: 2,
  },
  welcomeTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  welcomeSubtitle: {
    fontSize: 14,
    color: '#666',
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  menuGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  menuItem: {
    width: '48%',
    marginBottom: 15,
  },
  menuCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    elevation: 2,
  },
  cardContent: {
    alignItems: 'center',
    padding: 15,
  },
  menuItemTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginTop: 10,
    textAlign: 'center',
  },
  menuItemSubtitle: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
    textAlign: 'center',
  },
  statsCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 20,
    elevation: 2,
  },
  statsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  statItem: {
    alignItems: 'center',
    flex: 1,
  },
  statNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FF6B35',
    marginBottom: 5,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
  },
  statDivider: {
    width: 1,
    height: 30,
    backgroundColor: '#E0E0E0',
  },
  logoutButton: {
    backgroundColor: '#FF3B30',
    borderRadius: 8,
    paddingVertical: 8,
    marginBottom: 20,
  },
  logoutButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
  },
});