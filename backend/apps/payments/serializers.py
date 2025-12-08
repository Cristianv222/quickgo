from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal

from .models import (
    Payment,
    PaymentStatusHistory,
    Refund,
    PaymentMethod,
    Payout
)
from apps.orders.models import Order

User = get_user_model()


# ============================================================================
# SERIALIZERS DE PAYMENT
# ============================================================================

class PaymentStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer para historial de estados de pago"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PaymentStatusHistory
        fields = [
            'id',
            'status',
            'status_display',
            'notes',
            'metadata',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RefundSerializer(serializers.ModelSerializer):
    """Serializer para reembolsos"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    processed_by_name = serializers.CharField(
        source='processed_by.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = Refund
        fields = [
            'id',
            'refund_id',
            'amount',
            'reason',
            'status',
            'status_display',
            'processed_by',
            'processed_by_name',
            'failure_message',
            'created_at',
            'completed_at',
            'failed_at'
        ]
        read_only_fields = [
            'id',
            'refund_id',
            'status',
            'created_at',
            'completed_at',
            'failed_at'
        ]


class PaymentListSerializer(serializers.ModelSerializer):
    """Serializer para listar pagos"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )
    transaction_type_display = serializers.CharField(
        source='get_transaction_type_display',
        read_only=True
    )
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    customer_name = serializers.CharField(source='user.get_full_name', read_only=True)
    restaurant_name = serializers.CharField(source='order.restaurant.name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id',
            'transaction_id',
            'order',
            'order_number',
            'user',
            'customer_name',
            'restaurant_name',
            'transaction_type',
            'transaction_type_display',
            'payment_method',
            'payment_method_display',
            'status',
            'status_display',
            'amount',
            'currency',
            'card_last4',
            'card_brand',
            'refunded_amount',
            'is_refundable',
            'remaining_refundable_amount',
            'created_at',
            'completed_at',
            'failed_at'
        ]
        read_only_fields = [
            'id',
            'transaction_id',
            'status',
            'created_at',
            'completed_at',
            'failed_at'
        ]


class PaymentDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para un pago"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )
    transaction_type_display = serializers.CharField(
        source='get_transaction_type_display',
        read_only=True
    )
    failure_reason_display = serializers.CharField(
        source='get_failure_reason_display',
        read_only=True
    )
    
    # Información relacionada
    order_info = serializers.SerializerMethodField()
    user_info = serializers.SerializerMethodField()
    
    # Historial y reembolsos
    status_history = PaymentStatusHistorySerializer(many=True, read_only=True)
    refunds = RefundSerializer(many=True, read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id',
            'transaction_id',
            'order',
            'order_info',
            'user',
            'user_info',
            'transaction_type',
            'transaction_type_display',
            'payment_method',
            'payment_method_display',
            'status',
            'status_display',
            'amount',
            'currency',
            'subtotal',
            'delivery_fee',
            'service_fee',
            'tax',
            'discount',
            'tip',
            'platform_fee',
            'restaurant_amount',
            'driver_amount',
            'card_last4',
            'card_brand',
            'card_holder_name',
            'stripe_payment_intent_id',
            'stripe_charge_id',
            'paypal_transaction_id',
            'mercadopago_payment_id',
            'failure_reason',
            'failure_reason_display',
            'failure_message',
            'refund_reason',
            'refunded_amount',
            'refunded_at',
            'is_refundable',
            'remaining_refundable_amount',
            'ip_address',
            'metadata',
            'created_at',
            'updated_at',
            'completed_at',
            'failed_at',
            'cancelled_at',
            'status_history',
            'refunds'
        ]
        read_only_fields = [
            'id',
            'transaction_id',
            'status',
            'platform_fee',
            'restaurant_amount',
            'driver_amount',
            'created_at',
            'updated_at',
            'completed_at',
            'failed_at',
            'cancelled_at',
            'refunded_at'
        ]
    
    def get_order_info(self, obj):
        """Información del pedido"""
        order = obj.order
        return {
            'id': order.id,
            'order_number': order.order_number,
            'status': order.status,
            'status_display': order.get_status_display(),
            'total': str(order.total),
            'restaurant': {
                'id': order.restaurant.id,
                'name': order.restaurant.name,
                'phone': order.restaurant.phone
            },
            'customer': {
                'id': order.customer.id,
                'name': order.customer.get_full_name(),
                'email': order.customer.email
            }
        }
    
    def get_user_info(self, obj):
        """Información del usuario que realizó el pago"""
        user = obj.user
        return {
            'id': user.id,
            'name': user.get_full_name(),
            'email': user.email,
            'phone': user.phone,
            'user_type': user.user_type,
            'user_type_display': user.get_user_type_display()
        }


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear un pago"""
    
    class Meta:
        model = Payment
        fields = [
            'order',
            'payment_method',
            'amount',
            'currency',
            'subtotal',
            'delivery_fee',
            'service_fee',
            'tax',
            'discount',
            'tip',
            'card_last4',
            'card_brand',
            'card_holder_name',
            'ip_address',
            'user_agent',
            'metadata'
        ]
    
    def validate_order(self, value):
        """Validar que el pedido existe y está pendiente de pago"""
        if value.is_paid:
            raise serializers.ValidationError(
                "Este pedido ya ha sido pagado"
            )
        
        if value.status == 'CANCELLED':
            raise serializers.ValidationError(
                "No se puede pagar un pedido cancelado"
            )
        
        return value
    
    def validate_amount(self, value):
        """Validar que el monto sea mayor a 0"""
        if value <= 0:
            raise serializers.ValidationError(
                "El monto debe ser mayor a 0"
            )
        return value
    
    def validate(self, data):
        """Validaciones adicionales"""
        # Validar que el monto coincida con el total del pedido
        order = data.get('order')
        amount = data.get('amount')
        
        if order and amount:
            if abs(amount - order.total) > Decimal('0.01'):
                raise serializers.ValidationError(
                    "El monto del pago no coincide con el total del pedido"
                )
        
        return data
    
    def create(self, validated_data):
        """Crear el pago"""
        # El usuario que crea el pago es el usuario autenticado
        request = self.context.get('request')
        validated_data['user'] = request.user
        
        # Crear el pago
        payment = Payment.objects.create(**validated_data)
        
        return payment


class PaymentProcessSerializer(serializers.Serializer):
    """Serializer para procesar un pago"""
    payment_method_id = serializers.CharField(
        required=False,
        help_text="ID del método de pago guardado a utilizar"
    )
    stripe_payment_method_id = serializers.CharField(
        required=False,
        help_text="ID del payment method de Stripe"
    )
    save_payment_method = serializers.BooleanField(
        default=False,
        help_text="Guardar método de pago para uso futuro"
    )


class PaymentRefundSerializer(serializers.Serializer):
    """Serializer para solicitar un reembolso"""
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Monto a reembolsar (dejar vacío para reembolso total)"
    )
    reason = serializers.CharField(
        required=True,
        help_text="Razón del reembolso"
    )
    
    def validate_amount(self, value):
        """Validar que el monto sea válido"""
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "El monto debe ser mayor a 0"
            )
        return value
    
    def validate(self, data):
        """Validaciones adicionales"""
        payment = self.context.get('payment')
        amount = data.get('amount')
        
        if payment and amount:
            if amount > payment.remaining_refundable_amount:
                raise serializers.ValidationError({
                    'amount': f"El monto excede el monto reembolsable (${payment.remaining_refundable_amount})"
                })
        
        return data


# ============================================================================
# SERIALIZERS DE PAYMENT METHOD
# ============================================================================

class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer para métodos de pago guardados"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id',
            'type',
            'type_display',
            'card_last4',
            'card_brand',
            'card_exp_month',
            'card_exp_year',
            'card_holder_name',
            'paypal_email',
            'is_default',
            'is_active',
            'is_expired',
            'display_name',
            'billing_name',
            'billing_address',
            'billing_city',
            'billing_country',
            'billing_postal_code',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'is_expired'
        ]
        extra_kwargs = {
            'stripe_payment_method_id': {'write_only': True}
        }
    
    def get_display_name(self, obj):
        """Nombre para mostrar del método de pago"""
        return str(obj)
    
    def validate(self, data):
        """Validaciones"""
        if data.get('type') == 'CARD':
            # Validar que tenga información de tarjeta
            required_fields = ['card_last4', 'card_brand', 'card_exp_month', 'card_exp_year']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({
                        field: "Este campo es requerido para tarjetas"
                    })
        
        return data


class PaymentMethodCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear método de pago"""
    stripe_payment_method_id = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = PaymentMethod
        fields = [
            'type',
            'card_last4',
            'card_brand',
            'card_exp_month',
            'card_exp_year',
            'card_holder_name',
            'stripe_payment_method_id',
            'paypal_email',
            'is_default',
            'billing_name',
            'billing_address',
            'billing_city',
            'billing_country',
            'billing_postal_code'
        ]
    
    def create(self, validated_data):
        """Crear método de pago"""
        request = self.context.get('request')
        validated_data['user'] = request.user
        
        return PaymentMethod.objects.create(**validated_data)


# ============================================================================
# SERIALIZERS DE PAYOUT
# ============================================================================

class PayoutSerializer(serializers.ModelSerializer):
    """Serializer para pagos salientes"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    recipient_type_display = serializers.CharField(
        source='get_recipient_type_display',
        read_only=True
    )
    recipient_name = serializers.CharField(
        source='recipient.get_full_name',
        read_only=True
    )
    recipient_email = serializers.CharField(
        source='recipient.email',
        read_only=True
    )
    
    class Meta:
        model = Payout
        fields = [
            'id',
            'payout_id',
            'recipient_type',
            'recipient_type_display',
            'recipient',
            'recipient_name',
            'recipient_email',
            'amount',
            'period_start',
            'period_end',
            'status',
            'status_display',
            'payment_method',
            'bank_account_last4',
            'failure_message',
            'notes',
            'processed_by',
            'created_at',
            'completed_at',
            'failed_at'
        ]
        read_only_fields = [
            'id',
            'payout_id',
            'status',
            'created_at',
            'completed_at',
            'failed_at'
        ]


class PayoutCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear payout"""
    
    class Meta:
        model = Payout
        fields = [
            'recipient_type',
            'recipient',
            'amount',
            'period_start',
            'period_end',
            'payment_method',
            'bank_account_last4',
            'notes'
        ]
    
    def validate_amount(self, value):
        """Validar monto"""
        if value <= 0:
            raise serializers.ValidationError(
                "El monto debe ser mayor a 0"
            )
        return value
    
    def validate(self, data):
        """Validaciones adicionales"""
        # Validar que las fechas sean válidas
        if data['period_start'] > data['period_end']:
            raise serializers.ValidationError({
                'period_end': "La fecha de fin debe ser posterior a la fecha de inicio"
            })
        
        return data


# ============================================================================
# SERIALIZERS DE ESTADÍSTICAS
# ============================================================================

class PaymentStatisticsSerializer(serializers.Serializer):
    """Serializer para estadísticas de pagos"""
    total_payments = serializers.IntegerField()
    completed_payments = serializers.IntegerField()
    failed_payments = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_refunded = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_payment = serializers.DecimalField(max_digits=10, decimal_places=2)
    platform_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    payments_by_method = serializers.DictField()
    payments_by_status = serializers.DictField()