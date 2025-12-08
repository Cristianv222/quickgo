# apps/deliveries/serializers.py
from rest_framework import serializers
from django.utils import timezone
from django.db import transaction

from .models import (
    Delivery,
    DeliveryStatusHistory,
    DeliveryLocation,
    DeliveryIssue
)
from apps.orders.models import Order
from apps.users.models import User


# ============================================================================
# SERIALIZERS DE HISTORIAL Y UBICACIÓN
# ============================================================================

class DeliveryStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer para historial de estados"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    changed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DeliveryStatusHistory
        fields = [
            'id',
            'status',
            'status_display',
            'notes',
            'changed_by',
            'changed_by_name',
            'created_at'
        ]
    
    def get_changed_by_name(self, obj):
        if obj.changed_by:
            return obj.changed_by.get_full_name() or obj.changed_by.username
        return 'Sistema'


class DeliveryLocationSerializer(serializers.ModelSerializer):
    """Serializer para ubicaciones de tracking"""
    
    driver_name = serializers.CharField(source='driver.get_full_name', read_only=True)
    
    class Meta:
        model = DeliveryLocation
        fields = [
            'id',
            'delivery',
            'driver',
            'driver_name',
            'latitude',
            'longitude',
            'accuracy',
            'speed',
            'heading',
            'battery_level',
            'timestamp'
        ]
        read_only_fields = ['delivery', 'driver', 'timestamp']


class DeliveryLocationCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear ubicaciones (desde el conductor)"""
    
    class Meta:
        model = DeliveryLocation
        fields = [
            'latitude',
            'longitude',
            'accuracy',
            'speed',
            'heading',
            'battery_level'
        ]
    
    def validate(self, data):
        """Validar que el conductor tenga una entrega activa"""
        request = self.context.get('request')
        
        # Verificar que el usuario es conductor
        if request.user.user_type != 'DRIVER':
            raise serializers.ValidationError("Solo conductores pueden enviar ubicaciones")
        
        return data


class DeliveryIssueSerializer(serializers.ModelSerializer):
    """Serializer para problemas de entrega"""
    
    issue_type_display = serializers.CharField(source='get_issue_type_display', read_only=True)
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)
    
    class Meta:
        model = DeliveryIssue
        fields = [
            'id',
            'delivery',
            'issue_type',
            'issue_type_display',
            'description',
            'photo',
            'reported_by',
            'reported_by_name',
            'is_resolved',
            'resolution_notes',
            'resolved_at',
            'created_at'
        ]
        read_only_fields = ['reported_by', 'created_at']


class DeliveryIssueCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear problemas"""
    
    class Meta:
        model = DeliveryIssue
        fields = [
            'delivery',
            'issue_type',
            'description',
            'photo'
        ]
    
    def validate_delivery(self, value):
        """Validar que la entrega existe y está activa"""
        if value.status in ['DELIVERED', 'CANCELLED']:
            raise serializers.ValidationError(
                "No se pueden reportar problemas en entregas completadas o canceladas"
            )
        return value


# ============================================================================
# SERIALIZERS DE DELIVERY (LECTURA)
# ============================================================================

