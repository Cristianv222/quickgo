# apps/payments/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from django.contrib import messages
from decimal import Decimal

from .models import (
    Payment,
    PaymentStatusHistory,
    Refund,
    PaymentMethod,
    Payout
)


# ============================================================================
# INLINES
# ============================================================================

class PaymentStatusHistoryInline(admin.TabularInline):
    """Inline para historial de estados"""
    model = PaymentStatusHistory
    extra = 0
    fields = ['status', 'notes', 'created_at']
    readonly_fields = ['status', 'notes', 'created_at']
    can_delete = False
    ordering = ['-created_at']
    
    def has_add_permission(self, request, obj=None):
        return False


class RefundInline(admin.TabularInline):
    """Inline para reembolsos"""
    model = Refund
    extra = 0
    fields = ['refund_id', 'amount', 'status', 'reason', 'created_at']
    readonly_fields = ['refund_id', 'created_at']
    
    def has_add_permission(self, request, obj=None):
        return False


# ============================================================================
# ADMIN PRINCIPAL DE PAYMENT
# ============================================================================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Administración de Pagos"""
    
    list_display = [
        'transaction_id_display',
        'status_badge',
        'order_link',
        'user_link',
        'payment_method_badge',
        'amount_display',
        'distribution_display',
        'created_at_display',
        'quick_actions'
    ]
    
    list_filter = [
        'status',
        'payment_method',
        'transaction_type',
        'created_at',
        'failure_reason'
    ]
    
    search_fields = [
        'transaction_id',
        'order__order_number',
        'user__first_name',
        'user__last_name',
        'user__email',
        'card_last4',
        'stripe_payment_intent_id',
        'paypal_transaction_id'
    ]
    
    readonly_fields = [
        'transaction_id',
        'order',
        'user',
        'created_at',
        'updated_at',
        'completed_at',
        'failed_at',
        'cancelled_at',
        'refunded_at',
        'payment_summary',
        'user_info_display',
        'order_info_display',
        'amount_breakdown',
        'distribution_info',
        'gateway_info',
        'refund_info',
        'timeline_display',
        'platform_fee',
        'restaurant_amount',
        'driver_amount'
    ]
    
    inlines = [
        PaymentStatusHistoryInline,
        RefundInline
    ]
    
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('💳 Información del Pago', {
            'fields': (
                'transaction_id',
                'status',
                'payment_summary'
            )
        }),
        ('🛒 Pedido y Usuario', {
            'fields': (
                'order',
                'order_info_display',
                'user',
                'user_info_display'
            )
        }),
        ('💰 Montos y Desglose', {
            'fields': (
                'amount',
                'currency',
                'amount_breakdown',
                'distribution_info'
            )
        }),
        ('💳 Método de Pago', {
            'fields': (
                'payment_method',
                'transaction_type',
                'card_last4',
                'card_brand',
                'card_holder_name'
            )
        }),
        ('🔗 Pasarelas de Pago', {
            'fields': (
                'stripe_payment_intent_id',
                'stripe_charge_id',
                'paypal_transaction_id',
                'mercadopago_payment_id',
                'gateway_info'
            ),
            'classes': ('collapse',)
        }),
        ('❌ Información de Falla', {
            'fields': (
                'failure_reason',
                'failure_message'
            ),
            'classes': ('collapse',)
        }),
        ('🔄 Información de Reembolso', {
            'fields': (
                'refund_info',
                'refund_reason',
                'refunded_amount',
                'refunded_at',
                'refunded_by'
            ),
            'classes': ('collapse',)
        }),
        ('📊 Información Adicional', {
            'fields': (
                'ip_address',
                'user_agent',
                'metadata'
            ),
            'classes': ('collapse',)
        }),
        ('⏱️ Timeline', {
            'fields': (
                'timeline_display',
            )
        }),
        ('ℹ️ Información del Sistema', {
            'fields': (
                'created_at',
                'updated_at',
                'completed_at',
                'failed_at',
                'cancelled_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'mark_as_completed',
        'mark_as_failed',
        'process_refund',
        'export_to_csv'
    ]
    
    # ========================================================================
    # DISPLAY METHODS
    # ========================================================================
    
    def transaction_id_display(self, obj):
        """ID de transacción con icono"""
        return format_html(
            '<span style="font-family: monospace; font-weight: bold; color: #3b82f6;">💳 {}</span>',
            obj.transaction_id
        )
    transaction_id_display.short_description = 'ID Transacción'
    transaction_id_display.admin_order_field = 'transaction_id'
    
    def status_badge(self, obj):
        """Badge de estado con colores"""
        colors = {
            'PENDING': '#f59e0b',           # Orange
            'PROCESSING': '#8b5cf6',        # Purple
            'COMPLETED': '#22c55e',         # Green
            'FAILED': '#ef4444',            # Red
            'CANCELLED': '#6b7280',         # Gray
            'REFUNDED': '#06b6d4',          # Cyan
            'PARTIALLY_REFUNDED': '#14b8a6' # Teal
        }
        
        icons = {
            'PENDING': '⏳',
            'PROCESSING': '🔄',
            'COMPLETED': '✅',
            'FAILED': '❌',
            'CANCELLED': '🚫',
            'REFUNDED': '↩️',
            'PARTIALLY_REFUNDED': '↩️'
        }
        
        color = colors.get(obj.status, '#6b7280')
        icon = icons.get(obj.status, '•')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold; white-space: nowrap;">'
            '{} {}</span>',
            color,
            icon,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    status_badge.admin_order_field = 'status'
    
    def order_link(self, obj):
        """Link al pedido"""
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html(
            '<a href="{}" style="text-decoration: none;">'
            '<strong>📦 #{}</strong><br>'
            '<span style="color: #6b7280; font-size: 11px;">${:.2f}</span>'
            '</a>',
            url,
            obj.order.order_number,
            obj.order.total
        )
    order_link.short_description = 'Pedido'
    
    def user_link(self, obj):
        """Link al usuario"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html(
            '<a href="{}" style="text-decoration: none;">'
            '<strong>👤 {}</strong><br>'
            '<span style="color: #6b7280; font-size: 11px;">{}</span>'
            '</a>',
            url,
            obj.user.get_full_name() or obj.user.username,
            obj.user.email
        )
    user_link.short_description = 'Usuario'
    
    def payment_method_badge(self, obj):
        """Badge del método de pago"""
        icons = {
            'CASH': '💵',
            'CARD': '💳',
            'WALLET': '👛',
            'BANK_TRANSFER': '🏦',
            'PAYPAL': '🅿️',
            'STRIPE': '💳',
            'MERCADOPAGO': '💳'
        }
        
        colors = {
            'CASH': '#16a34a',
            'CARD': '#3b82f6',
            'WALLET': '#8b5cf6',
            'BANK_TRANSFER': '#0891b2',
            'PAYPAL': '#0070ba',
            'STRIPE': '#635bff',
            'MERCADOPAGO': '#00b1ea'
        }
        
        icon = icons.get(obj.payment_method, '💳')
        color = colors.get(obj.payment_method, '#6b7280')
        
        display = obj.get_payment_method_display()
        if obj.card_last4:
            display += f' •••• {obj.card_last4}'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icon,
            display
        )
    payment_method_badge.short_description = 'Método de Pago'
    
    def amount_display(self, obj):
        """Monto con moneda"""
        return format_html(
            '<div style="text-align: right;">'
            '<strong style="color: #16a34a; font-size: 16px;">${:.2f}</strong><br>'
            '<span style="color: #6b7280; font-size: 10px;">{}</span>'
            '</div>',
            obj.amount,
            obj.currency
        )
    amount_display.short_description = 'Monto'
    
    def distribution_display(self, obj):
        """Distribución de montos"""
        return format_html(
            '<div style="font-size: 11px;">'
            '<div>🏪 Rest: <strong>${:.2f}</strong></div>'
            '<div>🚗 Driver: <strong>${:.2f}</strong></div>'
            '<div>⚡ Platform: <strong>${:.2f}</strong></div>'
            '</div>',
            obj.restaurant_amount,
            obj.driver_amount,
            obj.platform_fee
        )
    distribution_display.short_description = 'Distribución'
    
    def created_at_display(self, obj):
        """Fecha formateada"""
        return format_html(
            '<div style="font-size: 11px;">'
            '<div>{}</div>'
            '<div style="color: #6b7280;">{}</div>'
            '</div>',
            obj.created_at.strftime('%d/%m/%Y'),
            obj.created_at.strftime('%H:%M:%S')
        )
    created_at_display.short_description = 'Fecha'
    created_at_display.admin_order_field = 'created_at'
    
    def quick_actions(self, obj):
        """Acciones rápidas"""
        actions = []
        
        if obj.status == 'PENDING':
            actions.append('<span style="color: #f59e0b;">⏳ Pendiente</span>')
        
        if obj.status == 'PROCESSING':
            actions.append('<span style="color: #8b5cf6;">🔄 Procesando</span>')
        
        if obj.status == 'COMPLETED':
            actions.append('<span style="color: #16a34a;">✅ Completado</span>')
            if obj.is_refundable:
                actions.append('<span style="color: #06b6d4;">↩️ Reembolsable</span>')
        
        if obj.status == 'FAILED':
            actions.append('<span style="color: #ef4444;">❌ Fallido</span>')
        
        if obj.status in ['REFUNDED', 'PARTIALLY_REFUNDED']:
            actions.append(f'<span style="color: #06b6d4;">↩️ ${obj.refunded_amount:.2f}</span>')
        
        if actions:
            return format_html('<br>'.join(actions))
        return '-'
    quick_actions.short_description = 'Acciones'
    
    # ========================================================================
    # READONLY FIELD DISPLAYS
    # ========================================================================
    
    def payment_summary(self, obj):
        """Resumen del pago"""
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<table style="width: 100%;">'
            '<tr><td><strong>ID:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Estado:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Método:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Monto:</strong></td><td style="font-size: 18px; color: #16a34a;"><strong>${:.2f}</strong></td></tr>'
            '<tr><td><strong>Pedido:</strong></td><td>#{}</td></tr>'
            '<tr><td><strong>Usuario:</strong></td><td>{}</td></tr>'
            '</table>'
            '</div>',
            obj.transaction_id,
            obj.get_status_display(),
            obj.get_payment_method_display(),
            obj.amount,
            obj.order.order_number,
            obj.user.get_full_name()
        )
    payment_summary.short_description = 'Resumen del Pago'
    
    def user_info_display(self, obj):
        """Información del usuario"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<p><strong>Nombre:</strong> {}</p>'
            '<p><strong>Email:</strong> {}</p>'
            '<p><strong>Teléfono:</strong> {}</p>'
            '<p><strong>Tipo:</strong> {}</p>'
            '<p><a href="{}" style="color: #3b82f6;">Ver perfil completo →</a></p>'
            '</div>',
            obj.user.get_full_name() or obj.user.username,
            obj.user.email,
            obj.user.phone or 'N/A',
            obj.user.get_user_type_display(),
            url
        )
    user_info_display.short_description = 'Info del Usuario'
    
    def order_info_display(self, obj):
        """Información del pedido"""
        order = obj.order
        url = reverse('admin:orders_order_change', args=[order.id])
        
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<p><strong>Número:</strong> #{}</p>'
            '<p><strong>Total:</strong> ${:.2f}</p>'
            '<p><strong>Estado:</strong> {}</p>'
            '<p><strong>Restaurante:</strong> {}</p>'
            '<p><strong>Cliente:</strong> {}</p>'
            '<p><a href="{}" style="color: #3b82f6;">Ver pedido completo →</a></p>'
            '</div>',
            order.order_number,
            order.total,
            order.get_status_display(),
            order.restaurant.name,
            order.customer.get_full_name(),
            url
        )
    order_info_display.short_description = 'Info del Pedido'
    
    def amount_breakdown(self, obj):
        """Desglose de montos"""
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<table style="width: 100%; border-collapse: collapse;">'
            '<tr style="border-bottom: 1px solid #d1d5db;">'
            '<td style="padding: 8px;"><strong>Subtotal:</strong></td>'
            '<td style="padding: 8px; text-align: right;">${:.2f}</td>'
            '</tr>'
            '<tr style="border-bottom: 1px solid #d1d5db;">'
            '<td style="padding: 8px;">Costo de Envío:</td>'
            '<td style="padding: 8px; text-align: right;">${:.2f}</td>'
            '</tr>'
            '<tr style="border-bottom: 1px solid #d1d5db;">'
            '<td style="padding: 8px;">Tarifa de Servicio:</td>'
            '<td style="padding: 8px; text-align: right;">${:.2f}</td>'
            '</tr>'
            '<tr style="border-bottom: 1px solid #d1d5db;">'
            '<td style="padding: 8px;">Impuestos:</td>'
            '<td style="padding: 8px; text-align: right;">${:.2f}</td>'
            '</tr>'
            '<tr style="border-bottom: 1px solid #d1d5db;">'
            '<td style="padding: 8px;">Propina:</td>'
            '<td style="padding: 8px; text-align: right;">${:.2f}</td>'
            '</tr>'
            '<tr style="border-bottom: 1px solid #d1d5db;">'
            '<td style="padding: 8px; color: #ef4444;">Descuento:</td>'
            '<td style="padding: 8px; text-align: right; color: #ef4444;">-${:.2f}</td>'
            '</tr>'
            '<tr style="background: #e5e7eb; font-weight: bold;">'
            '<td style="padding: 8px; font-size: 16px;">TOTAL:</td>'
            '<td style="padding: 8px; text-align: right; font-size: 16px; color: #16a34a;">${:.2f}</td>'
            '</tr>'
            '</table>'
            '</div>',
            obj.subtotal,
            obj.delivery_fee,
            obj.service_fee,
            obj.tax,
            obj.tip,
            obj.discount,
            obj.amount
        )
    amount_breakdown.short_description = 'Desglose de Montos'
    
    def distribution_info(self, obj):
        """Información de distribución"""
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<table style="width: 100%; border-collapse: collapse;">'
            '<tr style="border-bottom: 1px solid #d1d5db;">'
            '<td style="padding: 8px;"><strong>🏪 Restaurante:</strong></td>'
            '<td style="padding: 8px; text-align: right; color: #16a34a; font-weight: bold;">${:.2f}</td>'
            '</tr>'
            '<tr style="border-bottom: 1px solid #d1d5db;">'
            '<td style="padding: 8px;"><strong>🚗 Conductor:</strong></td>'
            '<td style="padding: 8px; text-align: right; color: #3b82f6; font-weight: bold;">${:.2f}</td>'
            '</tr>'
            '<tr style="border-bottom: 1px solid #d1d5db;">'
            '<td style="padding: 8px;"><strong>⚡ Plataforma:</strong></td>'
            '<td style="padding: 8px; text-align: right; color: #8b5cf6; font-weight: bold;">${:.2f}</td>'
            '</tr>'
            '<tr style="background: #e5e7eb; font-weight: bold;">'
            '<td style="padding: 8px;">TOTAL DISTRIBUIDO:</td>'
            '<td style="padding: 8px; text-align: right;">${:.2f}</td>'
            '</tr>'
            '</table>'
            '<p style="margin-top: 10px; color: #6b7280; font-size: 12px;">'
            'Comisión del restaurante: {:.1f}%'
            '</p>'
            '</div>',
            obj.restaurant_amount,
            obj.driver_amount,
            obj.platform_fee,
            obj.restaurant_amount + obj.driver_amount + obj.platform_fee,
            obj.order.restaurant.commission_rate
        )
    distribution_info.short_description = 'Distribución de Montos'
    
    def gateway_info(self, obj):
        """Información de pasarelas"""
        gateway_data = []
        
        if obj.stripe_payment_intent_id:
            gateway_data.append(f'<p><strong>Stripe Payment Intent:</strong> {obj.stripe_payment_intent_id}</p>')
        
        if obj.stripe_charge_id:
            gateway_data.append(f'<p><strong>Stripe Charge:</strong> {obj.stripe_charge_id}</p>')
        
        if obj.paypal_transaction_id:
            gateway_data.append(f'<p><strong>PayPal Transaction:</strong> {obj.paypal_transaction_id}</p>')
        
        if obj.mercadopago_payment_id:
            gateway_data.append(f'<p><strong>MercadoPago Payment:</strong> {obj.mercadopago_payment_id}</p>')
        
        if obj.gateway_response:
            gateway_data.append(
                f'<p><strong>Gateway Response:</strong></p>'
                f'<pre style="background: #1f2937; color: #f3f4f6; padding: 10px; '
                f'border-radius: 6px; overflow-x: auto; font-size: 11px;">'
                f'{obj.gateway_response}'
                f'</pre>'
            )
        
        if not gateway_data:
            return format_html('<p style="color: #6b7280;">No hay información de pasarela disponible</p>')
        
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '{}'
            '</div>',
            ''.join(gateway_data)
        )
    gateway_info.short_description = 'Info de Pasarela'
    
    def refund_info(self, obj):
        """Información de reembolsos"""
        if obj.refunded_amount == 0:
            return format_html(
                '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
                '<p style="color: #6b7280;">No hay reembolsos procesados</p>'
                '{}'
                '</div>',
                f'<p><strong>Monto reembolsable:</strong> ${obj.remaining_refundable_amount:.2f}</p>' if obj.is_refundable else ''
            )
        
        refunds = obj.refunds.all()
        refund_list = []
        
        for refund in refunds:
            refund_list.append(
                f'<tr style="border-bottom: 1px solid #d1d5db;">'
                f'<td style="padding: 8px;">{refund.refund_id}</td>'
                f'<td style="padding: 8px;">${refund.amount:.2f}</td>'
                f'<td style="padding: 8px;">{refund.get_status_display()}</td>'
                f'<td style="padding: 8px; font-size: 10px;">{refund.created_at.strftime("%d/%m/%Y %H:%M")}</td>'
                f'</tr>'
            )
        
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<p><strong>Monto total reembolsado:</strong> '
            '<span style="color: #06b6d4; font-size: 16px; font-weight: bold;">${:.2f}</span></p>'
            '<p><strong>Monto reembolsable restante:</strong> ${:.2f}</p>'
            '<p><strong>Estado:</strong> {}</p>'
            '{}'
            '<table style="width: 100%; margin-top: 10px; border-collapse: collapse;">'
            '<tr style="background: #e5e7eb; font-weight: bold;">'
            '<th style="padding: 8px; text-align: left;">ID</th>'
            '<th style="padding: 8px; text-align: left;">Monto</th>'
            '<th style="padding: 8px; text-align: left;">Estado</th>'
            '<th style="padding: 8px; text-align: left;">Fecha</th>'
            '</tr>'
            '{}'
            '</table>'
            '</div>',
            obj.refunded_amount,
            obj.remaining_refundable_amount,
            obj.get_status_display(),
            f'<p><strong>Razón:</strong> {obj.refund_reason}</p>' if obj.refund_reason else '',
            ''.join(refund_list)
        )
    refund_info.short_description = 'Info de Reembolsos'
    
    def timeline_display(self, obj):
        """Timeline del pago"""
        timeline = []
        
        timeline.append(
            f'<p>📝 <strong>Creado:</strong> {obj.created_at.strftime("%d/%m/%Y %H:%M:%S")}</p>'
        )
        
        if obj.status == 'COMPLETED' and obj.completed_at:
            delta = obj.completed_at - obj.created_at
            seconds = int(delta.total_seconds())
            timeline.append(
                f'<p>✅ <strong>Completado:</strong> {obj.completed_at.strftime("%d/%m/%Y %H:%M:%S")} '
                f'<span style="color: #6b7280;">({seconds}s)</span></p>'
            )
        
        if obj.status == 'FAILED' and obj.failed_at:
            timeline.append(
                f'<p>❌ <strong>Fallido:</strong> {obj.failed_at.strftime("%d/%m/%Y %H:%M:%S")}</p>'
            )
            if obj.failure_message:
                timeline.append(
                    f'<p style="color: #ef4444; margin-left: 20px;">Error: {obj.failure_message}</p>'
                )
        
        if obj.status == 'CANCELLED' and obj.cancelled_at:
            timeline.append(
                f'<p>🚫 <strong>Cancelado:</strong> {obj.cancelled_at.strftime("%d/%m/%Y %H:%M:%S")}</p>'
            )
        
        if obj.refunded_at:
            timeline.append(
                f'<p>↩️ <strong>Reembolsado:</strong> {obj.refunded_at.strftime("%d/%m/%Y %H:%M:%S")}</p>'
            )
            timeline.append(
                f'<p style="margin-left: 20px;">Monto: ${obj.refunded_amount:.2f}</p>'
            )
        
        # Historial de estados
        history = obj.status_history.all()[:5]
        if history:
            timeline.append('<p style="margin-top: 10px;"><strong>Historial de cambios:</strong></p>')
            for h in history:
                timeline.append(
                    f'<p style="margin-left: 20px; font-size: 12px;">'
                    f'{h.created_at.strftime("%H:%M:%S")} - {h.get_status_display()}'
                    f'{": " + h.notes if h.notes else ""}'
                    f'</p>'
                )
        
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '{}'
            '</div>',
            ''.join(timeline)
        )
    timeline_display.short_description = 'Timeline'
    
    # ========================================================================
    # ACTIONS
    # ========================================================================
    
    @admin.action(description='✅ Marcar como Completado')
    def mark_as_completed(self, request, queryset):
        """Marcar pagos como completados"""
        updated = 0
        for payment in queryset:
            if payment.status in ['PENDING', 'PROCESSING']:
                try:
                    payment.mark_as_completed()
                    updated += 1
                except Exception as e:
                    self.message_user(
                        request,
                        f'Error en pago {payment.transaction_id}: {str(e)}',
                        level=messages.ERROR
                    )
        
        if updated:
            self.message_user(
                request,
                f'{updated} pago(s) marcado(s) como completado(s)',
                level=messages.SUCCESS
            )
    
    @admin.action(description='❌ Marcar como Fallido')
    def mark_as_failed(self, request, queryset):
        """Marcar pagos como fallidos"""
        updated = 0
        for payment in queryset:
            if payment.status not in ['COMPLETED', 'REFUNDED']:
                try:
                    payment.mark_as_failed(
                        reason='OTHER',
                        message='Marcado como fallido desde admin'
                    )
                    updated += 1
                except Exception as e:
                    self.message_user(
                        request,
                        f'Error en pago {payment.transaction_id}: {str(e)}',
                        level=messages.ERROR
                    )
        
        if updated:
            self.message_user(
                request,
                f'{updated} pago(s) marcado(s) como fallido(s)',
                level=messages.WARNING
            )
    
    @admin.action(description='↩️ Procesar Reembolso')
    def process_refund(self, request, queryset):
        """Procesar reembolsos para pagos completados"""
        refunded = 0
        for payment in queryset:
            if payment.is_refundable:
                try:
                    payment.refund(
                        reason='Reembolso procesado desde admin',
                        refunded_by=request.user
                    )
                    refunded += 1
                except Exception as e:
                    self.message_user(
                        request,
                        f'Error reembolsando {payment.transaction_id}: {str(e)}',
                        level=messages.ERROR
                    )
        
        if refunded:
            self.message_user(
                request,
                f'{refunded} pago(s) reembolsado(s) exitosamente',
                level=messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                'No hay pagos reembolsables seleccionados',
                level=messages.WARNING
            )
    
    @admin.action(description='📊 Exportar a CSV')
    def export_to_csv(self, request, queryset):
        """Exportar pagos a CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="payments_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID Transacción',
            'Pedido',
            'Usuario',
            'Estado',
            'Método de Pago',
            'Monto',
            'Comisión Plataforma',
            'Monto Restaurante',
            'Monto Conductor',
            'Fecha'
        ])
        
        for payment in queryset:
            writer.writerow([
                payment.transaction_id,
                payment.order.order_number,
                payment.user.get_full_name(),
                payment.get_status_display(),
                payment.get_payment_method_display(),
                payment.amount,
                payment.platform_fee,
                payment.restaurant_amount,
                payment.driver_amount,
                payment.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    
    # ========================================================================
    # CUSTOM METHODS
    # ========================================================================
    
    def get_queryset(self, request):
        """Optimizar queries"""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'order',
            'order__customer',
            'order__restaurant',
            'user',
            'refunded_by'
        ).prefetch_related(
            'status_history',
            'refunds'
        )
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar pagos"""
        return False


