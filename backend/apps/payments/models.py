# apps/payments/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()


class Payment(models.Model):
    """Modelo principal de pagos/transacciones"""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        PROCESSING = 'PROCESSING', 'Procesando'
        COMPLETED = 'COMPLETED', 'Completado'
        FAILED = 'FAILED', 'Fallido'
        CANCELLED = 'CANCELLED', 'Cancelado'
        REFUNDED = 'REFUNDED', 'Reembolsado'
        PARTIALLY_REFUNDED = 'PARTIALLY_REFUNDED', 'Parcialmente Reembolsado'
    
    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', 'Efectivo'
        CARD = 'CARD', 'Tarjeta de Crédito/Débito'
        WALLET = 'WALLET', 'Billetera Digital'
        BANK_TRANSFER = 'BANK_TRANSFER', 'Transferencia Bancaria'
        PAYPAL = 'PAYPAL', 'PayPal'
        STRIPE = 'STRIPE', 'Stripe'
        MERCADOPAGO = 'MERCADOPAGO', 'MercadoPago'
    
    class TransactionType(models.TextChoices):
        ORDER_PAYMENT = 'ORDER_PAYMENT', 'Pago de Pedido'
        REFUND = 'REFUND', 'Reembolso'
        DRIVER_PAYOUT = 'DRIVER_PAYOUT', 'Pago a Conductor'
        RESTAURANT_PAYOUT = 'RESTAURANT_PAYOUT', 'Pago a Restaurante'
        TIP = 'TIP', 'Propina'
        PLATFORM_FEE = 'PLATFORM_FEE', 'Comisión de Plataforma'
    
    class FailureReason(models.TextChoices):
        INSUFFICIENT_FUNDS = 'INSUFFICIENT_FUNDS', 'Fondos Insuficientes'
        CARD_DECLINED = 'CARD_DECLINED', 'Tarjeta Rechazada'
        EXPIRED_CARD = 'EXPIRED_CARD', 'Tarjeta Expirada'
        INVALID_CARD = 'INVALID_CARD', 'Tarjeta Inválida'
        FRAUD_DETECTION = 'FRAUD_DETECTION', 'Detección de Fraude'
        NETWORK_ERROR = 'NETWORK_ERROR', 'Error de Red'
        GATEWAY_ERROR = 'GATEWAY_ERROR', 'Error de Pasarela'
        TIMEOUT = 'TIMEOUT', 'Tiempo de Espera Agotado'
        OTHER = 'OTHER', 'Otro'
    
    # Identificador único
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        editable=False,
        verbose_name='ID de Transacción'
    )
    
    # Relación con el pedido
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='Pedido'
    )
    
    # Usuario que realiza el pago
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='Usuario'
    )
    
    # Tipo y método de pago
    transaction_type = models.CharField(
        max_length=30,
        choices=TransactionType.choices,
        default=TransactionType.ORDER_PAYMENT,
        verbose_name='Tipo de Transacción'
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        verbose_name='Método de Pago'
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Estado',
        db_index=True
    )
    
    # Montos
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Monto',
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name='Moneda',
        help_text='Código ISO de la moneda (USD, EUR, etc.)'
    )
    
    # Desglose de montos
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Subtotal'
    )
    
    delivery_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Costo de Envío'
    )
    
    service_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Tarifa de Servicio'
    )
    
    tax = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Impuestos'
    )
    
    discount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Descuento'
    )
    
    tip = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Propina'
    )
    
    # Comisiones
    platform_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Comisión de Plataforma',
        help_text='Comisión que se queda la plataforma'
    )
    
    restaurant_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto para Restaurante',
        help_text='Monto que recibe el restaurante'
    )
    
    driver_amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto para Conductor',
        help_text='Monto que recibe el conductor'
    )
    
    # Información de la tarjeta (tokenizada, nunca guardar datos reales)
    card_last4 = models.CharField(
        max_length=4,
        blank=True,
        verbose_name='Últimos 4 dígitos',
        help_text='Últimos 4 dígitos de la tarjeta'
    )
    
    card_brand = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Marca de Tarjeta',
        help_text='Visa, Mastercard, etc.'
    )
    
    card_holder_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nombre del Titular'
    )
    
    # IDs de pasarelas de pago externas
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Stripe Payment Intent ID'
    )
    
    stripe_charge_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Stripe Charge ID'
    )
    
    paypal_transaction_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='PayPal Transaction ID'
    )
    
    mercadopago_payment_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='MercadoPago Payment ID'
    )
    
    gateway_response = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Respuesta de Pasarela',
        help_text='Respuesta completa de la pasarela de pago'
    )
    
    # Información de falla
    failure_reason = models.CharField(
        max_length=30,
        choices=FailureReason.choices,
        blank=True,
        verbose_name='Razón de Falla'
    )
    
    failure_message = models.TextField(
        blank=True,
        verbose_name='Mensaje de Error'
    )
    
    # Reembolso
    refund_reason = models.TextField(
        blank=True,
        verbose_name='Razón de Reembolso'
    )
    
    refunded_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto Reembolsado'
    )
    
    refunded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Reembolso'
    )
    
    refunded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_refunds',
        verbose_name='Reembolsado por'
    )
    
    # Información adicional
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Dirección IP'
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Metadata',
        help_text='Información adicional en formato JSON'
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
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Completado'
    )
    
    failed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Fallo'
    )
    
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Cancelación'
    )
    
    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['order']),
            models.Index(fields=['payment_method']),
        ]
    
    def __str__(self):
        return f"Pago #{self.transaction_id} - ${self.amount} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        """Generar transaction_id si no existe"""
        if not self.transaction_id:
            self.transaction_id = self._generate_transaction_id()
        
        # Calcular montos para restaurante y conductor
        self._calculate_distributions()
        
        super().save(*args, **kwargs)
    
    def _generate_transaction_id(self):
        """Generar ID único de transacción"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        random_part = uuid.uuid4().hex[:8].upper()
        return f"PAY{timestamp}{random_part}"
    
    def _calculate_distributions(self):
        """Calcular distribución de montos"""
        # Comisión de plataforma (% del subtotal del pedido)
        commission_rate = self.order.restaurant.commission_rate / 100
        self.platform_fee = self.subtotal * Decimal(str(commission_rate))
        
        # Monto para el restaurante (subtotal - comisión)
        self.restaurant_amount = self.subtotal - self.platform_fee
        
        # Monto para el conductor (delivery_fee + tip)
        self.driver_amount = self.delivery_fee + self.tip
    
    def mark_as_processing(self):
        """Marcar pago como en procesamiento"""
        if self.status != self.Status.PENDING:
            raise ValueError("Solo se pueden procesar pagos pendientes")
        
        self.status = self.Status.PROCESSING
        self.save()
        
        PaymentStatusHistory.objects.create(
            payment=self,
            status=self.Status.PROCESSING,
            notes='Pago en procesamiento'
        )
    
    def mark_as_completed(self):
        """Marcar pago como completado"""
        if self.status not in [self.Status.PENDING, self.Status.PROCESSING]:
            raise ValueError("Estado inválido para completar pago")
        
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save()
        
        # Actualizar estado del pedido
        self.order.is_paid = True
        self.order.payment_date = self.completed_at
        self.order.transaction_id = self.transaction_id
        self.order.save()
        
        PaymentStatusHistory.objects.create(
            payment=self,
            status=self.Status.COMPLETED,
            notes='Pago completado exitosamente'
        )
    
    def mark_as_failed(self, reason, message=''):
        """Marcar pago como fallido"""
        if self.status in [self.Status.COMPLETED, self.Status.REFUNDED]:
            raise ValueError("No se puede marcar como fallido un pago completado o reembolsado")
        
        self.status = self.Status.FAILED
        self.failure_reason = reason
        self.failure_message = message
        self.failed_at = timezone.now()
        self.save()
        
        PaymentStatusHistory.objects.create(
            payment=self,
            status=self.Status.FAILED,
            notes=f'Pago fallido: {message}'
        )
    
    def cancel(self, reason=''):
        """Cancelar pago"""
        if self.status in [self.Status.COMPLETED, self.Status.REFUNDED]:
            raise ValueError("No se puede cancelar un pago completado o reembolsado")
        
        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.save()
        
        PaymentStatusHistory.objects.create(
            payment=self,
            status=self.Status.CANCELLED,
            notes=f'Pago cancelado: {reason}'
        )
    
    def refund(self, amount=None, reason='', refunded_by=None):
        """Procesar reembolso"""
        if self.status != self.Status.COMPLETED:
            raise ValueError("Solo se pueden reembolsar pagos completados")
        
        # Si no se especifica monto, reembolsar todo
        if amount is None:
            amount = self.amount - self.refunded_amount
        
        # Validar que no se reembolse más de lo pagado
        if self.refunded_amount + amount > self.amount:
            raise ValueError("El monto de reembolso excede el monto pagado")
        
        self.refunded_amount += amount
        self.refund_reason = reason
        self.refunded_at = timezone.now()
        self.refunded_by = refunded_by
        
        # Actualizar estado
        if self.refunded_amount >= self.amount:
            self.status = self.Status.REFUNDED
        else:
            self.status = self.Status.PARTIALLY_REFUNDED
        
        self.save()
        
        # Crear registro de reembolso
        Refund.objects.create(
            payment=self,
            amount=amount,
            reason=reason,
            processed_by=refunded_by
        )
        
        PaymentStatusHistory.objects.create(
            payment=self,
            status=self.status,
            notes=f'Reembolso de ${amount}: {reason}'
        )
    
    @property
    def is_refundable(self):
        """Verificar si el pago puede ser reembolsado"""
        return (
            self.status == self.Status.COMPLETED and
            self.refunded_amount < self.amount
        )
    
    @property
    def remaining_refundable_amount(self):
        """Monto restante que puede ser reembolsado"""
        if self.is_refundable:
            return self.amount - self.refunded_amount
        return Decimal('0.00')


