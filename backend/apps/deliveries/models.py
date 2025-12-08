# apps/deliveries/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class Delivery(models.Model):
    """Modelo principal de entrega/delivery"""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente de Asignación'
        ASSIGNED = 'ASSIGNED', 'Asignado a Conductor'
        PICKING_UP = 'PICKING_UP', 'Recogiendo Pedido'
        PICKED_UP = 'PICKED_UP', 'Pedido Recogido'
        IN_TRANSIT = 'IN_TRANSIT', 'En Camino al Cliente'
        ARRIVED = 'ARRIVED', 'Llegó a Destino'
        DELIVERED = 'DELIVERED', 'Entregado'
        FAILED = 'FAILED', 'Entrega Fallida'
        CANCELLED = 'CANCELLED', 'Cancelado'
    
    class FailureReason(models.TextChoices):
        CUSTOMER_UNAVAILABLE = 'CUSTOMER_UNAVAILABLE', 'Cliente No Disponible'
        WRONG_ADDRESS = 'WRONG_ADDRESS', 'Dirección Incorrecta'
        CUSTOMER_REJECTED = 'CUSTOMER_REJECTED', 'Cliente Rechazó el Pedido'
        ACCIDENT = 'ACCIDENT', 'Accidente'
        VEHICLE_ISSUE = 'VEHICLE_ISSUE', 'Problema con el Vehículo'
        OTHER = 'OTHER', 'Otro'
    
    # Relaciones
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='delivery',
        verbose_name='Pedido'
    )
    
    driver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries',
        verbose_name='Conductor',
        limit_choices_to={'user_type': 'DRIVER'}
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Estado',
        db_index=True
    )
    
    # Información de pickup (restaurante)
    pickup_address = models.TextField(
        verbose_name='Dirección de Recogida'
    )
    
    pickup_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name='Latitud de Recogida'
    )
    
    pickup_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name='Longitud de Recogida'
    )
    
    # Información de entrega (cliente)
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
    
    # Distancias
    total_distance = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Distancia Total (km)',
        help_text='Distancia total del recorrido'
    )
    
    # Tiempos estimados
    estimated_pickup_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Tiempo Estimado de Recogida'
    )
    
    estimated_delivery_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Tiempo Estimado de Entrega'
    )
    
    # Tiempos reales
    assigned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Asignado en'
    )
    
    pickup_started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Inicio de Recogida'
    )
    
    picked_up_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Recogido en'
    )
    
    in_transit_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='En Tránsito desde'
    )
    
    arrived_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Llegada en'
    )
    
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Entregado en'
    )
    
    failed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fallido en'
    )
    
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Cancelado en'
    )
    
    # Información de falla
    failure_reason = models.CharField(
        max_length=30,
        choices=FailureReason.choices,
        blank=True,
        verbose_name='Razón de Falla'
    )
    
    failure_notes = models.TextField(
        blank=True,
        verbose_name='Notas de Falla'
    )
    
    failure_photo = models.ImageField(
        upload_to='deliveries/failures/',
        null=True,
        blank=True,
        verbose_name='Foto de Evidencia de Falla'
    )
    
    # Confirmación de entrega
    delivery_proof_photo = models.ImageField(
        upload_to='deliveries/proofs/',
        null=True,
        blank=True,
        verbose_name='Foto de Prueba de Entrega'
    )
    
    delivery_signature = models.TextField(
        blank=True,
        verbose_name='Firma Digital del Cliente',
        help_text='Datos de firma digital en formato base64'
    )
    
    delivery_notes = models.TextField(
        blank=True,
        verbose_name='Notas de Entrega',
        help_text='Notas del conductor al entregar'
    )
    
    # Contacto del cliente
    customer_phone = models.CharField(
        max_length=20,
        verbose_name='Teléfono del Cliente'
    )
    
    customer_name = models.CharField(
        max_length=200,
        verbose_name='Nombre del Cliente'
    )
    
    # Instrucciones especiales
    special_instructions = models.TextField(
        blank=True,
        verbose_name='Instrucciones Especiales'
    )
    
    # Costos
    delivery_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Tarifa de Entrega'
    )
    
    tip = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Propina'
    )
    
    driver_earnings = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Ganancias del Conductor',
        help_text='Tarifa de entrega + propina'
    )
    
    # Prioridad
    priority = models.IntegerField(
        default=0,
        verbose_name='Prioridad',
        help_text='Mayor número = mayor prioridad',
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    
    # Intentos de entrega
    delivery_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name='Intentos de Entrega'
    )
    
    max_delivery_attempts = models.PositiveIntegerField(
        default=3,
        verbose_name='Máximo de Intentos'
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
        verbose_name = 'Entrega'
        verbose_name_plural = 'Entregas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['driver', 'status']),
            models.Index(fields=['order']),
            models.Index(fields=['-priority', 'created_at']),
        ]
    
    def __str__(self):
        return f"Entrega #{self.order.order_number} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        """Calcular ganancias del conductor"""
        self.driver_earnings = self.delivery_fee + self.tip
        super().save(*args, **kwargs)
    
    def assign_driver(self, driver):
        """Asignar conductor a la entrega"""
        if self.status != self.Status.PENDING:
            raise ValueError("Solo se pueden asignar conductores a entregas pendientes")
        
        if not driver.user_type == 'DRIVER':
            raise ValueError("El usuario no es un conductor")
        
        if hasattr(driver, 'driver_profile'):
            profile = driver.driver_profile
            if profile.status != 'APPROVED':
                raise ValueError("El conductor no está aprobado")
            if not profile.is_available:
                raise ValueError("El conductor no está disponible")
        
        self.driver = driver
        self.status = self.Status.ASSIGNED
        self.assigned_at = timezone.now()
        
        # Calcular tiempo estimado
        avg_speed = 30  # km/h promedio en ciudad
        if self.total_distance:
            travel_time_minutes = (float(self.total_distance) / avg_speed) * 60
            self.estimated_delivery_time = timezone.now() + timezone.timedelta(
                minutes=travel_time_minutes + 10  # +10 min de margen
            )
        
        self.save()
        
        # Crear registro en historial
        DeliveryStatusHistory.objects.create(
            delivery=self,
            status=self.Status.ASSIGNED,
            notes=f'Asignado a {driver.get_full_name()}',
            changed_by=driver
        )
        
        # Actualizar pedido
        self.order.driver = driver
        self.order.save()
    
    def start_pickup(self):
        """Conductor inicia recogida del pedido"""
        if self.status != self.Status.ASSIGNED:
            raise ValueError("La entrega debe estar asignada")
        
        self.status = self.Status.PICKING_UP
        self.pickup_started_at = timezone.now()
        self.save()
        
        DeliveryStatusHistory.objects.create(
            delivery=self,
            status=self.Status.PICKING_UP,
            notes='Conductor en camino a recoger el pedido',
            changed_by=self.driver
        )
    
    def confirm_pickup(self):
        """Confirmar que se recogió el pedido"""
        if self.status not in [self.Status.ASSIGNED, self.Status.PICKING_UP]:
            raise ValueError("Estado inválido para confirmar recogida")
        
        self.status = self.Status.PICKED_UP
        self.picked_up_at = timezone.now()
        self.save()
        
        DeliveryStatusHistory.objects.create(
            delivery=self,
            status=self.Status.PICKED_UP,
            notes='Pedido recogido del restaurante',
            changed_by=self.driver
        )
        
        # Actualizar pedido
        self.order.status = 'PICKED_UP'
        self.order.picked_up_at = self.picked_up_at
        self.order.save()
    
    def start_transit(self):
        """Iniciar tránsito hacia el cliente"""
        if self.status != self.Status.PICKED_UP:
            raise ValueError("Debe recoger el pedido primero")
        
        self.status = self.Status.IN_TRANSIT
        self.in_transit_at = timezone.now()
        self.save()
        
        DeliveryStatusHistory.objects.create(
            delivery=self,
            status=self.Status.IN_TRANSIT,
            notes='En camino hacia el cliente',
            changed_by=self.driver
        )
        
        # Actualizar pedido
        self.order.status = 'IN_TRANSIT'
        self.order.save()
    
    def mark_arrived(self):
        """Marcar llegada al destino"""
        if self.status != self.Status.IN_TRANSIT:
            raise ValueError("Debe estar en tránsito")
        
        self.status = self.Status.ARRIVED
        self.arrived_at = timezone.now()
        self.save()
        
        DeliveryStatusHistory.objects.create(
            delivery=self,
            status=self.Status.ARRIVED,
            notes='Conductor llegó al destino',
            changed_by=self.driver
        )
    
    def complete_delivery(self, proof_photo=None, signature=None, notes=''):
        """Completar la entrega"""
        if self.status not in [self.Status.IN_TRANSIT, self.Status.ARRIVED]:
            raise ValueError("Estado inválido para completar entrega")
        
        self.status = self.Status.DELIVERED
        self.delivered_at = timezone.now()
        self.delivery_proof_photo = proof_photo
        self.delivery_signature = signature
        self.delivery_notes = notes
        self.save()
        
        DeliveryStatusHistory.objects.create(
            delivery=self,
            status=self.Status.DELIVERED,
            notes=f'Entrega completada. {notes}',
            changed_by=self.driver
        )
        
        # Actualizar pedido
        self.order.status = 'DELIVERED'
        self.order.delivered_at = self.delivered_at
        self.order.save()
        
        # Actualizar estadísticas del conductor
        if self.driver and hasattr(self.driver, 'driver_profile'):
            profile = self.driver.driver_profile
            profile.total_deliveries += 1
            profile.total_earnings += self.driver_earnings
            profile.is_available = True  # Queda disponible para nuevas entregas
            profile.save()
    
    def mark_failed(self, reason, notes='', photo=None):
        """Marcar entrega como fallida"""
        if self.status in [self.Status.DELIVERED, self.Status.CANCELLED]:
            raise ValueError("No se puede marcar como fallida una entrega completada o cancelada")
        
        self.delivery_attempts += 1
        
        if self.delivery_attempts >= self.max_delivery_attempts:
            self.status = self.Status.FAILED
            self.failed_at = timezone.now()
        
        self.failure_reason = reason
        self.failure_notes = notes
        self.failure_photo = photo
        self.save()
        
        DeliveryStatusHistory.objects.create(
            delivery=self,
            status=self.Status.FAILED if self.delivery_attempts >= self.max_delivery_attempts else self.status,
            notes=f'Intento {self.delivery_attempts} fallido: {notes}',
            changed_by=self.driver
        )
        
        # Si falló definitivamente, cancelar el pedido
        if self.status == self.Status.FAILED:
            self.order.status = 'CANCELLED'
            self.order.cancellation_reason = 'DRIVER_UNAVAILABLE'
            self.order.cancellation_notes = f'Entrega fallida: {self.get_failure_reason_display()}'
            self.order.cancelled_at = timezone.now()
            self.order.save()
    
    def cancel(self, reason=''):
        """Cancelar la entrega"""
        if self.status in [self.Status.DELIVERED, self.Status.FAILED]:
            raise ValueError("No se puede cancelar una entrega completada o fallida")
        
        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.failure_notes = reason
        self.save()
        
        DeliveryStatusHistory.objects.create(
            delivery=self,
            status=self.Status.CANCELLED,
            notes=f'Entrega cancelada: {reason}',
            changed_by=self.driver
        )
        
        # Liberar al conductor
        if self.driver and hasattr(self.driver, 'driver_profile'):
            self.driver.driver_profile.is_available = True
            self.driver.driver_profile.save()
    
    def calculate_distance(self):
        """Calcular distancia total del recorrido"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Radio de la Tierra en km
        
        # Distancia del pickup al delivery
        lat1 = radians(float(self.pickup_latitude))
        lon1 = radians(float(self.pickup_longitude))
        lat2 = radians(float(self.delivery_latitude))
        lon2 = radians(float(self.delivery_longitude))
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        self.total_distance = round(Decimal(str(distance)), 2)
        self.save(update_fields=['total_distance'])
        
        return self.total_distance
    
    @property
    def is_delayed(self):
        """Verificar si la entrega está retrasada"""
        if self.estimated_delivery_time and self.status not in [
            self.Status.DELIVERED,
            self.Status.FAILED,
            self.Status.CANCELLED
        ]:
            return timezone.now() > self.estimated_delivery_time
        return False
    
    @property
    def total_delivery_time(self):
        """Tiempo total de entrega en minutos"""
        if self.delivered_at and self.created_at:
            delta = self.delivered_at - self.created_at
            return int(delta.total_seconds() / 60)
        return None
    
    @property
    def pickup_time(self):
        """Tiempo de recogida en minutos"""
        if self.picked_up_at and self.assigned_at:
            delta = self.picked_up_at - self.assigned_at
            return int(delta.total_seconds() / 60)
        return None
    
    @property
    def transit_time(self):
        """Tiempo de tránsito en minutos"""
        if self.delivered_at and self.picked_up_at:
            delta = self.delivered_at - self.picked_up_at
            return int(delta.total_seconds() / 60)
        return None


