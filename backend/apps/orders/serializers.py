# apps/orders/serializers.py
from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from .models import Order, OrderItem, OrderStatusHistory, OrderRating
from apps.products.models import Product, ProductExtra, ProductOption
from apps.restaurants.models import Restaurant
from apps.users.models import User


# ============================================================================
# SERIALIZERS DE ITEMS
# ============================================================================

class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer para items del pedido (lectura)"""
    
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    customizations_display = serializers.CharField(
        source='get_customizations_display',
        read_only=True
    )
    total_price_per_unit = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product_id',
            'product_name',
            'product_description',
            'product_image',
            'unit_price',
            'quantity',
            'selected_extras',
            'selected_options',
            'extras_total',
            'options_total',
            'subtotal',
            'special_notes',
            'customizations_display',
            'total_price_per_unit'
        ]


class OrderItemCreateSerializer(serializers.Serializer):
    """Serializer para crear items del pedido"""
    
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    selected_extras = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
        help_text='[{"id": 1, "quantity": 2}]'
    )
    selected_options = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
        help_text='[{"group_id": 1, "option_id": 2}]'
    )
    special_notes = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True
    )
    
    def validate_product_id(self, value):
        """Validar que el producto existe y está disponible"""
        try:
            product = Product.objects.get(id=value)
            if not product.is_available or not product.is_active:
                raise serializers.ValidationError("El producto no está disponible")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("El producto no existe")
    
    def validate_selected_extras(self, value):
        """Validar que los extras existen y están disponibles"""
        if not value:
            return []
        
        validated_extras = []
        for extra_data in value:
            extra_id = extra_data.get('id')
            quantity = extra_data.get('quantity', 1)
            
            try:
                extra = ProductExtra.objects.get(id=extra_id, is_available=True)
                validated_extras.append({
                    'id': extra.id,
                    'name': extra.name,
                    'price': str(extra.price),
                    'quantity': quantity
                })
            except ProductExtra.DoesNotExist:
                raise serializers.ValidationError(f"Extra con ID {extra_id} no disponible")
        
        return validated_extras
    
    def validate_selected_options(self, value):
        """Validar que las opciones existen y están disponibles"""
        if not value:
            return []
        
        validated_options = []
        for option_data in value:
            option_id = option_data.get('option_id')
            
            try:
                option = ProductOption.objects.select_related('group').get(
                    id=option_id,
                    is_available=True
                )
                validated_options.append({
                    'group_id': option.group.id,
                    'group': option.group.name,
                    'option_id': option.id,
                    'option': option.name,
                    'price_modifier': str(option.price_modifier)
                })
            except ProductOption.DoesNotExist:
                raise serializers.ValidationError(f"Opción con ID {option_id} no disponible")
        
        return validated_options


# ============================================================================
# SERIALIZERS DE HISTORIAL
# ============================================================================

class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer para historial de estados"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    changed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderStatusHistory
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


# ============================================================================
# SERIALIZERS DE RATING
# ============================================================================

class OrderRatingSerializer(serializers.ModelSerializer):
    """Serializer para calificaciones"""
    
    class Meta:
        model = OrderRating
        fields = [
            'id',
            'order',
            'overall_rating',
            'food_rating',
            'delivery_rating',
            'driver_rating',
            'driver_comment',
            'comment',
            'would_order_again',
            'liked_aspects',
            'disliked_aspects',
            'created_at'
        ]
        read_only_fields = ['order', 'created_at']
    
    def validate_overall_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("La calificación debe estar entre 1 y 5")
        return value
    
    def validate(self, data):
        """Validar que el pedido puede ser calificado"""
        order = self.context.get('order')
        
        if not order:
            raise serializers.ValidationError("Pedido no proporcionado")
        
        if not order.can_be_rated():
            raise serializers.ValidationError(
                "Solo se pueden calificar pedidos entregados y no calificados previamente"
            )
        
        return data


# ============================================================================
# SERIALIZERS DE ORDER (LECTURA)
# ============================================================================

class OrderListSerializer(serializers.ModelSerializer):
    """Serializer simple para listar pedidos"""
    
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    restaurant_logo = serializers.ImageField(source='restaurant.logo', read_only=True)
    driver_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )
    total_items = serializers.IntegerField(read_only=True)
    can_be_cancelled = serializers.BooleanField(read_only=True)
    can_be_rated = serializers.BooleanField(read_only=True)
    is_delayed = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'status',
            'status_display',
            'customer',
            'customer_name',
            'restaurant',
            'restaurant_name',
            'restaurant_logo',
            'driver',
            'driver_name',
            'total',
            'total_items',
            'payment_method',
            'payment_method_display',
            'is_paid',
            'estimated_delivery_time',
            'can_be_cancelled',
            'can_be_rated',
            'is_delayed',
            'is_rated',
            'created_at'
        ]
    
    def get_driver_name(self, obj):
        if obj.driver:
            return obj.driver.get_full_name()
        return None


class OrderDetailSerializer(serializers.ModelSerializer):
    """Serializer completo del pedido"""
    
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    restaurant_phone = serializers.CharField(source='restaurant.phone', read_only=True)
    restaurant_logo = serializers.ImageField(source='restaurant.logo', read_only=True)
    restaurant_address = serializers.CharField(source='restaurant.address', read_only=True)
    
    driver_name = serializers.SerializerMethodField()
    driver_phone = serializers.SerializerMethodField()
    driver_vehicle = serializers.SerializerMethodField()
    
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    rating = OrderRatingSerializer(read_only=True)
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )
    cancellation_reason_display = serializers.CharField(
        source='get_cancellation_reason_display',
        read_only=True
    )
    
    total_items = serializers.IntegerField(read_only=True)
    can_be_cancelled = serializers.BooleanField(read_only=True)
    can_be_rated = serializers.BooleanField(read_only=True)
    is_delayed = serializers.BooleanField(read_only=True)
    preparation_time_elapsed = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'status',
            'status_display',
            
            # Cliente
            'customer',
            'customer_name',
            'customer_phone',
            'customer_email',
            
            # Restaurante
            'restaurant',
            'restaurant_name',
            'restaurant_phone',
            'restaurant_logo',
            'restaurant_address',
            
            # Conductor
            'driver',
            'driver_name',
            'driver_phone',
            'driver_vehicle',
            
            # Dirección de entrega
            'delivery_address',
            'delivery_reference',
            'delivery_latitude',
            'delivery_longitude',
            'delivery_distance',
            
            # Costos
            'subtotal',
            'delivery_fee',
            'service_fee',
            'tax',
            'discount',
            'tip',
            'total',
            'total_items',
            
            # Pago
            'payment_method',
            'payment_method_display',
            'is_paid',
            'payment_date',
            'transaction_id',
            
            # Notas
            'special_instructions',
            'coupon_code',
            
            # Cancelación
            'cancellation_reason',
            'cancellation_reason_display',
            'cancellation_notes',
            'cancelled_by',
            'cancelled_at',
            
            # Tiempos
            'estimated_preparation_time',
            'estimated_delivery_time',
            'preparation_time_elapsed',
            'confirmed_at',
            'preparing_at',
            'ready_at',
            'picked_up_at',
            'delivered_at',
            
            # Estados
            'can_be_cancelled',
            'can_be_rated',
            'is_delayed',
            'is_rated',
            
            # Relaciones
            'items',
            'status_history',
            'rating',
            
            # Timestamps
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


# ============================================================================
# SERIALIZERS DE ORDER (ESCRITURA)
# ============================================================================

class OrderCreateSerializer(serializers.Serializer):
    """Serializer para crear un pedido"""
    
    restaurant_id = serializers.IntegerField()
    items = OrderItemCreateSerializer(many=True)
    
    # Dirección de entrega
    delivery_address = serializers.CharField(max_length=500)
    delivery_reference = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )
    delivery_latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    delivery_longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    
    # Opciones de pago
    payment_method = serializers.ChoiceField(
        choices=Order.PaymentMethod.choices,
        default=Order.PaymentMethod.CASH
    )
    
    # Opcional
    special_instructions = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True
    )
    coupon_code = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True
    )
    tip = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        default=Decimal('0.00')
    )
    
    def validate_restaurant_id(self, value):
        """Validar que el restaurante existe y está disponible"""
        try:
            restaurant = Restaurant.objects.get(id=value)
            if restaurant.status != Restaurant.Status.APPROVED:
                raise serializers.ValidationError("El restaurante no está disponible")
            if not restaurant.is_accepting_orders:
                raise serializers.ValidationError("El restaurante no está aceptando pedidos")
            return value
        except Restaurant.DoesNotExist:
            raise serializers.ValidationError("El restaurante no existe")
    
    def validate_items(self, value):
        """Validar que hay al menos un item"""
        if not value:
            raise serializers.ValidationError("Debe agregar al menos un producto")
        return value
    
    def validate(self, data):
        """Validaciones generales"""
        request = self.context.get('request')
        
        # Validar que el usuario es un cliente
        if request.user.user_type != 'CUSTOMER':
            raise serializers.ValidationError("Solo los clientes pueden crear pedidos")
        
        # Validar que todos los productos son del mismo restaurante
        restaurant_id = data['restaurant_id']
        for item_data in data['items']:
            product = Product.objects.get(id=item_data['product_id'])
            if product.restaurant_id != restaurant_id:
                raise serializers.ValidationError(
                    f"El producto {product.name} no pertenece a este restaurante"
                )
        
        # Validar distancia de entrega
        restaurant = Restaurant.objects.get(id=restaurant_id)
        if not restaurant.is_within_delivery_radius(
            data['delivery_latitude'],
            data['delivery_longitude']
        ):
            raise serializers.ValidationError(
                f"La dirección está fuera del radio de entrega ({restaurant.delivery_radius_km} km)"
            )
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        """Crear el pedido con todos sus items"""
        request = self.context.get('request')
        items_data = validated_data.pop('items')
        
        # Obtener restaurante
        restaurant = Restaurant.objects.get(id=validated_data.pop('restaurant_id'))
        
        # Crear orden
        order = Order.objects.create(
            customer=request.user,
            restaurant=restaurant,
            delivery_address=validated_data.get('delivery_address'),
            delivery_reference=validated_data.get('delivery_reference', ''),
            delivery_latitude=validated_data.get('delivery_latitude'),
            delivery_longitude=validated_data.get('delivery_longitude'),
            payment_method=validated_data.get('payment_method'),
            special_instructions=validated_data.get('special_instructions', ''),
            coupon_code=validated_data.get('coupon_code', ''),
            tip=validated_data.get('tip', Decimal('0.00')),
            service_fee=Decimal('0.50'),  # Tarifa de servicio fija
            estimated_preparation_time=restaurant.delivery_time_max
        )
        
        # Calcular distancia
        order.calculate_distance()
        
        # Crear items del pedido
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            
            # Reducir stock si aplica
            if product.track_inventory:
                product.reduce_stock(item_data['quantity'])
            
            # Crear item
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                product_description=product.description,
                product_image=product.image.url if product.image else '',
                unit_price=product.price,
                quantity=item_data['quantity'],
                selected_extras=item_data.get('selected_extras', []),
                selected_options=item_data.get('selected_options', []),
                special_notes=item_data.get('special_notes', '')
            )
        
        # Calcular totales
        order.calculate_totals()
        
        # Verificar pedido mínimo
        if order.subtotal < restaurant.min_order_amount:
            raise serializers.ValidationError(
                f"El pedido mínimo es ${restaurant.min_order_amount}"
            )
        
        # Crear historial inicial
        OrderStatusHistory.objects.create(
            order=order,
            status=Order.Status.PENDING,
            notes='Pedido creado',
            changed_by=request.user
        )
        
        return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar campos básicos del pedido"""
    
    class Meta:
        model = Order
        fields = [
            'delivery_address',
            'delivery_reference',
            'special_instructions',
            'tip'
        ]
    
    def validate(self, data):
        """Validar que el pedido puede ser modificado"""
        if self.instance.status not in ['PENDING', 'CONFIRMED']:
            raise serializers.ValidationError(
                "Solo se pueden modificar pedidos pendientes o confirmados"
            )
        return data


class OrderCancelSerializer(serializers.Serializer):
    """Serializer para cancelar un pedido"""
    
    cancellation_reason = serializers.ChoiceField(
        choices=Order.CancellationReason.choices
    )
    cancellation_notes = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True
    )
    
    def validate(self, data):
        """Validar que el pedido puede ser cancelado"""
        order = self.context.get('order')
        
        if not order.can_be_cancelled():
            raise serializers.ValidationError(
                "El pedido no puede ser cancelado en su estado actual"
            )
        
        return data


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer para actualizar el estado del pedido"""
    
    status = serializers.ChoiceField(choices=Order.Status.choices)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate(self, data):
        """Validar transición de estado"""
        order = self.context.get('order')
        new_status = data['status']
        current_status = order.status
        
        # Definir transiciones válidas
        valid_transitions = {
            'PENDING': ['CONFIRMED', 'CANCELLED'],
            'CONFIRMED': ['PREPARING', 'CANCELLED'],
            'PREPARING': ['READY', 'CANCELLED'],
            'READY': ['PICKED_UP'],
            'PICKED_UP': ['IN_TRANSIT'],
            'IN_TRANSIT': ['DELIVERED'],
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"No se puede cambiar de {current_status} a {new_status}"
            )
        
        return data