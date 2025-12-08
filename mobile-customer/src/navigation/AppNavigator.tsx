// src/navigation/AppNavigator.tsx
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';

// ============================================
// IMPORTAR PANTALLAS
// ============================================

// Auth Screens
import LoginScreen from '../screens/Auth/LoginScreen';
import RegisterScreen from '../screens/Auth/RegisterScreen';

// Customer Screens
import HomeScreen from '../screens/main/HomeScreen';
import ProfileScreen from '../screens/Profile/ProfileScreen';

// Restaurant Screens
import RestaurantsScreen from '../screens/Restaurant/RestaurantsScreen';
import RestaurantDetailScreen from '../screens/Restaurant/RestaurantDetailScreen';
import RestaurantReviewsScreen from '../screens/Restaurant/RestaurantReviewsScreen';
import CreateReviewScreen from '../screens/Restaurant/CreateReviewScreen';
import { MenuScreen } from '../screens/Restaurant/MenuScreen';

// Cart & Order Screens
import { CartScreen } from '../screens/Cart/CartScreen';
import { CheckoutScreen } from '../screens/Cart/CheckoutScreen';
import { OrdersScreen } from '../screens/Orders/OrdersScreen';
import { OrderDetailScreen } from '../screens/Orders/OrderDetailScreen';

// ============================================
// CREAR NAVIGATORS
// ============================================

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();
const AuthStackNav = createNativeStackNavigator();

// ============================================
// BARRA INFERIOR (3 tabs)
// ============================================
const MainTabs = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap = 'home';

          if (route.name === 'HomeTab') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'RestaurantsTab') {
            iconName = focused ? 'restaurant' : 'restaurant-outline';
          } else if (route.name === 'ProfileTab') {
            iconName = focused ? 'person' : 'person-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#FF6B6B',
        tabBarInactiveTintColor: 'gray',
        tabBarStyle: {
          height: 60,
          paddingBottom: 8,
          paddingTop: 8,
        },
        headerShown: false,
      })}
    >
      <Tab.Screen
        name="HomeTab"
        component={HomeScreen}
        options={{ title: 'Inicio' }}
      />
      <Tab.Screen
        name="RestaurantsTab"
        component={RestaurantsScreen}
        options={{ title: 'Restaurantes' }}
      />
      <Tab.Screen
        name="ProfileTab"
        component={ProfileScreen}
        options={{ title: 'Perfil' }}
      />
    </Tab.Navigator>
  );
};

// ============================================
// STACK DE AUTENTICACIÓN (Login/Register)
// ============================================
const AuthStack = () => {
  return (
    <AuthStackNav.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <AuthStackNav.Screen
        name="Login"
        component={LoginScreen}
      />
      <AuthStackNav.Screen
        name="Register"
        component={RegisterScreen}
      />
    </AuthStackNav.Navigator>
  );
};

// ============================================
// STACK PRINCIPAL (después de login)
// ============================================
const MainStack = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: true,
      }}
    >
      <Stack.Screen
        name="MainTabs"
        component={MainTabs}
        options={{ headerShown: false }}
      />

      <Stack.Screen
        name="RestaurantDetail"
        component={RestaurantDetailScreen}
        options={{
          headerShown: false,
          presentation: 'card',
        }}
      />
      <Stack.Screen
        name="RestaurantReviews"
        component={RestaurantReviewsScreen}
        options={{
          title: 'Reseñas',
          headerBackTitle: 'Volver',
          headerTintColor: '#FF6B6B',
        }}
      />
      <Stack.Screen
        name="CreateReview"
        component={CreateReviewScreen}
        options={{
          title: 'Escribir Reseña',
          headerBackTitle: 'Cancelar',
          headerTintColor: '#FF6B6B',
        }}
      />

      {/* Menu & Order Screens */}
      <Stack.Screen
        name="Menu"
        component={MenuScreen}
        options={{
          title: 'Menú',
          headerBackTitle: 'Volver',
          headerTintColor: '#FF6B6B',
        }}
      />
      <Stack.Screen
        name="Cart"
        component={CartScreen}
        options={{
          title: 'Carrito',
          headerBackTitle: 'Volver',
          headerTintColor: '#FF6B6B',
        }}
      />
      <Stack.Screen
        name="Checkout"
        component={CheckoutScreen}
        options={{
          title: 'Finalizar Pedido',
          headerBackTitle: 'Volver',
          headerTintColor: '#FF6B6B',
        }}
      />
      <Stack.Screen
        name="Orders"
        component={OrdersScreen}
        options={{
          title: 'Mis Órdenes',
          headerBackTitle: 'Volver',
          headerTintColor: '#FF6B6B',
        }}
      />
      <Stack.Screen
        name="OrderDetail"
        component={OrderDetailScreen}
        options={{
          title: 'Detalle de Orden',
          headerBackTitle: 'Volver',
          headerTintColor: '#FF6B6B',
        }}
      />
    </Stack.Navigator>
  );
};

// ============================================
// NAVEGADOR PRINCIPAL
// ============================================
const AppNavigator = () => {
  const { isAuthenticated } = useAuth();

  return (
    <NavigationContainer>
      {isAuthenticated ? <MainStack /> : <AuthStack />}
    </NavigationContainer>
  );
};

export default AppNavigator;