# ============================================================================
# ADMIN DE REFUND
# ============================================================================

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """Administración de Reembolsos"""
    
    list_display = [
        'refund_id_display',
        'payment_link',
        'amount_display',
        'status_badge',
        'reason_preview',
        'processed_by_display',
        'created_at_display'
    ]
    
    list_filter = [
        'status',
        'created_at'
    ]
    
    search_fields = [
        'refund_id',
        'payment__transaction_id',
        'reason'
    ]
    
    readonly_fields = [
        'refund_id',
        'payment',
        'created_at',
        'completed_at',
        'failed_at',
        'refund_summary'
    ]
    
    fieldsets = (
        ('Información del Reembolso', {
            'fields': (
                'refund_id',
                'payment',
                'amount',
                'reason',
                'status',
                'refund_summary'
            )
        }),
        ('Pasarelas de Pago', {
            'fields': (
                'stripe_refund_id',
                'paypal_refund_id',
                'gateway_response'
            ),
            'classes': ('collapse',)
        }),
        ('Procesamiento', {
            'fields': (
                'processed_by',
                'failure_message'
            )
        }),
        ('Información del Sistema', {
            'fields': (
                'created_at',
                'completed_at',
                'failed_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def refund_id_display(self, obj):
        return format_html(
            '<span style="font-family: monospace; font-weight: bold; color: #06b6d4;">↩️ {}</span>',
            obj.refund_id
        )
    refund_id_display.short_description = 'ID Reembolso'
    
    def payment_link(self, obj):
        url = reverse('admin:payments_payment_change', args=[obj.payment.id])
        return format_html(
            '<a href="{}" style="text-decoration: none;">'
            '<strong>💳 {}</strong>'
            '</a>',
            url,
            obj.payment.transaction_id
        )
    payment_link.short_description = 'Pago Original'
    
    def amount_display(self, obj):
        return format_html(
            '<strong style="color: #06b6d4; font-size: 14px;">${:.2f}</strong>',
            obj.amount
        )
    amount_display.short_description = 'Monto'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#f59e0b',
            'PROCESSING': '#8b5cf6',
            'COMPLETED': '#22c55e',
            'FAILED': '#ef4444',
            'CANCELLED': '#6b7280'
        }
        
        color = colors.get(obj.status, '#6b7280')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def reason_preview(self, obj):
        if len(obj.reason) > 50:
            return obj.reason[:50] + '...'
        return obj.reason
    reason_preview.short_description = 'Razón'
    
    def processed_by_display(self, obj):
        if obj.processed_by:
            return obj.processed_by.get_full_name()
        return 'Sistema'
    processed_by_display.short_description = 'Procesado por'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_display.short_description = 'Fecha'
    
    def refund_summary(self, obj):
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<p><strong>ID:</strong> {}</p>'
            '<p><strong>Pago Original:</strong> {}</p>'
            '<p><strong>Monto:</strong> <span style="color: #06b6d4; font-size: 16px;">${:.2f}</span></p>'
            '<p><strong>Estado:</strong> {}</p>'
            '<p><strong>Razón:</strong> {}</p>'
            '</div>',
            obj.refund_id,
            obj.payment.transaction_id,
            obj.amount,
            obj.get_status_display(),
            obj.reason
        )
    refund_summary.short_description = 'Resumen'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================================
# ADMIN DE PAYMENT METHOD
# ============================================================================

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """Administración de Métodos de Pago Guardados"""
    
    list_display = [
        'user_link',
        'type_badge',
        'card_info',
        'is_default_badge',
        'is_active_badge',
        'created_at_display'
    ]
    
    list_filter = [
        'type',
        'is_default',
        'is_active',
        'created_at'
    ]
    
    search_fields = [
        'user__first_name',
        'user__last_name',
        'user__email',
        'card_last4',
        'card_holder_name',
        'paypal_email'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at'
    ]
    
    def user_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.user.get_full_name()
        )
    user_link.short_description = 'Usuario'
    
    def type_badge(self, obj):
        icons = {
            'CARD': '💳',
            'BANK_ACCOUNT': '🏦',
            'PAYPAL': '🅿️',
            'WALLET': '👛'
        }
        
        icon = icons.get(obj.type, '💳')
        
        return format_html(
            '<span style="font-weight: bold;">{} {}</span>',
            icon,
            obj.get_type_display()
        )
    type_badge.short_description = 'Tipo'
    
    def card_info(self, obj):
        if obj.type == 'CARD':
            expired = ' ⚠️ EXPIRADA' if obj.is_expired else ''
            return format_html(
                '<strong>{} •••• {}</strong>{}<br>'
                '<span style="color: #6b7280; font-size: 11px;">Exp: {:02d}/{}</span>',
                obj.card_brand,
                obj.card_last4,
                expired,
                obj.card_exp_month or 0,
                obj.card_exp_year or 0
            )
        elif obj.type == 'PAYPAL':
            return obj.paypal_email
        return '-'
    card_info.short_description = 'Información'
    
    def is_default_badge(self, obj):
        if obj.is_default:
            return format_html('<span style="color: #16a34a; font-weight: bold;">⭐ Sí</span>')
        return format_html('<span style="color: #6b7280;">No</span>')
    is_default_badge.short_description = 'Por Defecto'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #16a34a;">✓ Activo</span>')
        return format_html('<span style="color: #ef4444;">✗ Inactivo</span>')
    is_active_badge.short_description = 'Estado'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%d/%m/%Y')
    created_at_display.short_description = 'Creado'


# ============================================================================
# ADMIN DE PAYOUT
# ============================================================================

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    """Administración de Pagos Salientes"""
    
    list_display = [
        'payout_id_display',
        'recipient_info',
        'recipient_type_badge',
        'amount_display',
        'period_display',
        'status_badge',
        'created_at_display'
    ]
    
    list_filter = [
        'status',
        'recipient_type',
        'created_at'
    ]
    
    search_fields = [
        'payout_id',
        'recipient__first_name',
        'recipient__last_name',
        'recipient__email'
    ]
    
    readonly_fields = [
        'payout_id',
        'created_at',
        'completed_at',
        'failed_at'
    ]
    
    def payout_id_display(self, obj):
        return format_html(
            '<span style="font-family: monospace; font-weight: bold; color: #f59e0b;">💸 {}</span>',
            obj.payout_id
        )
    payout_id_display.short_description = 'ID Pago'
    
    def recipient_info(self, obj):
        url = reverse('admin:users_user_change', args=[obj.recipient.id])
        return format_html(
            '<a href="{}" style="text-decoration: none;">'
            '<strong>{}</strong><br>'
            '<span style="color: #6b7280; font-size: 11px;">{}</span>'
            '</a>',
            url,
            obj.recipient.get_full_name(),
            obj.recipient.email
        )
    recipient_info.short_description = 'Destinatario'
    
    def recipient_type_badge(self, obj):
        icons = {
            'RESTAURANT': '🏪',
            'DRIVER': '🚗'
        }
        
        colors = {
            'RESTAURANT': '#16a34a',
            'DRIVER': '#3b82f6'
        }
        
        icon = icons.get(obj.recipient_type, '👤')
        color = colors.get(obj.recipient_type, '#6b7280')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icon,
            obj.get_recipient_type_display()
        )
    recipient_type_badge.short_description = 'Tipo'
    
    def amount_display(self, obj):
        return format_html(
            '<strong style="color: #f59e0b; font-size: 14px;">${:.2f}</strong>',
            obj.amount
        )
    amount_display.short_description = 'Monto'
    
    def period_display(self, obj):
        return format_html(
            '{} al {}',
            obj.period_start.strftime('%d/%m/%Y'),
            obj.period_end.strftime('%d/%m/%Y')
        )
    period_display.short_description = 'Período'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#f59e0b',
            'PROCESSING': '#8b5cf6',
            'COMPLETED': '#22c55e',
            'FAILED': '#ef4444',
            'CANCELLED': '#6b7280'
        }
        
        color = colors.get(obj.status, '#6b7280')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%d/%m/%Y')
    created_at_display.short_description = 'Creado'


