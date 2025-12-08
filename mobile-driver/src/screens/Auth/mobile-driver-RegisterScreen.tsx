import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { authAPI } from '../../api/index';

interface DriverRegistrationScreenProps {
  navigation: any;
}

const DriverRegistrationScreen: React.FC<DriverRegistrationScreenProps> = ({ navigation }) => {
  // Estado del formulario - Paso 1: Información Personal
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [password2, setPassword2] = useState('');

  // Estado del formulario - Paso 2: Información del Vehículo
  const [vehicleType, setVehicleType] = useState<'BIKE' | 'MOTORCYCLE' | 'CAR'>('MOTORCYCLE');
  const [vehiclePlate, setVehiclePlate] = useState('');
  const [vehicleBrand, setVehicleBrand] = useState('');
  const [vehicleModel, setVehicleModel] = useState('');
  const [vehicleColor, setVehicleColor] = useState('');
  const [licenseNumber, setLicenseNumber] = useState('');

  // Estados de UI
  const [currentStep, setCurrentStep] = useState(1);
  const [showPassword, setShowPassword] = useState(false);
  const [showPassword2, setShowPassword2] = useState(false);
  const [loading, setLoading] = useState(false);

  // Validación del Paso 1
  const validateStep1 = () => {
    if (!firstName.trim()) {
      Alert.alert('Error', 'Por favor ingresa tu nombre');
      return false;
    }
    if (!lastName.trim()) {
      Alert.alert('Error', 'Por favor ingresa tu apellido');
      return false;
    }
    if (!email.trim()) {
      Alert.alert('Error', 'Por favor ingresa tu email');
      return false;
    }
    // Validar formato de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      Alert.alert('Error', 'Por favor ingresa un email válido');
      return false;
    }
    if (!phone.trim()) {
      Alert.alert('Error', 'Por favor ingresa tu teléfono');
      return false;
    }
    // Validar formato de teléfono (10 dígitos)
    const phoneRegex = /^\d{10}$/;
    if (!phoneRegex.test(phone.replace(/\D/g, ''))) {
      Alert.alert('Error', 'Por favor ingresa un teléfono válido (10 dígitos)');
      return false;
    }
    if (!password) {
      Alert.alert('Error', 'Por favor ingresa una contraseña');
      return false;
    }
    if (password.length < 8) {
      Alert.alert('Error', 'La contraseña debe tener al menos 8 caracteres');
      return false;
    }
    if (password !== password2) {
      Alert.alert('Error', 'Las contraseñas no coinciden');
      return false;
    }
    return true;
  };

  // Validación del Paso 2
  const validateStep2 = () => {
    if (!vehiclePlate.trim()) {
      Alert.alert('Error', 'Por favor ingresa la placa del vehículo');
      return false;
    }
    if (!vehicleBrand.trim()) {
      Alert.alert('Error', 'Por favor ingresa la marca del vehículo');
      return false;
    }
    if (!vehicleModel.trim()) {
      Alert.alert('Error', 'Por favor ingresa el modelo del vehículo');
      return false;
    }
    if (!vehicleColor.trim()) {
      Alert.alert('Error', 'Por favor ingresa el color del vehículo');
      return false;
    }
    if (!licenseNumber.trim()) {
      Alert.alert('Error', 'Por favor ingresa tu número de licencia');
      return false;
    }
    return true;
  };

  // Avanzar al siguiente paso
  const handleNextStep = () => {
    if (currentStep === 1 && validateStep1()) {
      setCurrentStep(2);
    }
  };

  // Volver al paso anterior
  const handlePreviousStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  // Registrar conductor
  const handleRegister = async () => {
    if (!validateStep2()) return;

    setLoading(true);

    try {
      const userData = {
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        email: email.trim().toLowerCase(),
        phone: phone.trim(),
        password: password,
        password2: password2,
        user_type: 'DRIVER' as const,
        vehicle_type: vehicleType,
        vehicle_plate: vehiclePlate.trim().toUpperCase(),
        vehicle_brand: vehicleBrand.trim(),
        vehicle_model: vehicleModel.trim(),
        vehicle_color: vehicleColor.trim(),
        license_number: licenseNumber.trim(),
      };

      const response = await authAPI.register(userData);

      Alert.alert(
        '¡Registro Exitoso!',
        'Tu solicitud está pendiente de aprobación. Te notificaremos cuando sea aprobada.',
        [
          {
            text: 'Entendido',
            onPress: () => navigation.navigate('Login'),
          },
        ]
      );
    } catch (error: any) {
      console.error('Error en registro:', error);
      
      let errorMessage = 'Ocurrió un error al registrarte. Por favor intenta de nuevo.';
      
      if (error.email) {
        errorMessage = error.email[0];
      } else if (error.phone) {
        errorMessage = error.phone[0];
      } else if (error.password) {
        errorMessage = error.password[0];
      } else if (error.message) {
        errorMessage = error.message;
      } else if (typeof error === 'string') {
        errorMessage = error;
      }

      Alert.alert('Error', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Renderizar Paso 1: Información Personal
  const renderStep1 = () => (
    <View style={styles.stepContainer}>
      <Text style={styles.stepTitle}>Información Personal</Text>
      <Text style={styles.stepSubtitle}>Paso 1 de 2</Text>

      {/* Nombre */}
      <View style={styles.inputContainer}>
        <Ionicons name="person-outline" size={20} color="#666" style={styles.inputIcon} />
        <TextInput
          style={styles.input}
          placeholder="Nombre"
          value={firstName}
          onChangeText={setFirstName}
          autoCapitalize="words"
          placeholderTextColor="#999"
        />
      </View>

      {/* Apellido */}
      <View style={styles.inputContainer}>
        <Ionicons name="person-outline" size={20} color="#666" style={styles.inputIcon} />
        <TextInput
          style={styles.input}
          placeholder="Apellido"
          value={lastName}
          onChangeText={setLastName}
          autoCapitalize="words"
          placeholderTextColor="#999"
        />
      </View>

      {/* Email */}
      <View style={styles.inputContainer}>
        <Ionicons name="mail-outline" size={20} color="#666" style={styles.inputIcon} />
        <TextInput
          style={styles.input}
          placeholder="Email"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
          placeholderTextColor="#999"
        />
      </View>

      {/* Teléfono */}
      <View style={styles.inputContainer}>
        <Ionicons name="call-outline" size={20} color="#666" style={styles.inputIcon} />
        <TextInput
          style={styles.input}
          placeholder="Teléfono (10 dígitos)"
          value={phone}
          onChangeText={setPhone}
          keyboardType="phone-pad"
          maxLength={10}
          placeholderTextColor="#999"
        />
      </View>

      {/* Contraseña */}
      <View style={styles.inputContainer}>
        <Ionicons name="lock-closed-outline" size={20} color="#666" style={styles.inputIcon} />
        <TextInput
          style={styles.input}
          placeholder="Contraseña (mínimo 8 caracteres)"
          value={password}
          onChangeText={setPassword}
          secureTextEntry={!showPassword}
          placeholderTextColor="#999"
        />
        <TouchableOpacity
          onPress={() => setShowPassword(!showPassword)}
          style={styles.eyeIcon}
        >
          <Ionicons
            name={showPassword ? 'eye-outline' : 'eye-off-outline'}
            size={20}
            color="#666"
          />
        </TouchableOpacity>
      </View>

      {/* Confirmar Contraseña */}
      <View style={styles.inputContainer}>
        <Ionicons name="lock-closed-outline" size={20} color="#666" style={styles.inputIcon} />
        <TextInput
          style={styles.input}
          placeholder="Confirmar Contraseña"
          value={password2}
          onChangeText={setPassword2}
          secureTextEntry={!showPassword2}
          placeholderTextColor="#999"
        />
        <TouchableOpacity
          onPress={() => setShowPassword2(!showPassword2)}
          style={styles.eyeIcon}
        >
          <Ionicons
            name={showPassword2 ? 'eye-outline' : 'eye-off-outline'}
            size={20}
            color="#666"
          />
        </TouchableOpacity>
      </View>

      <TouchableOpacity
        style={styles.nextButton}
        onPress={handleNextStep}
        activeOpacity={0.8}
      >
        <Text style={styles.nextButtonText}>Siguiente</Text>
        <Ionicons name="arrow-forward" size={20} color="#FFF" />
      </TouchableOpacity>
    </View>
  );

  // Renderizar Paso 2: Información del Vehículo
  const renderStep2 = () => (
    <View style={styles.stepContainer}>
      <Text style={styles.stepTitle}>Información del Vehículo</Text>
      <Text style={styles.stepSubtitle}>Paso 2 de 2</Text>

      {/* Tipo de Vehículo */}
      <Text style={styles.label}>Tipo de Vehículo</Text>
      <View style={styles.vehicleTypeContainer}>
        <TouchableOpacity
          style={[
            styles.vehicleTypeButton,
            vehicleType === 'BIKE' && styles.vehicleTypeButtonActive,
          ]}
          onPress={() => setVehicleType('BIKE')}
        >
          <Ionicons
            name="bicycle"
            size={30}
            color={vehicleType === 'BIKE' ? '#FF6B6B' : '#666'}
          />
          <Text
            style={[
              styles.vehicleTypeText,
              vehicleType === 'BIKE' && styles.vehicleTypeTextActive,
            ]}
          >
            Bicicleta
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            styles.vehicleTypeButton,
            vehicleType === 'MOTORCYCLE' && styles.vehicleTypeButtonActive,
          ]}
          onPress={() => setVehicleType('MOTORCYCLE')}
        >
          <Ionicons
            name="bicycle"
            size={30}
            color={vehicleType === 'MOTORCYCLE' ? '#FF6B6B' : '#666'}
          />
          <Text
            style={[
              styles.vehicleTypeText,
              vehicleType === 'MOTORCYCLE' && styles.vehicleTypeTextActive,
            ]}
          >
            Moto
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            styles.vehicleTypeButton,
            vehicleType === 'CAR' && styles.vehicleTypeButtonActive,
          ]}
          onPress={() => setVehicleType('CAR')}
        >
          <Ionicons
            name="car"
            size={30}
            color={vehicleType === 'CAR' ? '#FF6B6B' : '#666'}
          />
          <Text
            style={[
              styles.vehicleTypeText,
              vehicleType === 'CAR' && styles.vehicleTypeTextActive,
            ]}
          >
            Auto
          </Text>
        </TouchableOpacity>
      </View>

      {/* Placa */}
      <View style={styles.inputContainer}>
        <Ionicons name="card-outline" size={20} color="#666" style={styles.inputIcon} />
        <TextInput
          style={styles.input}
          placeholder="Placa del Vehículo (ABC-123)"
          value={vehiclePlate}
          onChangeText={(text) => setVehiclePlate(text.toUpperCase())}
          autoCapitalize="characters"
          placeholderTextColor="#999"
        />
      </View>

      {/* Marca */}
      <View style={styles.inputContainer}>
        <Ionicons name="car-sport-outline" size={20} color="#666" style={styles.inputIcon} />
        <TextInput
          style={styles.input}
          placeholder="Marca (Honda, Yamaha, Toyota...)"
          value={vehicleBrand}
          onChangeText={setVehicleBrand}
          autoCapitalize="words"
          placeholderTextColor="#999"
        />
      </View>

      {/* Modelo */}
      <View style={styles.inputContainer}>
        <Ionicons name="speedometer-outline" size={20} color="#666" style={styles.inputIcon} />
        <TextInput
          style={styles.input}
          placeholder="Modelo (CBR 250, Corolla...)"
          value={vehicleModel}
          onChangeText={setVehicleModel}
          autoCapitalize="words"
          placeholderTextColor="#999"
        />
      </View>

      {/* Color */}
      <View style={styles.inputContainer}>
        <Ionicons name="color-palette-outline" size={20} color="#666" style={styles.inputIcon} />
        <TextInput
          style={styles.input}
          placeholder="Color"
          value={vehicleColor}
          onChangeText={setVehicleColor}
          autoCapitalize="words"
          placeholderTextColor="#999"
        />
      </View>

      {/* Número de Licencia */}
      <View style={styles.inputContainer}>
        <Ionicons name="id-card-outline" size={20} color="#666" style={styles.inputIcon} />
        <TextInput
          style={styles.input}
          placeholder="Número de Licencia"
          value={licenseNumber}
          onChangeText={setLicenseNumber}
          autoCapitalize="characters"
          placeholderTextColor="#999"
        />
      </View>

      <View style={styles.buttonRow}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={handlePreviousStep}
          activeOpacity={0.8}
        >
          <Ionicons name="arrow-back" size={20} color="#FF6B6B" />
          <Text style={styles.backButtonText}>Atrás</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.registerButton}
          onPress={handleRegister}
          disabled={loading}
          activeOpacity={0.8}
        >
          {loading ? (
            <ActivityIndicator color="#FFF" />
          ) : (
            <>
              <Text style={styles.registerButtonText}>Registrarse</Text>
              <Ionicons name="checkmark-circle" size={20} color="#FFF" />
            </>
          )}
        </TouchableOpacity>
      </View>

      <Text style={styles.infoText}>
        Tu solicitud será revisada y te notificaremos cuando sea aprobada.
      </Text>
    </View>
  );

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={styles.backIconButton}
          >
            <Ionicons name="arrow-back" size={24} color="#333" />
          </TouchableOpacity>
          <View style={styles.logoContainer}>
            <View style={styles.logo}>
              <Ionicons name="bicycle" size={40} color="#FF6B6B" />
            </View>
            <Text style={styles.logoText}>QuickGo Driver</Text>
            <Text style={styles.subtitle}>Únete a nuestro equipo de repartidores</Text>
          </View>
        </View>

        {/* Progress Indicator */}
        <View style={styles.progressContainer}>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                { width: currentStep === 1 ? '50%' : '100%' },
              ]}
            />
          </View>
        </View>

        {/* Renderizar paso actual */}
        {currentStep === 1 ? renderStep1() : renderStep2()}

        {/* Link a Login */}
        <View style={styles.loginContainer}>
          <Text style={styles.loginText}>¿Ya tienes cuenta? </Text>
          <TouchableOpacity onPress={() => navigation.navigate('Login')}>
            <Text style={styles.loginLink}>Inicia Sesión</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 40,
  },
  header: {
    paddingTop: 60,
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  backIconButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#FFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  logoContainer: {
    alignItems: 'center',
  },
  logo: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#FFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  logoText: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  progressContainer: {
    paddingHorizontal: 20,
    marginBottom: 30,
  },
  progressBar: {
    height: 4,
    backgroundColor: '#E0E0E0',
    borderRadius: 2,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#FF6B6B',
  },
  stepContainer: {
    paddingHorizontal: 20,
  },
  stepTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  stepSubtitle: {
    fontSize: 14,
    color: '#999',
    marginBottom: 25,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    borderRadius: 12,
    paddingHorizontal: 15,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  inputIcon: {
    marginRight: 10,
  },
  input: {
    flex: 1,
    height: 50,
    fontSize: 16,
    color: '#333',
  },
  eyeIcon: {
    padding: 5,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 10,
  },
  vehicleTypeContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  vehicleTypeButton: {
    flex: 1,
    alignItems: 'center',
    padding: 15,
    marginHorizontal: 5,
    backgroundColor: '#FFF',
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#E0E0E0',
  },
  vehicleTypeButtonActive: {
    borderColor: '#FF6B6B',
    backgroundColor: '#FFF5F5',
  },
  vehicleTypeText: {
    marginTop: 8,
    fontSize: 12,
    color: '#666',
    fontWeight: '500',
  },
  vehicleTypeTextActive: {
    color: '#FF6B6B',
    fontWeight: '600',
  },
  nextButton: {
    flexDirection: 'row',
    backgroundColor: '#FF6B6B',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 10,
    shadowColor: '#FF6B6B',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  nextButtonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
    marginRight: 8,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 10,
  },
  backButton: {
    flexDirection: 'row',
    flex: 1,
    backgroundColor: '#FFF',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
    borderWidth: 2,
    borderColor: '#FF6B6B',
  },
  backButtonText: {
    color: '#FF6B6B',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  registerButton: {
    flexDirection: 'row',
    flex: 1,
    backgroundColor: '#FF6B6B',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 10,
    shadowColor: '#FF6B6B',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  registerButtonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
    marginRight: 8,
  },
  infoText: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
    marginTop: 15,
    paddingHorizontal: 20,
    lineHeight: 18,
  },
  loginContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 30,
  },
  loginText: {
    fontSize: 14,
    color: '#666',
  },
  loginLink: {
    fontSize: 14,
    color: '#FF6B6B',
    fontWeight: 'bold',
  },
});

export default DriverRegistrationScreen;