class PaymentStatusHistory(models.Model):
    """Historial de cambios de estado del pago"""
    
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name='Pago'
    )
    
    status = models.CharField(
        max_length=20,
        choices=Payment.Status.choices,
        verbose_name='Estado'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Metadata'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha',
        db_index=True
    )
    
    class Meta:
        verbose_name = 'Historial de Estado de Pago'
        verbose_name_plural = 'Historial de Estados de Pagos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pago #{self.payment.transaction_id} - {self.get_status_display()}"


class Refund(models.Model):
    """Registro de reembolsos"""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        PROCESSING = 'PROCESSING', 'Procesando'
        COMPLETED = 'COMPLETED', 'Completado'
        FAILED = 'FAILED', 'Fallido'
        CANCELLED = 'CANCELLED', 'Cancelado'
    
    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name='refunds',
        verbose_name='Pago Original'
    )
    
    refund_id = models.CharField(
        max_length=100,
        unique=True,
        editable=False,
        verbose_name='ID de Reembolso'
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Monto Reembolsado',
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    reason = models.TextField(
        verbose_name='Razón del Reembolso'
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Estado'
    )
    
    # IDs de pasarelas externas
    stripe_refund_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Stripe Refund ID'
    )
    
    paypal_refund_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='PayPal Refund ID'
    )
    
    gateway_response = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Respuesta de Pasarela'
    )
    
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_refunds_history',
        verbose_name='Procesado por'
    )
    
    failure_message = models.TextField(
        blank=True,
        verbose_name='Mensaje de Error'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Completado'
    )
    
    failed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Fallo'
    )
    
    class Meta:
        verbose_name = 'Reembolso'
        verbose_name_plural = 'Reembolsos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reembolso #{self.refund_id} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        """Generar refund_id si no existe"""
        if not self.refund_id:
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            random_part = uuid.uuid4().hex[:6].upper()
            self.refund_id = f"REF{timestamp}{random_part}"
        
        super().save(*args, **kwargs)
    
    def mark_as_completed(self):
        """Marcar reembolso como completado"""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, message=''):
        """Marcar reembolso como fallido"""
        self.status = self.Status.FAILED
        self.failure_message = message
        self.failed_at = timezone.now()
        self.save()