# ============================================================================
# ADMIN DE PAYMENT STATUS HISTORY
# ============================================================================

@admin.register(PaymentStatusHistory)
class PaymentStatusHistoryAdmin(admin.ModelAdmin):
    """Administración de Historial de Estados de Pago"""
    
    list_display = [
        'payment_link',
        'status_badge',
        'notes_preview',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'created_at'
    ]
    
    search_fields = [
        'payment__transaction_id',
        'notes'
    ]
    
    readonly_fields = [
        'payment',
        'status',
        'notes',
        'metadata',
        'created_at'
    ]
    
    def payment_link(self, obj):
        url = reverse('admin:payments_payment_change', args=[obj.payment.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.payment.transaction_id
        )
    payment_link.short_description = 'Pago'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#f59e0b',
            'PROCESSING': '#8b5cf6',
            'COMPLETED': '#22c55e',
            'FAILED': '#ef4444',
            'CANCELLED': '#6b7280',
            'REFUNDED': '#06b6d4',
            'PARTIALLY_REFUNDED': '#14b8a6'
        }
        
        color = colors.get(obj.status, '#6b7280')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def notes_preview(self, obj):
        if obj.notes:
            return obj.notes[:50] + '...' if len(obj.notes) > 50 else obj.notes
        return '-'
    notes_preview.short_description = 'Notas'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False