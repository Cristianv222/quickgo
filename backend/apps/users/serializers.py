from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, Customer, Driver


# ========================================
# USER SERIALIZERS
# ========================================

class UserSerializer(serializers.ModelSerializer):
    """Serializer básico para User"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone',
            'avatar',
            'user_type',
            'is_verified',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_verified']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


# ========================================
# CUSTOMER SERIALIZERS
# ========================================

class CustomerSerializer(serializers.ModelSerializer):
    """Serializer para Customer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            'id',
            'user',
            'address',
            'address_reference',
            'latitude',
            'longitude',
            'total_orders',
            'total_spent',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'total_orders', 'total_spent', 'created_at', 'updated_at']


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro de clientes"""
    # Campos del User
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Confirmar contraseña")
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    
    # Campos del Customer (opcionales)
    address = serializers.CharField(required=False, allow_blank=True)
    address_reference = serializers.CharField(required=False, allow_blank=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    
    class Meta:
        model = Customer
        fields = [
            'email',
            'password',
            'password2',
            'first_name',
            'last_name',
            'phone',
            'address',
            'address_reference',
            'latitude',
            'longitude'
        ]
    
    def validate_email(self, value):
        """Validar que el email no exista"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value.lower()
    
    def validate_phone(self, value):
        """Validar formato de teléfono"""
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Este teléfono ya está registrado.")
        return value
    
    def validate(self, attrs):
        """Validar que las contraseñas coincidan"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Las contraseñas no coinciden."})
        return attrs
    
    def create(self, validated_data):
        """Crear usuario y perfil de cliente"""
        # Extraer datos del customer
        address = validated_data.pop('address', '')
        address_reference = validated_data.pop('address_reference', '')
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        
        # Extraer password2 (no se usa)
        validated_data.pop('password2')
        
        # Crear usuario
        email = validated_data['email']
        user = User.objects.create_user(
            username=email,  # Usar email como username
            email=email,
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data['phone'],
            user_type='CUSTOMER'
        )
        
        # Crear perfil de cliente
        customer = Customer.objects.create(
            user=user,
            address=address,
            address_reference=address_reference,
            latitude=latitude,
            longitude=longitude
        )
        
        return customer


# ========================================
# DRIVER SERIALIZERS
# ========================================

class DriverSerializer(serializers.ModelSerializer):
    """Serializer para Driver"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Driver
        fields = [
            'id',
            'user',
            'vehicle_type',
            'vehicle_plate',
            'vehicle_brand',
            'vehicle_model',
            'vehicle_color',
            'license_number',
            'license_photo',
            'vehicle_photo',
            'id_photo',
            'status',
            'is_available',
            'is_online',
            'current_latitude',
            'current_longitude',
            'rating',
            'total_deliveries',
            'total_earnings',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'user',
            'status',
            'rating',
            'total_deliveries',
            'total_earnings',
            'created_at',
            'updated_at'
        ]


class DriverRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro de conductores"""
    
    # Definir las opciones de tipo de vehículo directamente aquí
    VEHICLE_TYPES = [
        ('MOTORCYCLE', 'Motocicleta'),
        ('CAR', 'Auto'),
        ('VAN', 'Camioneta'),
        ('TRUCK', 'Camión'),
    ]
    
    # Campos del User
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Confirmar contraseña")
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    
    # Campos del Driver
    vehicle_type = serializers.ChoiceField(choices=VEHICLE_TYPES, required=True)
    vehicle_plate = serializers.CharField(required=True)
    license_number = serializers.CharField(required=True)
    
    # Campos opcionales
    vehicle_brand = serializers.CharField(required=False, allow_blank=True)
    vehicle_model = serializers.CharField(required=False, allow_blank=True)
    vehicle_color = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Driver
        fields = [
            'email',
            'password',
            'password2',
            'first_name',
            'last_name',
            'phone',
            'vehicle_type',
            'vehicle_plate',
            'vehicle_brand',
            'vehicle_model',
            'vehicle_color',
            'license_number'
        ]
    
    def validate_email(self, value):
        """Validar que el email no exista"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value.lower()
    
    def validate_phone(self, value):
        """Validar formato de teléfono"""
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Este teléfono ya está registrado.")
        return value
    
    def validate_vehicle_plate(self, value):
        """Validar que la placa no exista"""
        if Driver.objects.filter(vehicle_plate=value).exists():
            raise serializers.ValidationError("Esta placa ya está registrada.")
        return value.upper()
    
    def validate_license_number(self, value):
        """Validar que la licencia no exista"""
        if Driver.objects.filter(license_number=value).exists():
            raise serializers.ValidationError("Este número de licencia ya está registrado.")
        return value
    
    def validate(self, attrs):
        """Validar que las contraseñas coincidan"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Las contraseñas no coinciden."})
        return attrs
    
    def create(self, validated_data):
        """Crear usuario y perfil de conductor"""
        # Extraer datos del driver
        vehicle_type = validated_data.pop('vehicle_type')
        vehicle_plate = validated_data.pop('vehicle_plate')
        vehicle_brand = validated_data.pop('vehicle_brand', '')
        vehicle_model = validated_data.pop('vehicle_model', '')
        vehicle_color = validated_data.pop('vehicle_color', '')
        license_number = validated_data.pop('license_number')
        
        # Extraer password2 (no se usa)
        validated_data.pop('password2')
        
        # Crear usuario
        email = validated_data['email']
        user = User.objects.create_user(
            username=email,  # Usar email como username
            email=email,
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data['phone'],
            user_type='DRIVER'
        )
        
        # Crear perfil de conductor
        driver = Driver.objects.create(
            user=user,
            vehicle_type=vehicle_type,
            vehicle_plate=vehicle_plate,
            vehicle_brand=vehicle_brand,
            vehicle_model=vehicle_model,
            vehicle_color=vehicle_color,
            license_number=license_number,
            status='PENDING'  # Requiere aprobación
        )
        
        return driver


# ========================================
# AUTHENTICATION SERIALIZERS
# ========================================

class LoginSerializer(serializers.Serializer):
    """Serializer para login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        """Validar credenciales"""
        email = attrs.get('email').lower()
        password = attrs.get('password')
        
        # Buscar usuario por email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Credenciales inválidas.")
        
        # Autenticar con username (ya que Django usa username)
        user = authenticate(username=user.username, password=password)
        
        if not user:
            raise serializers.ValidationError("Credenciales inválidas.")
        
        if not user.is_active:
            raise serializers.ValidationError("Esta cuenta está desactivada.")
        
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para cambiar contraseña"""
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, required=True)
    
    def validate_old_password(self, value):
        """Validar contraseña actual"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta.")
        return value
    
    def validate(self, attrs):
        """Validar que las nuevas contraseñas coincidan"""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password2": "Las contraseñas no coinciden."})
        return attrs
    
    def save(self, **kwargs):
        """Guardar nueva contraseña"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Serializer para actualizar perfil de usuario"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar']
    
    def validate_phone(self, value):
        """Validar que el teléfono no esté en uso por otro usuario"""
        user = self.context['request'].user
        if User.objects.filter(phone=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("Este teléfono ya está en uso.")
        return value


class UpdateCustomerAddressSerializer(serializers.ModelSerializer):
    """Serializer para actualizar dirección del cliente"""
    
    class Meta:
        model = Customer
        fields = ['address', 'address_reference', 'latitude', 'longitude']


class UpdateDriverLocationSerializer(serializers.ModelSerializer):
    """Serializer para actualizar ubicación del conductor"""
    
    class Meta:
        model = Driver
        fields = ['current_latitude', 'current_longitude', 'is_online']