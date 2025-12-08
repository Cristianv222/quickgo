# apps/orders/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid

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
    
    class CancellationReason(models.TextChoices):
        CUSTOMER_REQUEST = 'CUSTOMER_REQUEST', 'Solicitado por el Cliente'
        RESTAURANT_UNAVAILABLE = 'RESTAURANT_UNAVAILABLE', 'Restaurante no Disponible'
        DRIVER_UNAVAILABLE = 'DRIVER_UNAVAILABLE', 'Sin Conductor Disponible'
        PAYMENT_FAILED = 'PAYMENT_FAILED', 'Fallo en el Pago'
        OUT_OF_STOCK = 'OUT_OF_STOCK', 'Producto Agotado'
        WRONG_ADDRESS = 'WRONG_ADDRESS', 'Dirección Incorrecta'
        OTHER = 'OTHER', 'Otro'
    
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
        editable=False,
        verbose_name='Número de Pedido'
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Estado',
        db_index=True
    )
    
    # Dirección de Entrega
    delivery_address = models.TextField(
        verbose_name='Dirección de Entrega'
    )
    
    delivery_reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Referencia de Entrega',
        help_text='Ej: Casa blanca con portón negro'
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
    
    delivery_distance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Distancia de Entrega (km)',
        help_text='Distancia desde el restaurante'
    )
    
    # Costos
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Subtotal',
        validators=[MinValueValidator(Decimal('0.00'))]
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
        default=Decimal('0.50'),
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
    
    tax = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Impuestos',
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    tip = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Propina',
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Propina para el repartidor'
    )
    
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total',
        validators=[MinValueValidator(Decimal('0.00'))]
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
    
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ID de Transacción',
        help_text='ID de la transacción de pago'
    )
    
    # Notas y Especificaciones
    special_instructions = models.TextField(
        blank=True,
        verbose_name='Instrucciones Especiales',
        help_text='Notas del cliente para el restaurante o repartidor'
    )
    
    cancellation_reason = models.CharField(
        max_length=30,
        choices=CancellationReason.choices,
        blank=True,
        verbose_name='Razón de Cancelación'
    )
    
    cancellation_notes = models.TextField(
        blank=True,
        verbose_name='Notas de Cancelación'
    )
    
    cancelled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_orders',
        verbose_name='Cancelado por'
    )
    
    # Tiempos
    estimated_preparation_time = models.PositiveIntegerField(
        default=30,
        verbose_name='Tiempo Estimado de Preparación (min)'
    )
    
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
    
    preparing_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='En Preparación desde'
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
    
    # Rating
    is_rated = models.BooleanField(
        default=False,
        verbose_name='Calificado'
    )
    
    # Cupón de descuento (si aplica)
    coupon_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Código de Cupón'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación',
        db_index=True
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
            models.Index(fields=['created_at']),
            models.Index(fields=['is_paid']),
        ]
    
    def __str__(self):
        return f"Pedido #{self.order_number} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        """Genera número de pedido si no existe"""
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)
    
    def _generate_order_number(self):
        """Genera un número de pedido único"""
        # Formato: QG + timestamp + random
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        random_part = uuid.uuid4().hex[:4].upper()
        return f"QG{timestamp[-8:]}{random_part}"
    
    def calculate_totals(self):
        """Calcula todos los totales del pedido"""
        # Calcular subtotal de items
        self.subtotal = sum(item.subtotal for item in self.items.all())
        
        # Calcular delivery_fee basado en distancia o usar el del restaurante
        if not self.delivery_fee:
            self.delivery_fee = self.restaurant.delivery_fee
        
        # Verificar si aplica envío gratis
        if self.restaurant.free_delivery_above and self.subtotal >= self.restaurant.free_delivery_above:
            self.delivery_fee = Decimal('0.00')
        
        # Calcular impuestos (si aplica, ej: 12% IVA)
        # self.tax = (self.subtotal + self.delivery_fee) * Decimal('0.12')
        
        # Calcular total
        self.total = self.subtotal + self.delivery_fee + self.service_fee + self.tax + self.tip - self.discount
        
        self.save(update_fields=['subtotal', 'delivery_fee', 'tax', 'total'])
    
    def calculate_distance(self):
        """Calcula la distancia entre el restaurante y la dirección de entrega"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Radio de la Tierra en km
        
        lat1 = radians(float(self.restaurant.latitude))
        lon1 = radians(float(self.restaurant.longitude))
        lat2 = radians(float(self.delivery_latitude))
        lon2 = radians(float(self.delivery_longitude))
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        self.delivery_distance = round(Decimal(str(distance)), 2)
        self.save(update_fields=['delivery_distance'])
        
        return self.delivery_distance
    
    def can_be_cancelled(self):
        """Verifica si el pedido puede ser cancelado"""
        return self.status in [
            self.Status.PENDING,
            self.Status.CONFIRMED,
        ]
    
    def can_be_rated(self):
        """Verifica si el pedido puede ser calificado"""
        return self.status == self.Status.DELIVERED and not self.is_rated
    
    def cancel(self, reason, notes='', cancelled_by=None):
        """Cancela el pedido"""
        if not self.can_be_cancelled():
            raise ValueError(f"El pedido en estado {self.get_status_display()} no puede ser cancelado")
        
        self.status = self.Status.CANCELLED
        self.cancellation_reason = reason
        self.cancellation_notes = notes
        self.cancelled_by = cancelled_by
        self.cancelled_at = timezone.now()
        self.save()
        
        # Registrar en historial
        OrderStatusHistory.objects.create(
            order=self,
            status=self.Status.CANCELLED,
            notes=f"Cancelado: {self.get_cancellation_reason_display()} - {notes}",
            changed_by=cancelled_by
        )
        
        # Restaurar stock de productos si aplica
        for item in self.items.all():
            if item.product and item.product.track_inventory:
                item.product.increase_stock(item.quantity)
    
    def confirm(self, confirmed_by=None):
        """Confirma el pedido"""
        if self.status != self.Status.PENDING:
            raise ValueError("Solo se pueden confirmar pedidos pendientes")
        
        self.status = self.Status.CONFIRMED
        self.confirmed_at = timezone.now()
        
        # Calcular tiempo estimado de entrega
        prep_time = self.estimated_preparation_time
        delivery_time = self.restaurant.delivery_time_max
        total_minutes = prep_time + delivery_time
        self.estimated_delivery_time = timezone.now() + timezone.timedelta(minutes=total_minutes)
        
        self.save()
        
        # Registrar en historial
        OrderStatusHistory.objects.create(
            order=self,
            status=self.Status.CONFIRMED,
            notes='Pedido confirmado por el restaurante',
            changed_by=confirmed_by
        )
    
    def start_preparing(self, changed_by=None):
        """Marca el pedido como en preparación"""
        if self.status != self.Status.CONFIRMED:
            raise ValueError("Solo se pueden preparar pedidos confirmados")
        
        self.status = self.Status.PREPARING
        self.preparing_at = timezone.now()
        self.save()
        
        OrderStatusHistory.objects.create(
            order=self,
            status=self.Status.PREPARING,
            notes='El restaurante está preparando el pedido',
            changed_by=changed_by
        )
    
    def mark_ready(self, changed_by=None):
        """Marca el pedido como listo para recoger"""
        if self.status != self.Status.PREPARING:
            raise ValueError("El pedido debe estar en preparación")
        
        self.status = self.Status.READY
        self.ready_at = timezone.now()
        self.save()
        
        OrderStatusHistory.objects.create(
            order=self,
            status=self.Status.READY,
            notes='Pedido listo para recoger',
            changed_by=changed_by
        )
    
    def mark_picked_up(self, driver, changed_by=None):
        """Marca el pedido como recogido por el conductor"""
        if self.status != self.Status.READY:
            raise ValueError("El pedido debe estar listo para ser recogido")
        
        self.status = self.Status.PICKED_UP
        self.driver = driver
        self.picked_up_at = timezone.now()
        self.save()
        
        OrderStatusHistory.objects.create(
            order=self,
            status=self.Status.PICKED_UP,
            notes=f'Pedido recogido por {driver.get_full_name()}',
            changed_by=changed_by or driver
        )
    
    def mark_in_transit(self, changed_by=None):
        """Marca el pedido como en camino"""
        if self.status != self.Status.PICKED_UP:
            raise ValueError("El pedido debe estar recogido")
        
        self.status = self.Status.IN_TRANSIT
        self.save()
        
        OrderStatusHistory.objects.create(
            order=self,
            status=self.Status.IN_TRANSIT,
            notes='Pedido en camino al cliente',
            changed_by=changed_by or self.driver
        )
    
    def mark_delivered(self, changed_by=None):
        """Marca el pedido como entregado"""
        if self.status != self.Status.IN_TRANSIT:
            raise ValueError("El pedido debe estar en tránsito")
        
        self.status = self.Status.DELIVERED
        self.delivered_at = timezone.now()
        self.save()
        
        # Actualizar estadísticas del restaurante
        self.restaurant.total_orders += 1
        self.restaurant.total_revenue += self.total
        self.restaurant.save(update_fields=['total_orders', 'total_revenue'])
        
        # Actualizar estadísticas del cliente
        if hasattr(self.customer, 'customer_profile'):
            profile = self.customer.customer_profile
            profile.total_orders += 1
            profile.total_spent += self.total
            profile.save(update_fields=['total_orders', 'total_spent'])
        
        # Actualizar estadísticas del driver
        if self.driver and hasattr(self.driver, 'driver_profile'):
            profile = self.driver.driver_profile
            profile.total_deliveries += 1
            profile.total_earnings += self.delivery_fee + self.tip
            profile.save(update_fields=['total_deliveries', 'total_earnings'])
        
        OrderStatusHistory.objects.create(
            order=self,
            status=self.Status.DELIVERED,
            notes='Pedido entregado al cliente',
            changed_by=changed_by or self.driver
        )
    
    @property
    def total_items(self):
        """Retorna el número total de items"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def preparation_time_elapsed(self):
        """Retorna el tiempo transcurrido desde la confirmación"""
        if self.confirmed_at:
            return (timezone.now() - self.confirmed_at).total_seconds() / 60
        return 0
    
    @property
    def is_delayed(self):
        """Verifica si el pedido está retrasado"""
        if self.estimated_delivery_time and timezone.now() > self.estimated_delivery_time:
            return self.status not in [self.Status.DELIVERED, self.Status.CANCELLED]
        return False


class OrderItem(models.Model):
    """Items/Productos de un Pedido"""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Pedido'
    )
    
    # Referencia al producto original (puede ser null si se elimina)
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
        verbose_name='Producto'
    )
    
    # Snapshot del producto (guardamos la info por si cambia el menú)
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
        verbose_name='Precio Unitario Base',
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Cantidad',
        validators=[MinValueValidator(1)]
    )
    
    # Extras seleccionados (guardados como JSON)
    selected_extras = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Extras Seleccionados',
        help_text='[{"id": 1, "name": "Extra Queso", "price": "1.50", "quantity": 1}]'
    )
    
    # Opciones seleccionadas (guardadas como JSON)
    selected_options = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Opciones Seleccionadas',
        help_text='[{"group": "Tamaño", "option": "Grande", "price_modifier": "2.00"}]'
    )
    
    extras_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total de Extras'
    )
    
    options_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total de Opciones'
    )
    
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Subtotal',
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Notas especiales del cliente
    special_notes = models.TextField(
        blank=True,
        verbose_name='Notas Especiales',
        help_text='Ej: Sin cebolla, poco picante, etc.'
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
        """Calcula totales automáticamente"""
        # Calcular total de extras
        self.extras_total = sum(
            Decimal(str(extra.get('price', 0))) * extra.get('quantity', 1)
            for extra in self.selected_extras
        )
        
        # Calcular total de opciones
        self.options_total = sum(
            Decimal(str(option.get('price_modifier', 0)))
            for option in self.selected_options
        )
        
        # Calcular subtotal: (precio base + opciones + extras) * cantidad
        item_price = self.unit_price + self.options_total + self.extras_total
        self.subtotal = item_price * self.quantity
        
        super().save(*args, **kwargs)
        
        # Recalcular total del pedido
        self.order.calculate_totals()
    
    def get_customizations_display(self):
        """Retorna las personalizaciones en formato legible"""
        customizations = []
        
        # Agregar opciones
        for option in self.selected_options:
            customizations.append(f"{option['group']}: {option['option']}")
        
        # Agregar extras
        for extra in self.selected_extras:
            qty = extra.get('quantity', 1)
            if qty > 1:
                customizations.append(f"{extra['name']} x{qty}")
            else:
                customizations.append(extra['name'])
        
        # Agregar notas especiales
        if self.special_notes:
            customizations.append(f"Nota: {self.special_notes}")
        
        return " | ".join(customizations) if customizations else "Sin personalizaciones"
    
    @property
    def total_price_per_unit(self):
        """Precio total por unidad incluyendo extras y opciones"""
        return self.unit_price + self.options_total + self.extras_total


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
        verbose_name='Fecha',
        db_index=True
    )
    
    class Meta:
        verbose_name = 'Historial de Estado'
        verbose_name_plural = 'Historial de Estados'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pedido #{self.order.order_number} - {self.get_status_display()}"


class OrderRating(models.Model):
    """Calificación del pedido"""
    
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
    
    # Calificaciones específicas
    food_rating = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Calificación de la Comida',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    delivery_rating = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Calificación de la Entrega',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
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
    
    # Feedback general
    comment = models.TextField(
        blank=True,
        verbose_name='Comentario'
    )
    
    would_order_again = models.BooleanField(
        default=True,
        verbose_name='¿Volvería a Ordenar?'
    )
    
    # Aspectos positivos/negativos
    liked_aspects = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Aspectos Positivos',
        help_text='["Rápido", "Buena presentación", etc.]'
    )
    
    disliked_aspects = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Aspectos Negativos',
        help_text='["Llegó frío", "Faltó cubiertos", etc.]'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Calificación'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    class Meta:
        verbose_name = 'Calificación de Pedido'
        verbose_name_plural = 'Calificaciones de Pedidos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Rating Pedido #{self.order.order_number} - {self.overall_rating}⭐"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Marcar el pedido como calificado
        if not self.order.is_rated:
            self.order.is_rated = True
            self.order.save(update_fields=['is_rated'])
        
        # Actualizar rating del driver si aplica
        if self.driver_rating and self.order.driver and hasattr(self.order.driver, 'driver_profile'):
            driver = self.order.driver.driver_profile
            # Recalcular rating del driver
            from django.db.models import Avg
            avg_rating = OrderRating.objects.filter(
                order__driver=self.order.driver,
                driver_rating__isnull=False
            ).aggregate(Avg('driver_rating'))['driver_rating__avg']
            
            if avg_rating:
                driver.rating = round(avg_rating, 2)
                driver.save(update_fields=['rating'])