class DeliveryStatusHistory(models.Model):
    """Historial de cambios de estado de la entrega"""
    
    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name='Entrega'
    )
    
    status = models.CharField(
        max_length=20,
        choices=Delivery.Status.choices,
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
        related_name='delivery_status_changes',
        verbose_name='Cambiado por'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha',
        db_index=True
    )
    
    class Meta:
        verbose_name = 'Historial de Estado de Entrega'
        verbose_name_plural = 'Historial de Estados de Entregas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Entrega #{self.delivery.order.order_number} - {self.get_status_display()}"


class DeliveryLocation(models.Model):
    """Tracking de ubicación en tiempo real del conductor"""
    
    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.CASCADE,
        related_name='location_tracking',
        verbose_name='Entrega'
    )
    
    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='location_history',
        verbose_name='Conductor'
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
    
    accuracy = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Precisión (metros)',
        help_text='Precisión del GPS en metros'
    )
    
    speed = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Velocidad (km/h)'
    )
    
    heading = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Dirección (grados)',
        help_text='Dirección del movimiento en grados (0-360)'
    )
    
    battery_level = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Nivel de Batería (%)',
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Timestamp',
        db_index=True
    )
    
    class Meta:
        verbose_name = 'Ubicación de Entrega'
        verbose_name_plural = 'Ubicaciones de Entregas'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['delivery', '-timestamp']),
            models.Index(fields=['driver', '-timestamp']),
        ]
    
    def __str__(self):
        return f"Ubicación - {self.driver.get_full_name()} - {self.timestamp}"


