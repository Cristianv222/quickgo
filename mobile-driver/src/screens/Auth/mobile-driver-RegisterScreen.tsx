import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { authAPI } from '../../api';

export default function RegisterScreen({ navigation }: any) {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    password: '',
    password2: '',
    vehicle_type: 'MOTORCYCLE',
    vehicle_plate: '',
    vehicle_brand: '',
    vehicle_model: '',
    vehicle_color: '',
    license_number: '',
  });
  const [loading, setLoading] = useState(false);

  const updateField = (field: string, value: string) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleRegister = async () => {
    // Validación de campos básicos
    if (
      !formData.first_name ||
      !formData.last_name ||
      !formData.email ||
      !formData.phone ||
      !formData.password ||
      !formData.password2
    ) {
      Alert.alert('Error', 'Por favor completa todos los campos obligatorios');
      return;
    }

    // Validación de campos del vehículo
    if (
      !formData.vehicle_plate ||
      !formData.vehicle_brand ||
      !formData.license_number
    ) {
      Alert.alert('Error', 'Por favor completa todos los campos del vehículo');
      return;
    }

    if (formData.password !== formData.password2) {
      Alert.alert('Error', 'Las contraseñas no coinciden');
      return;
    }

    if (formData.password.length < 8) {
      Alert.alert('Error', 'La contraseña debe tener al menos 8 caracteres');
      return;
    }

    setLoading(true);
    try {
      const response = await authAPI.register(formData);

      Alert.alert(
        '¡Registro Exitoso!',
        'Tu solicitud está pendiente de aprobación. Te notificaremos cuando sea aprobada.',
        [
          {
            text: 'OK',
            onPress: () => navigation.replace('Login'),
          },
        ]
      );
    } catch (error: any) {
      console.error('Error de registro:', error);
      
      let errorMessage = 'Error al registrarse. Intenta nuevamente.';
      
      if (error?.email) {
        errorMessage = Array.isArray(error.email) ? error.email[0] : error.email;
      } else if (error?.phone) {
        errorMessage = Array.isArray(error.phone) ? error.phone[0] : error.phone;
      } else if (error?.vehicle_plate) {
        errorMessage = Array.isArray(error.vehicle_plate) ? error.vehicle_plate[0] : error.vehicle_plate;
      } else if (error?.license_number) {
        errorMessage = Array.isArray(error.license_number) ? error.license_number[0] : error.license_number;
      } else if (error?.password) {
        errorMessage = Array.isArray(error.password) ? error.password[0] : error.password;
      } else if (typeof error === 'string') {
        errorMessage = error;
      }

      Alert.alert('Error', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.content}>
          {/* Header */}
          <View style={styles.header}>
            <View style={styles.logoContainer}>
              <Ionicons name="bicycle" size={60} color="#007bff" />
            </View>
            <Text style={styles.title}>Regístrate como Repartidor</Text>
            <Text style={styles.subtitle}>Únete a QuickGo Driver</Text>
          </View>

          <View style={styles.form}>
            {/* Información Personal */}
            <View style={styles.sectionHeader}>
              <Ionicons  name="person" size={20} color="#007bff" />
              <Text style={styles.sectionTitle}>Información Personal</Text>
            </View>

            <View style={styles.inputContainer}>
              <View style={styles.labelContainer}>
                <Ionicons name="person-outline" size={14} color="#495057" />
                <Text style={styles.label}>Nombre *</Text>
              </View>
              <TextInput
                style={styles.input}
                placeholder="Juan"
                value={formData.first_name}
                onChangeText={(value) => updateField('first_name', value)}
                editable={!loading}
              />
            </View>

            <View style={styles.inputContainer}>
              <View style={styles.labelContainer}>
                <Ionicons name="person-outline" size={14} color="#495057" />
                <Text style={styles.label}>Apellido *</Text>
              </View>
              <TextInput
                style={styles.input}
                placeholder="Pérez"
                value={formData.last_name}
                onChangeText={(value) => updateField('last_name', value)}
                editable={!loading}
              />
            </View>

            <View style={styles.inputContainer}>
              <View style={styles.labelContainer}>
                <Ionicons name="mail-outline" size={14} color="#495057" />
                <Text style={styles.label}>Email *</Text>
              </View>
              <TextInput
                style={styles.input}
                placeholder="tu@email.com"
                value={formData.email}
                onChangeText={(value) => updateField('email', value)}
                keyboardType="email-address"
                autoCapitalize="none"
                editable={!loading}
              />
            </View>

            <View style={styles.inputContainer}>
              <View style={styles.labelContainer}>
                <Ionicons name="call-outline" size={14} color="#495057" />
                <Text style={styles.label}>Teléfono *</Text>
              </View>
              <TextInput
                style={styles.input}
                placeholder="+593987654321"
                value={formData.phone}
                onChangeText={(value) => updateField('phone', value)}
                keyboardType="phone-pad"
                editable={!loading}
              />
            </View>

            {/* Información del Vehículo */}
            <View style={styles.sectionHeader}>
              <Ionicons name="car-sport" size={20} color="#007bff" />
              <Text style={styles.sectionTitle}>Información del Vehículo</Text>
            </View>

            <View style={styles.inputContainer}>
              <View style={styles.labelContainer}>
                <Ionicons name="list-outline" size={14} color="#495057" />
                <Text style={styles.label}>Tipo de Vehículo *</Text>
              </View>
              <View style={styles.vehicleTypeContainer}>
                {[
                  { key: 'BIKE', label: 'Bicicleta', icon: 'bicycle' },
                  { key: 'MOTORCYCLE', label: 'Moto', icon: 'bicycle' },
                  { key: 'CAR', label: 'Auto', icon: 'car' }
                ].map((type) => (
                  <TouchableOpacity
                    key={type.key}
                    style={[
                      styles.vehicleTypeButton,
                      formData.vehicle_type === type.key && styles.vehicleTypeButtonActive
                    ]}
                    onPress={() => updateField('vehicle_type', type.key)}
                    disabled={loading}
                  >
                    <Ionicons 
                      name={type.icon as any} 
                      size={24} 
                      color={formData.vehicle_type === type.key ? '#fff' : '#007bff'}
                    />
                    <Text style={[
                      styles.vehicleTypeButtonText,
                      formData.vehicle_type === type.key && styles.vehicleTypeButtonTextActive
                    ]}>
                      {type.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            <View style={styles.inputContainer}>
              <View style={styles.labelContainer}>
                <Ionicons name="card-outline" size={14} color="#495057" />
                <Text style={styles.label}>Placa del Vehículo *</Text>
              </View>
              <TextInput
                style={styles.input}
                placeholder="ABC-1234"
                value={formData.vehicle_plate}
                onChangeText={(value) => updateField('vehicle_plate', value.toUpperCase())}
                autoCapitalize="characters"
                editable={!loading}
              />
            </View>

            <View style={styles.inputContainer}>
              <View style={styles.labelContainer}>
                <Ionicons name="business-outline" size={14} color="#495057" />
                <Text style={styles.label}>Marca del Vehículo *</Text>
              </View>
              <TextInput
                style={styles.input}
                placeholder="Honda, Yamaha, Toyota..."
                value={formData.vehicle_brand}
                onChangeText={(value) => updateField('vehicle_brand', value)}
                editable={!loading}
              />
            </View>

            <View style={styles.inputContainer}>
              <View style={styles.labelContainer}>
                <Ionicons name="pricetag-outline" size={14} color="#495057" />
                <Text style={styles.label}>Modelo</Text>
              </View>
              <TextInput
                style={styles.input}
                placeholder="CBR 150, Corolla..."
                value={formData.vehicle_model}
                onChangeText={(value) => updateField('vehicle_model', value)}
                editable={!loading}
              />
            </View>

            <View style={styles.inputContainer}>
              <View style={styles.labelContainer}>
                <Ionicons name="color-palette-outline" size={14} color="#495057" />
                <Text style={styles.label}>Color</Text>
              </View>
              <TextInput
                style={styles.input}
                placeholder="Negro, Rojo, Azul..."
                value={formData.vehicle_color}
                onChangeText={(value) => updateField('vehicle_color', value)}
                editable={!loading}
              />
            </View>

            <View style={styles.inputContainer}>
              <View style={styles.labelContainer}>
                <Ionicons name="document-text-outline" size={14} color="#495057" />
                <Text style={styles.label}>Número de Licencia *</Text>
              </View>
              <TextInput
                style={styles.input}
                placeholder="0123456789"
                value={formData.license_number}
                onChangeText={(value) => updateField('license_number', value)}
                editable={!loading}
              />
            </View>

            {/* Contraseñas */}
            <View style={styles.sectionHeader}>
              <Ionicons name="lock-closed" size={20} color="#007bff" />
              <Text style={styles.sectionTitle}>Seguridad</Text>
            </View>

            <View style={styles.inputContainer}>
              <View style={styles.labelContainer}>
                <Ionicons name="lock-closed-outline" size={14} color="#495057" />
                <Text style={styles.label}>Contraseña *</Text>
              </View>
              <TextInput
                style={styles.input}
                placeholder="Mínimo 8 caracteres"
                value={formData.password}
                onChangeText={(value) => updateField('password', value)}
                secureTextEntry
                editable={!loading}
              />
              <Text style={styles.passwordHint}>
                Debe tener al menos 8 caracteres
              </Text>
            </View>

            <View style={styles.inputContainer}>
              <View style={styles.labelContainer}>
                <Ionicons name="lock-closed-outline" size={14} color="#495057" />
                <Text style={styles.label}>Confirmar Contraseña *</Text>
              </View>
              <TextInput
                style={styles.input}
                placeholder="Repite tu contraseña"
                value={formData.password2}
                onChangeText={(value) => updateField('password2', value)}
                secureTextEntry
                editable={!loading}
              />
            </View>

            {/* Botón de Registro */}
            <TouchableOpacity
              style={[styles.button, loading && styles.buttonDisabled]}
              onPress={handleRegister}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <View style={styles.buttonContent}>
                  <Ionicons name="checkmark-circle" size={20} color="#fff" />
                  <Text style={styles.buttonText}>Crear Cuenta</Text>
                </View>
              )}
            </TouchableOpacity>

            {/* Enlace para iniciar sesión */}
            <View style={styles.loginContainer}>
              <Text style={styles.loginText}>¿Ya tienes una cuenta? </Text>
              <TouchableOpacity
                onPress={() => navigation.navigate('Login')}
                disabled={loading}
              >
                <Text style={styles.loginLink}>Inicia sesión</Text>
              </TouchableOpacity>
            </View>

            {/* Nota importante */}
            <View style={styles.noteContainer}>
              <Ionicons name="information-circle" size={20} color="#ffc107" />
              <Text style={styles.noteText}>
                Tu cuenta será revisada y aprobada por el administrador antes de que puedas comenzar a trabajar.
              </Text>
            </View>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  scrollContent: {
    flexGrow: 1,
    paddingVertical: 20,
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
  },
  header: {
    alignItems: 'center',
    marginBottom: 24,
    marginTop: 20,
  },
  logoContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#e3f2fd',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6c757d',
  },
  form: {
    width: '100%',
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginTop: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#007bff',
  },
  inputContainer: {
    marginBottom: 16,
  },
  labelContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 8,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#495057',
  },
  input: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#dee2e6',
    borderRadius: 8,
    padding: 14,
    fontSize: 16,
    color: '#1a1a1a',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  vehicleTypeContainer: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 8,
  },
  vehicleTypeButton: {
    flex: 1,
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#007bff',
    backgroundColor: '#fff',
    gap: 4,
  },
  vehicleTypeButtonActive: {
    backgroundColor: '#007bff',
    borderColor: '#007bff',
  },
  vehicleTypeButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#007bff',
  },
  vehicleTypeButtonTextActive: {
    color: '#fff',
  },
  passwordHint: {
    fontSize: 12,
    color: '#6c757d',
    marginTop: 4,
    marginLeft: 4,
  },
  button: {
    backgroundColor: '#007bff',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 24,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  buttonDisabled: {
    backgroundColor: '#6c757d',
    opacity: 0.7,
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  loginContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  loginText: {
    fontSize: 14,
    color: '#6c757d',
  },
  loginLink: {
    fontSize: 14,
    color: '#007bff',
    fontWeight: 'bold',
  },
  noteContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 8,
    backgroundColor: '#fff3cd',
    padding: 12,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#ffc107',
  },
  noteText: {
    flex: 1,
    fontSize: 12,
    color: '#856404',
    lineHeight: 18,
  },
});