from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Modelo de usuario personalizado para QuickGo"""
    
    class UserType(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        CUSTOMER = 'CUSTOMER', 'Cliente'
        DRIVER = 'DRIVER', 'Repartidor'
        RESTAURANT = 'RESTAURANT', 'Restaurante'
    
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.CUSTOMER,
        verbose_name='Tipo de Usuario'
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="El número debe estar en formato: '+999999999'. Hasta 15 dígitos."
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=20,
        blank=True,
        verbose_name='Teléfono'
    )
    
    avatar = models.ImageField(
        upload_to='users/avatars/',
        null=True,
        blank=True,
        verbose_name='Foto de Perfil'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    is_verified = models.BooleanField(default=False, verbose_name='Verificado')  # NUEVO
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_user_type_display()})'
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario"""
        return f'{self.first_name} {self.last_name}'.strip()


class Customer(models.Model):
    """Perfil de Cliente"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='customer_profile',
        verbose_name='Usuario'
    )
    
    address = models.TextField(
        blank=True,
        verbose_name='Dirección Principal'
    )
    
    # NUEVO - Referencias del domicilio
    address_reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Referencias',
        help_text='Ej: Casa blanca con portón negro'
    )
    
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Latitud'
    )
    
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Longitud'
    )
    
    # NUEVO - Estadísticas
    total_orders = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de Pedidos'
    )
    
    total_spent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='Total Gastado'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Driver(models.Model):
    """Perfil de Repartidor/Conductor"""
    
    class VehicleType(models.TextChoices):
        BIKE = 'BIKE', 'Bicicleta'
        MOTORCYCLE = 'MOTORCYCLE', 'Motocicleta'
        CAR = 'CAR', 'Automóvil'
    
    # NUEVO - Estados de aprobación
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        APPROVED = 'APPROVED', 'Aprobado'
        REJECTED = 'REJECTED', 'Rechazado'
        SUSPENDED = 'SUSPENDED', 'Suspendido'
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='driver_profile',
        verbose_name='Usuario'
    )
    
    # Información del Vehículo
    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleType.choices,
        verbose_name='Tipo de Vehículo'
    )
    
    vehicle_plate = models.CharField(
        max_length=20,
        verbose_name='Placa del Vehículo'
    )
    
    # NUEVO - Más info del vehículo
    vehicle_brand = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Marca'
    )
    
    vehicle_model = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Modelo'
    )
    
    vehicle_color = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='Color'
    )
    
    # Licencia y Documentos
    license_number = models.CharField(
        max_length=50,
        verbose_name='Número de Licencia'
    )
    
    # NUEVO - Fotos de documentos
    license_photo = models.ImageField(
        upload_to='drivers/licenses/',
        null=True,
        blank=True,
        verbose_name='Foto de Licencia'
    )
    
    vehicle_photo = models.ImageField(
        upload_to='drivers/vehicles/',
        null=True,
        blank=True,
        verbose_name='Foto del Vehículo'
    )
    
    id_photo = models.ImageField(
        upload_to='drivers/ids/',
        null=True,
        blank=True,
        verbose_name='Foto de ID'
    )
    
    # NUEVO - Estado de aprobación
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Estado'
    )
    
    # Disponibilidad
    is_available = models.BooleanField(
        default=False,
        verbose_name='Disponible'
    )
    
    # NUEVO - En línea
    is_online = models.BooleanField(
        default=False,
        verbose_name='En Línea'
    )
    
    # Ubicación Actual
    current_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Latitud Actual'
    )
    
    current_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Longitud Actual'
    )
    
    # Calificación y Estadísticas
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=5.0,
        verbose_name='Calificación'
    )
    
    # NUEVO - Más estadísticas
    total_deliveries = models.PositiveIntegerField(
        default=0,
        verbose_name='Total Entregas'
    )
    
    total_earnings = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='Ganancias Totales'
    )
    
    # NUEVO - Info de aprobación
    notes = models.TextField(
        blank=True,
        verbose_name='Notas del Admin'
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Aprobación'
    )
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_drivers',
        verbose_name='Aprobado por'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Repartidor'
        verbose_name_plural = 'Repartidores'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.get_full_name()} - {self.vehicle_plate}'
    
    # NUEVO - Métodos útiles
    def approve(self, admin_user):
        """Aprobar conductor"""
        from django.utils import timezone
        self.status = self.Status.APPROVED
        self.approved_by = admin_user
        self.approved_at = timezone.now()
        self.save()
    
    def reject(self, reason=''):
        """Rechazar conductor"""
        self.status = self.Status.REJECTED
        if reason:
            self.notes = reason
        self.save()
    
    def suspend(self, reason=''):
        """Suspender conductor"""
        self.status = self.Status.SUSPENDED
        self.is_available = False
        self.is_online = False
        if reason:
            self.notes = reason
        self.save()