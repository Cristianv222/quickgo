from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from apps.users.models import User 

class Restaurant(models.Model):
    """Perfil de Restaurante"""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        APPROVED = 'APPROVED', 'Aprobado'
        REJECTED = 'REJECTED', 'Rechazado'
        SUSPENDED = 'SUSPENDED', 'Suspendido'
    
    class CuisineType(models.TextChoices):
        ECUADORIAN = 'ECUADORIAN', 'Ecuatoriana'
        FAST_FOOD = 'FAST_FOOD', 'Comida Rápida'
        PIZZA = 'PIZZA', 'Pizzería'
        CHINESE = 'CHINESE', 'China'
        MEXICAN = 'MEXICAN', 'Mexicana'
        ITALIAN = 'ITALIAN', 'Italiana'
        SEAFOOD = 'SEAFOOD', 'Mariscos'
        GRILL = 'GRILL', 'Parrillada'
        CHICKEN = 'CHICKEN', 'Pollo'
        BURGER = 'BURGER', 'Hamburguesas'
        BREAKFAST = 'BREAKFAST', 'Desayunos'
        COFFEE = 'COFFEE', 'Cafetería'
        BAKERY = 'BAKERY', 'Panadería'
        HEALTHY = 'HEALTHY', 'Saludable'
        VEGAN = 'VEGAN', 'Vegano'
        DESSERTS = 'DESSERTS', 'Postres'
        OTHER = 'OTHER', 'Otro'
    
    # Usuario propietario
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='restaurant_profile',
        verbose_name='Usuario'
    )
    
    # Información Básica
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre del Restaurante'
    )
    
    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
        verbose_name='Slug'
    )
    
    description = models.TextField(
        verbose_name='Descripción',
        help_text='Descripción del restaurante y tipo de comida'
    )
    
    # Imágenes
    logo = models.ImageField(
        upload_to='restaurants/logos/',
        null=True,
        blank=True,
        verbose_name='Logo'
    )
    
    banner = models.ImageField(
        upload_to='restaurants/banners/',
        null=True,
        blank=True,
        verbose_name='Banner/Portada'
    )
    
    # Tipo de Cocina
    cuisine_type = models.CharField(
        max_length=50,
        choices=CuisineType.choices,
        verbose_name='Tipo de Cocina'
    )
    
    # Contacto
    phone = models.CharField(
        max_length=20,
        verbose_name='Teléfono'
    )
    
    email = models.EmailField(
        verbose_name='Email de Contacto'
    )
    
    # Ubicación
    address = models.TextField(
        verbose_name='Dirección'
    )
    
    address_reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Referencias',
        help_text='Ej: Al lado del parque central'
    )
    
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name='Latitud'
    )
    
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name='Longitud'
    )
    
    # Documentos Legales
    ruc = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='RUC',
        help_text='Registro Único de Contribuyentes'
    )
    
    business_license = models.ImageField(
        upload_to='restaurants/licenses/',
        null=True,
        blank=True,
        verbose_name='Permiso de Funcionamiento'
    )
    
    health_permit = models.ImageField(
        upload_to='restaurants/health_permits/',
        null=True,
        blank=True,
        verbose_name='Permiso Sanitario'
    )
    
    # Estado y Aprobación
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Estado'
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
        related_name='approved_restaurants',
        verbose_name='Aprobado por'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Notas del Admin'
    )
    
    # Horarios y Disponibilidad
    is_open = models.BooleanField(
        default=True,
        verbose_name='Abierto Ahora'
    )
    
    is_accepting_orders = models.BooleanField(
        default=True,
        verbose_name='Aceptando Pedidos'
    )
    
    # Configuración de Entregas
    delivery_time_min = models.PositiveIntegerField(
        default=30,
        verbose_name='Tiempo Mínimo de Entrega (min)',
        help_text='En minutos'
    )
    
    delivery_time_max = models.PositiveIntegerField(
        default=60,
        verbose_name='Tiempo Máximo de Entrega (min)',
        help_text='En minutos'
    )
    
    delivery_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=2.00,
        verbose_name='Costo de Envío',
        validators=[MinValueValidator(0)]
    )
    
    min_order_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=5.00,
        verbose_name='Pedido Mínimo',
        help_text='Monto mínimo para realizar un pedido',
        validators=[MinValueValidator(0)]
    )
    
    free_delivery_above = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Envío Gratis Desde',
        help_text='Monto para envío gratis (opcional)',
        validators=[MinValueValidator(0)]
    )
    
    delivery_radius_km = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5.0,
        verbose_name='Radio de Entrega (km)',
        help_text='Distancia máxima de entrega',
        validators=[MinValueValidator(0.1)]
    )
    
    # Calificación y Estadísticas
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=5.0,
        verbose_name='Calificación',
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    
    total_reviews = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de Reseñas'
    )
    
    total_orders = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de Pedidos'
    )
    
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name='Ingresos Totales'
    )
    
    # Destacados y Promociones
    is_featured = models.BooleanField(
        default=False,
        verbose_name='Destacado',
        help_text='Aparece en la sección destacados'
    )
    
    is_new = models.BooleanField(
        default=False,
        verbose_name='Nuevo',
        help_text='Muestra badge de "Nuevo"'
    )
    
    has_promotion = models.BooleanField(
        default=False,
        verbose_name='Tiene Promoción',
        help_text='Muestra badge de promoción'
    )
    
    promotion_text = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Texto de Promoción',
        help_text='Ej: 2x1 en pizzas'
    )
    
    # Características
    accepts_cash = models.BooleanField(
        default=True,
        verbose_name='Acepta Efectivo'
    )
    
    accepts_card = models.BooleanField(
        default=True,
        verbose_name='Acepta Tarjeta'
    )
    
    has_parking = models.BooleanField(
        default=False,
        verbose_name='Tiene Estacionamiento'
    )
    
    has_wifi = models.BooleanField(
        default=False,
        verbose_name='Tiene WiFi'
    )
    
    is_eco_friendly = models.BooleanField(
        default=False,
        verbose_name='Eco-Friendly',
        help_text='Usa empaques biodegradables'
    )
    
    # Comisión de la Plataforma
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=15.0,
        verbose_name='Tasa de Comisión (%)',
        help_text='Porcentaje que cobra la plataforma',
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # SEO
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Meta Title'
    )
    
    meta_description = models.TextField(
        blank=True,
        verbose_name='Meta Description'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Registro'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    class Meta:
        verbose_name = 'Restaurante'
        verbose_name_plural = 'Restaurantes'
        ordering = ['-is_featured', '-rating', 'name']
        indexes = [
            models.Index(fields=['status', 'is_open']),
            models.Index(fields=['cuisine_type']),
            models.Index(fields=['-rating']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Genera slug automáticamente"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def approve(self, admin_user):
        """Aprobar restaurante"""
        from django.utils import timezone
        self.status = self.Status.APPROVED
        self.approved_by = admin_user
        self.approved_at = timezone.now()
        self.save()
    
    def reject(self, reason=''):
        """Rechazar restaurante"""
        self.status = self.Status.REJECTED
        if reason:
            self.notes = reason
        self.save()
    
    def suspend(self, reason=''):
        """Suspender restaurante"""
        self.status = self.Status.SUSPENDED
        self.is_accepting_orders = False
        if reason:
            self.notes = reason
        self.save()
    
    def calculate_rating(self):
        """Recalcula el rating promedio"""
        from django.db.models import Avg
        avg_rating = self.reviews.aggregate(Avg('rating'))['rating__avg']
        if avg_rating:
            self.rating = round(avg_rating, 2)
            self.save()
    
    def is_within_delivery_radius(self, lat, lon):
        """Verifica si una ubicación está dentro del radio de entrega"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Radio de la Tierra en km
        
        lat1, lon1 = radians(float(self.latitude)), radians(float(self.longitude))
        lat2, lon2 = radians(lat), radians(lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        return distance <= float(self.delivery_radius_km)
    
    @property
    def delivery_time_range(self):
        """Retorna el rango de tiempo de entrega formateado"""
        return f"{self.delivery_time_min}-{self.delivery_time_max} min"
    
    @property
    def is_delivery_free(self):
        """Verifica si el envío es gratis"""
        return self.delivery_fee == 0


class RestaurantSchedule(models.Model):
    """Horario de Atención del Restaurante"""
    
    class DayOfWeek(models.IntegerChoices):
        MONDAY = 1, 'Lunes'
        TUESDAY = 2, 'Martes'
        WEDNESDAY = 3, 'Miércoles'
        THURSDAY = 4, 'Jueves'
        FRIDAY = 5, 'Viernes'
        SATURDAY = 6, 'Sábado'
        SUNDAY = 7, 'Domingo'
    
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='Restaurante'
    )
    
    day_of_week = models.IntegerField(
        choices=DayOfWeek.choices,
        verbose_name='Día de la Semana'
    )
    
    opening_time = models.TimeField(
        verbose_name='Hora de Apertura'
    )
    
    closing_time = models.TimeField(
        verbose_name='Hora de Cierre'
    )
    
    is_closed = models.BooleanField(
        default=False,
        verbose_name='Cerrado',
        help_text='Marcar si el restaurante está cerrado este día'
    )
    
    class Meta:
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'
        ordering = ['day_of_week', 'opening_time']
        unique_together = ['restaurant', 'day_of_week']
    
    def __str__(self):
        if self.is_closed:
            return f"{self.restaurant.name} - {self.get_day_of_week_display()}: Cerrado"
        return f"{self.restaurant.name} - {self.get_day_of_week_display()}: {self.opening_time.strftime('%H:%M')} - {self.closing_time.strftime('%H:%M')}"


class RestaurantReview(models.Model):
    """Reseñas de Restaurantes"""
    
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Restaurante'
    )
    
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='restaurant_reviews',
        verbose_name='Cliente'
    )
    
    order = models.ForeignKey(
        'orders.Order',  # Ajusta según tu app de pedidos
        on_delete=models.CASCADE,
        related_name='restaurant_reviews',
        verbose_name='Pedido',
        null=True,
        blank=True
    )
    
    rating = models.IntegerField(
        verbose_name='Calificación',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Calificación de 1 a 5 estrellas'
    )
    
    comment = models.TextField(
        blank=True,
        verbose_name='Comentario'
    )
    
    # Calificaciones específicas
    food_quality = models.IntegerField(
        verbose_name='Calidad de Comida',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    
    delivery_time = models.IntegerField(
        verbose_name='Tiempo de Entrega',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    
    packaging = models.IntegerField(
        verbose_name='Empaquetado',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    
    # Respuesta del restaurante
    restaurant_response = models.TextField(
        blank=True,
        verbose_name='Respuesta del Restaurante'
    )
    
    response_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Respuesta'
    )
    
    # Estado
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Verificada',
        help_text='El cliente realizó el pedido'
    )
    
    is_visible = models.BooleanField(
        default=True,
        verbose_name='Visible'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    class Meta:
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'
        ordering = ['-created_at']
        unique_together = ['restaurant', 'customer', 'order']
    
    def __str__(self):
        return f"{self.customer.get_full_name()} - {self.restaurant.name} ({self.rating}⭐)"
    
    def save(self, *args, **kwargs):
        """Actualiza el rating del restaurante al guardar"""
        super().save(*args, **kwargs)
        self.restaurant.calculate_rating()


class RestaurantGallery(models.Model):
    """Galería de Fotos del Restaurante"""
    
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='gallery',
        verbose_name='Restaurante'
    )
    
    image = models.ImageField(
        upload_to='restaurants/gallery/',
        verbose_name='Imagen'
    )
    
    caption = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Descripción'
    )
    
    is_featured = models.BooleanField(
        default=False,
        verbose_name='Destacada'
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Subida'
    )
    
    class Meta:
        verbose_name = 'Foto de Galería'
        verbose_name_plural = 'Galería de Fotos'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.restaurant.name} - Foto {self.id}"