class PaymentMethod(models.Model):
    """Métodos de pago guardados del usuario"""
    
    class Type(models.TextChoices):
        CARD = 'CARD', 'Tarjeta'
        BANK_ACCOUNT = 'BANK_ACCOUNT', 'Cuenta Bancaria'
        PAYPAL = 'PAYPAL', 'PayPal'
        WALLET = 'WALLET', 'Billetera Digital'
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_payment_methods',
        verbose_name='Usuario'
    )
    
    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        verbose_name='Tipo'
    )
    
    # Información de tarjeta (tokenizada)
    card_last4 = models.CharField(
        max_length=4,
        blank=True,
        verbose_name='Últimos 4 dígitos'
    )
    
    card_brand = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Marca',
        help_text='Visa, Mastercard, etc.'
    )
    
    card_exp_month = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='Mes de Expiración',
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    
    card_exp_year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='Año de Expiración'
    )
    
    card_holder_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nombre del Titular'
    )
    
    # Tokens de pasarelas
    stripe_payment_method_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Stripe Payment Method ID'
    )
    
    paypal_email = models.EmailField(
        blank=True,
        verbose_name='Email de PayPal'
    )
    
    # Configuración
    is_default = models.BooleanField(
        default=False,
        verbose_name='Método por Defecto'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    # Dirección de facturación
    billing_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nombre de Facturación'
    )
    
    billing_address = models.TextField(
        blank=True,
        verbose_name='Dirección de Facturación'
    )
    
    billing_city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Ciudad'
    )
    
    billing_country = models.CharField(
        max_length=2,
        blank=True,
        verbose_name='País',
        help_text='Código ISO de 2 letras'
    )
    
    billing_postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Código Postal'
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
        verbose_name = 'Método de Pago Guardado'
        verbose_name_plural = 'Métodos de Pago Guardados'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        if self.type == 'CARD':
            return f"{self.card_brand} •••• {self.card_last4}"
        elif self.type == 'PAYPAL':
            return f"PayPal ({self.paypal_email})"
        return f"{self.get_type_display()}"
    
    def save(self, *args, **kwargs):
        """Si es método por defecto, quitar default de los demás"""
        if self.is_default:
            PaymentMethod.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Verificar si la tarjeta está expirada"""
        if self.type == 'CARD' and self.card_exp_month and self.card_exp_year:
            now = timezone.now()
            return (
                self.card_exp_year < now.year or
                (self.card_exp_year == now.year and self.card_exp_month < now.month)
            )
        return False


class Payout(models.Model):
    """Pagos de la plataforma a restaurantes y conductores"""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        PROCESSING = 'PROCESSING', 'Procesando'
        COMPLETED = 'COMPLETED', 'Completado'
        FAILED = 'FAILED', 'Fallido'
        CANCELLED = 'CANCELLED', 'Cancelado'
    
    class RecipientType(models.TextChoices):
        RESTAURANT = 'RESTAURANT', 'Restaurante'
        DRIVER = 'DRIVER', 'Conductor'
    
    payout_id = models.CharField(
        max_length=100,
        unique=True,
        editable=False,
        verbose_name='ID de Pago'
    )
    
    recipient_type = models.CharField(
        max_length=20,
        choices=RecipientType.choices,
        verbose_name='Tipo de Destinatario'
    )
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='received_payouts',
        verbose_name='Destinatario'
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Monto',
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    period_start = models.DateField(
        verbose_name='Inicio del Período'
    )
    
    period_end = models.DateField(
        verbose_name='Fin del Período'
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Estado'
    )
    
    # Método de pago
    payment_method = models.CharField(
        max_length=50,
        verbose_name='Método de Pago',
        help_text='Transferencia bancaria, PayPal, etc.'
    )
    
    bank_account_last4 = models.CharField(
        max_length=4,
        blank=True,
        verbose_name='Últimos 4 dígitos de cuenta'
    )
    
    # Referencias externas
    stripe_payout_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Stripe Payout ID'
    )
    
    paypal_payout_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='PayPal Payout ID'
    )
    
    failure_message = models.TextField(
        blank=True,
        verbose_name='Mensaje de Error'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payouts',
        verbose_name='Procesado por'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Completado'
    )
    
    failed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Fallo'
    )
    
    class Meta:
        verbose_name = 'Pago Saliente'
        verbose_name_plural = 'Pagos Salientes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payout #{self.payout_id} - {self.recipient.get_full_name()} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        """Generar payout_id si no existe"""
        if not self.payout_id:
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            random_part = uuid.uuid4().hex[:6].upper()
            self.payout_id = f"OUT{timestamp}{random_part}"
        
        super().save(*args, **kwargs)
    
    def mark_as_completed(self):
        """Marcar pago como completado"""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, message=''):
        """Marcar pago como fallido"""
        self.status = self.Status.FAILED
        self.failure_message = message
        self.failed_at = timezone.now()
        self.save()