class DeliveryIssue(models.Model):
    """Problemas o incidencias durante la entrega"""
    
    class IssueType(models.TextChoices):
        TRAFFIC = 'TRAFFIC', 'Tráfico Pesado'
        WEATHER = 'WEATHER', 'Mal Clima'
        VEHICLE = 'VEHICLE', 'Problema con Vehículo'
        ACCIDENT = 'ACCIDENT', 'Accidente'
        WRONG_ADDRESS = 'WRONG_ADDRESS', 'Dirección Incorrecta'
        CUSTOMER_ISSUE = 'CUSTOMER_ISSUE', 'Problema con Cliente'
        RESTAURANT_DELAY = 'RESTAURANT_DELAY', 'Retraso del Restaurante'
        OTHER = 'OTHER', 'Otro'
    
    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.CASCADE,
        related_name='issues',
        verbose_name='Entrega'
    )
    
    issue_type = models.CharField(
        max_length=30,
        choices=IssueType.choices,
        verbose_name='Tipo de Problema'
    )
    
    description = models.TextField(
        verbose_name='Descripción'
    )
    
    photo = models.ImageField(
        upload_to='deliveries/issues/',
        null=True,
        blank=True,
        verbose_name='Foto de Evidencia'
    )
    
    reported_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reported_delivery_issues',
        verbose_name='Reportado por'
    )
    
    is_resolved = models.BooleanField(
        default=False,
        verbose_name='Resuelto'
    )
    
    resolution_notes = models.TextField(
        blank=True,
        verbose_name='Notas de Resolución'
    )
    
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Resuelto en'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Reporte'
    )
    
    class Meta:
        verbose_name = 'Problema de Entrega'
        verbose_name_plural = 'Problemas de Entregas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_issue_type_display()} - Entrega #{self.delivery.order.order_number}"