class DeliveryListSerializer(serializers.ModelSerializer):
    """Serializer simple para listar entregas"""
    
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    customer_name = serializers.CharField(read_only=True)
    driver_name = serializers.SerializerMethodField()
    restaurant_name = serializers.CharField(source='order.restaurant.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_delayed = serializers.BooleanField(read_only=True)
    total_delivery_time = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Delivery
        fields = [
            'id',
            'order',
            'order_number',
            'driver',
            'driver_name',
            'customer_name',
            'restaurant_name',
            'status',
            'status_display',
            'priority',
            'total_distance',
            'driver_earnings',
            'estimated_delivery_time',
            'is_delayed',
            'total_delivery_time',
            'delivery_attempts',
            'created_at'
        ]
    
    def get_driver_name(self, obj):
        if obj.driver:
            return obj.driver.get_full_name()
        return None


class DeliveryDetailSerializer(serializers.ModelSerializer):
    """Serializer completo de la entrega"""
    
    # Información del pedido
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    order_total = serializers.DecimalField(
        source='order.total',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    order_status = serializers.CharField(source='order.status', read_only=True)
    
    # Información del conductor
    driver_name = serializers.SerializerMethodField()
    driver_phone = serializers.SerializerMethodField()
    driver_vehicle = serializers.SerializerMethodField()
    driver_rating = serializers.SerializerMethodField()
    
    # Información del restaurante
    restaurant_name = serializers.CharField(source='order.restaurant.name', read_only=True)
    restaurant_phone = serializers.CharField(source='order.restaurant.phone', read_only=True)
    restaurant_logo = serializers.ImageField(source='order.restaurant.logo', read_only=True)
    
    # Relaciones
    status_history = DeliveryStatusHistorySerializer(many=True, read_only=True)
    issues = DeliveryIssueSerializer(many=True, read_only=True)
    current_location = serializers.SerializerMethodField()
    
    # Campos calculados
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    failure_reason_display = serializers.CharField(
        source='get_failure_reason_display',
        read_only=True
    )
    is_delayed = serializers.BooleanField(read_only=True)
    total_delivery_time = serializers.IntegerField(read_only=True)
    pickup_time = serializers.IntegerField(read_only=True)
    transit_time = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Delivery
        fields = [
            # IDs
            'id',
            'order',
            'order_number',
            'order_total',
            'order_status',
            
            # Conductor
            'driver',
            'driver_name',
            'driver_phone',
            'driver_vehicle',
            'driver_rating',
            
            # Cliente
            'customer_name',
            'customer_phone',
            
            # Restaurante
            'restaurant_name',
            'restaurant_phone',
            'restaurant_logo',
            
            # Estado
            'status',
            'status_display',
            'priority',
            
            # Ubicaciones
            'pickup_address',
            'pickup_latitude',
            'pickup_longitude',
            'delivery_address',
            'delivery_reference',
            'delivery_latitude',
            'delivery_longitude',
            'current_location',
            
            # Distancias y tiempos
            'total_distance',
            'estimated_pickup_time',
            'estimated_delivery_time',
            'is_delayed',
            'total_delivery_time',
            'pickup_time',
            'transit_time',
            
            # Timestamps
            'assigned_at',
            'pickup_started_at',
            'picked_up_at',
            'in_transit_at',
            'arrived_at',
            'delivered_at',
            'failed_at',
            'cancelled_at',
            
            # Costos
            'delivery_fee',
            'tip',
            'driver_earnings',
            
            # Instrucciones
            'special_instructions',
            
            # Prueba de entrega
            'delivery_proof_photo',
            'delivery_signature',
            'delivery_notes',
            
            # Fallos
            'delivery_attempts',
            'max_delivery_attempts',
            'failure_reason',
            'failure_reason_display',
            'failure_notes',
            'failure_photo',
            
            # Relaciones
            'status_history',
            'issues',
            
            # Sistema
            'created_at',
            'updated_at'
        ]
    
    def get_driver_name(self, obj):
        if obj.driver:
            return obj.driver.get_full_name()
        return None
    
    def get_driver_phone(self, obj):
        if obj.driver:
            return obj.driver.phone
        return None
    
    def get_driver_vehicle(self, obj):
        if obj.driver and hasattr(obj.driver, 'driver_profile'):
            profile = obj.driver.driver_profile
            return {
                'type': profile.get_vehicle_type_display(),
                'plate': profile.vehicle_plate,
                'brand': profile.vehicle_brand,
                'model': profile.vehicle_model,
                'color': profile.vehicle_color
            }
        return None
    
    def get_driver_rating(self, obj):
        if obj.driver and hasattr(obj.driver, 'driver_profile'):
            return float(obj.driver.driver_profile.rating)
        return None
    
    def get_current_location(self, obj):
        """Obtener la ubicación más reciente del conductor"""
        if obj.driver and hasattr(obj.driver, 'driver_profile'):
            profile = obj.driver.driver_profile
            if profile.current_latitude and profile.current_longitude:
                return {
                    'latitude': float(profile.current_latitude),
                    'longitude': float(profile.current_longitude)
                }
        
        # Si no hay en el perfil, buscar la última ubicación registrada
        last_location = obj.location_tracking.first()
        if last_location:
            return {
                'latitude': float(last_location.latitude),
                'longitude': float(last_location.longitude),
                'timestamp': last_location.timestamp
            }
        
        return None


# ============================================================================
# SERIALIZERS DE DELIVERY (ESCRITURA)
# ============================================================================

class DeliveryCreateSerializer(serializers.Serializer):
    """Serializer para crear una entrega (automático al crear pedido)"""
    
    order_id = serializers.IntegerField()
    priority = serializers.IntegerField(min_value=0, max_value=10, default=0)
    
    def validate_order_id(self, value):
        """Validar que el pedido existe y no tiene entrega"""
        try:
            order = Order.objects.get(id=value)
            
            # Verificar que el pedido está confirmado o listo
            if order.status not in ['CONFIRMED', 'PREPARING', 'READY']:
                raise serializers.ValidationError(
                    "Solo se pueden crear entregas para pedidos confirmados, en preparación o listos"
                )
            
            # Verificar que no tenga entrega ya
            if hasattr(order, 'delivery'):
                raise serializers.ValidationError("Este pedido ya tiene una entrega asignada")
            
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("El pedido no existe")
    
    @transaction.atomic
    def create(self, validated_data):
        """Crear la entrega"""
        order = Order.objects.get(id=validated_data['order_id'])
        restaurant = order.restaurant
        
        # Crear entrega
        delivery = Delivery.objects.create(
            order=order,
            status=Delivery.Status.PENDING,
            priority=validated_data.get('priority', 0),
            
            # Pickup (restaurante)
            pickup_address=restaurant.address,
            pickup_latitude=restaurant.latitude,
            pickup_longitude=restaurant.longitude,
            
            # Delivery (cliente)
            delivery_address=order.delivery_address,
            delivery_reference=order.delivery_reference,
            delivery_latitude=order.delivery_latitude,
            delivery_longitude=order.delivery_longitude,
            
            # Cliente
            customer_name=order.customer.get_full_name() or order.customer.username,
            customer_phone=order.customer.phone or '',
            
            # Costos
            delivery_fee=order.delivery_fee,
            tip=order.tip,
            
            # Instrucciones
            special_instructions=order.special_instructions
        )
        
        # Calcular distancia
        delivery.calculate_distance()
        
        # Crear historial inicial
        DeliveryStatusHistory.objects.create(
            delivery=delivery,
            status=Delivery.Status.PENDING,
            notes='Entrega creada, esperando asignación de conductor'
        )
        
        return delivery


class DeliveryAssignSerializer(serializers.Serializer):
    """Serializer para asignar conductor"""
    
    driver_id = serializers.IntegerField()
    
    def validate_driver_id(self, value):
        """Validar que el conductor existe y está disponible"""
        try:
            driver = User.objects.get(id=value, user_type='DRIVER')
            
            if not hasattr(driver, 'driver_profile'):
                raise serializers.ValidationError("El conductor no tiene perfil configurado")
            
            profile = driver.driver_profile
            
            if profile.status != 'APPROVED':
                raise serializers.ValidationError("El conductor no está aprobado")
            
            if not profile.is_available:
                raise serializers.ValidationError("El conductor no está disponible")
            
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("El conductor no existe")


class DeliveryProofSerializer(serializers.Serializer):
    """Serializer para prueba de entrega"""
    
    proof_photo = serializers.ImageField(required=False, allow_null=True)
    signature = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    def validate(self, data):
        """Validar que al menos haya foto o firma"""
        if not data.get('proof_photo') and not data.get('signature'):
            raise serializers.ValidationError(
                "Debe proporcionar al menos una foto o firma como prueba de entrega"
            )
        return data


class DeliveryFailSerializer(serializers.Serializer):
    """Serializer para marcar entrega como fallida"""
    
    reason = serializers.ChoiceField(choices=Delivery.FailureReason.choices)
    notes = serializers.CharField(max_length=500)
    photo = serializers.ImageField(required=False, allow_null=True)


class DeliveryCancelSerializer(serializers.Serializer):
    """Serializer para cancelar entrega"""
    
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)


# ============================================================================
# SERIALIZER DE TRACKING
# ============================================================================

class DeliveryTrackingSerializer(serializers.Serializer):
    """Serializer para tracking en tiempo real"""
    
    def to_representation(self, instance):
        """Generar datos de tracking"""
        
        # Ubicación actual del conductor
        current_location = None
        if instance.driver and hasattr(instance.driver, 'driver_profile'):
            profile = instance.driver.driver_profile
            if profile.current_latitude and profile.current_longitude:
                current_location = {
                    'latitude': float(profile.current_latitude),
                    'longitude': float(profile.current_longitude)
                }
        
        # Timeline de estados
        timeline = []
        
        timeline.append({
            'status': 'PENDING',
            'label': 'Entrega Creada',
            'timestamp': instance.created_at,
            'completed': True
        })
        
        if instance.assigned_at:
            timeline.append({
                'status': 'ASSIGNED',
                'label': 'Conductor Asignado',
                'timestamp': instance.assigned_at,
                'completed': True
            })
        
        if instance.pickup_started_at:
            timeline.append({
                'status': 'PICKING_UP',
                'label': 'Recogiendo Pedido',
                'timestamp': instance.pickup_started_at,
                'completed': True
            })
        
        if instance.picked_up_at:
            timeline.append({
                'status': 'PICKED_UP',
                'label': 'Pedido Recogido',
                'timestamp': instance.picked_up_at,
                'completed': True
            })
        
        if instance.in_transit_at:
            timeline.append({
                'status': 'IN_TRANSIT',
                'label': 'En Camino',
                'timestamp': instance.in_transit_at,
                'completed': True
            })
        
        if instance.arrived_at:
            timeline.append({
                'status': 'ARRIVED',
                'label': 'Llegó a Destino',
                'timestamp': instance.arrived_at,
                'completed': True
            })
        
        if instance.delivered_at:
            timeline.append({
                'status': 'DELIVERED',
                'label': 'Entregado',
                'timestamp': instance.delivered_at,
                'completed': True
            })
        
        if instance.failed_at:
            timeline.append({
                'status': 'FAILED',
                'label': 'Entrega Fallida',
                'timestamp': instance.failed_at,
                'completed': True,
                'reason': instance.get_failure_reason_display()
            })
        
        if instance.cancelled_at:
            timeline.append({
                'status': 'CANCELLED',
                'label': 'Cancelado',
                'timestamp': instance.cancelled_at,
                'completed': True
            })
        
        # Información del conductor
        driver_info = None
        if instance.driver:
            driver_info = {
                'name': instance.driver.get_full_name(),
                'phone': instance.driver.phone,
                'vehicle': None,
                'rating': None
            }
            
            if hasattr(instance.driver, 'driver_profile'):
                profile = instance.driver.driver_profile
                driver_info['vehicle'] = {
                    'type': profile.get_vehicle_type_display(),
                    'plate': profile.vehicle_plate,
                    'brand': profile.vehicle_brand,
                    'model': profile.vehicle_model,
                    'color': profile.vehicle_color
                }
                driver_info['rating'] = float(profile.rating)
        
        return {
            'delivery_id': instance.id,
            'order_number': instance.order.order_number,
            'status': instance.status,
            'status_display': instance.get_status_display(),
            'is_delayed': instance.is_delayed,
            'estimated_delivery_time': instance.estimated_delivery_time,
            'total_distance': float(instance.total_distance) if instance.total_distance else None,
            
            # Ubicaciones
            'pickup_location': {
                'latitude': float(instance.pickup_latitude),
                'longitude': float(instance.pickup_longitude),
                'address': instance.pickup_address
            },
            'delivery_location': {
                'latitude': float(instance.delivery_latitude),
                'longitude': float(instance.delivery_longitude),
                'address': instance.delivery_address,
                'reference': instance.delivery_reference
            },
            'current_location': current_location,
            
            # Conductor
            'driver': driver_info,
            
            # Timeline
            'timeline': timeline,
            
            # Tiempos
            'total_delivery_time': instance.total_delivery_time,
            'pickup_time': instance.pickup_time,
            'transit_time': instance.transit_time
        }