# apps/orders/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = get_user_model()


class Order(models.Model):
    """Modelo de Pedido"""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        CONFIRMED = 'CONFIRMED', 'Confirmado'
        PREPARING = 'PREPARING', 'Preparando'
        READY = 'READY', 'Listo para Entrega'
        PICKED_UP = 'PICKED_UP', 'Recogido'
        IN_TRANSIT = 'IN_TRANSIT', 'En Camino'
        DELIVERED = 'DELIVERED', 'Entregado'
        CANCELLED = 'CANCELLED', 'Cancelado'
    
    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', 'Efectivo'
        CARD = 'CARD', 'Tarjeta'
        WALLET = 'WALLET', 'Billetera Digital'
    
    # Relaciones
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='customer_orders',
        verbose_name='Cliente',
        limit_choices_to={'user_type': 'CUSTOMER'}
    )
    
    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Restaurante'
    )
    
    driver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='driver_orders',
        verbose_name='Repartidor',
        limit_choices_to={'user_type': 'DRIVER'}
    )
    
    # Información del Pedido
    order_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de Pedido'
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Estado'
    )
    
    # Dirección de Entrega
    delivery_address = models.TextField(
        verbose_name='Dirección de Entrega'
    )
    
    delivery_reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Referencia de Entrega'
    )
    
    delivery_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name='Latitud de Entrega'
    )
    
    delivery_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name='Longitud de Entrega'
    )
    
    # Costos
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Subtotal',
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    delivery_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Costo de Envío',
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    service_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Tarifa de Servicio',
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    discount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Descuento',
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total',
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Pago
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
        verbose_name='Método de Pago'
    )
    
    is_paid = models.BooleanField(
        default=False,
        verbose_name='Pagado'
    )
    
    payment_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Pago'
    )
    
    # Notas y Especificaciones
    special_instructions = models.TextField(
        blank=True,
        verbose_name='Instrucciones Especiales'
    )
    
    cancellation_reason = models.TextField(
        blank=True,
        verbose_name='Razón de Cancelación'
    )
    
    # Tiempos
    estimated_delivery_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Tiempo Estimado de Entrega'
    )
    
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Confirmado en'
    )
    
    ready_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Listo en'
    )
    
    picked_up_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Recogido en'
    )
    
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Entregado en'
    )
    
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Cancelado en'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['restaurant', 'status']),
            models.Index(fields=['driver', 'status']),
        ]
    
    def __str__(self):
        return f"Pedido #{self.order_number} - {self.customer.get_full_name()}"
    
    def save(self, *args, **kwargs):
        """Genera número de pedido si no existe"""
        if not self.order_number:
            import uuid
            self.order_number = f"QG{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)
    
    def calculate_total(self):
        """Calcula el total del pedido"""
        self.subtotal = sum(item.subtotal for item in self.items.all())
        self.total = self.subtotal + self.delivery_fee + self.service_fee - self.discount
        self.save()
    
    def can_be_cancelled(self):
        """Verifica si el pedido puede ser cancelado"""
        return self.status in [
            self.Status.PENDING,
            self.Status.CONFIRMED,
            self.Status.PREPARING
        ]


class OrderItem(models.Model):
    """Items/Productos de un Pedido"""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Pedido'
    )
    
    # Información del Producto (guardamos snapshot por si cambia el menú)
    product_name = models.CharField(
        max_length=200,
        verbose_name='Nombre del Producto'
    )
    
    product_description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    product_image = models.URLField(
        blank=True,
        verbose_name='Imagen del Producto'
    )
    
    # Precios
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio Unitario',
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Cantidad',
        validators=[MinValueValidator(1)]
    )
    
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Subtotal',
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Personalizaciones (extras, ingredientes removidos, etc)
    customizations = models.TextField(
        blank=True,
        verbose_name='Personalizaciones',
        help_text='Extras, sin cebolla, etc.'
    )
    
    special_notes = models.TextField(
        blank=True,
        verbose_name='Notas Especiales'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    class Meta:
        verbose_name = 'Item de Pedido'
        verbose_name_plural = 'Items de Pedido'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name} - Pedido #{self.order.order_number}"
    
    def save(self, *args, **kwargs):
        """Calcula subtotal automáticamente"""
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
        # Recalcular total del pedido
        self.order.calculate_total()


class OrderStatusHistory(models.Model):
    """Historial de cambios de estado del pedido"""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name='Pedido'
    )
    
    status = models.CharField(
        max_length=20,
        choices=Order.Status.choices,
        verbose_name='Estado'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_status_changes',
        verbose_name='Cambiado por'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha'
    )
    
    class Meta:
        verbose_name = 'Historial de Estado'
        verbose_name_plural = 'Historial de Estados'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pedido #{self.order.order_number} - {self.get_status_display()}"


class OrderRating(models.Model):
    """Calificación del pedido (separado de la reseña del restaurante)"""
    
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='rating',
        verbose_name='Pedido'
    )
    
    # Calificación del servicio en general
    overall_rating = models.IntegerField(
        verbose_name='Calificación General',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='1-5 estrellas'
    )
    
    # Calificación del repartidor
    driver_rating = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Calificación del Repartidor',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    driver_comment = models.TextField(
        blank=True,
        verbose_name='Comentario sobre el Repartidor'
    )
    
    # Feedback adicional
    comment = models.TextField(
        blank=True,
        verbose_name='Comentario'
    )
    
    would_order_again = models.BooleanField(
        default=True,
        verbose_name='¿Volvería a Ordenar?'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Calificación'
    )
    
    class Meta:
        verbose_name = 'Calificación de Pedido'
        verbose_name_plural = 'Calificaciones de Pedidos'
    
    def __str__(self):
        return f"Rating Pedido #{self.order.order_number} - {self.overall_rating}⭐"