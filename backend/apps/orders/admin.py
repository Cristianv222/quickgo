# apps/orders/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from django.contrib import messages
from .models import Order, OrderItem, OrderStatusHistory, OrderRating


# ============================================================================
# INLINES
# ============================================================================

class OrderItemInline(admin.TabularInline):
    """Inline para items del pedido"""
    model = OrderItem
    extra = 0
    fields = [
        'product_name',
        'quantity',
        'unit_price',
        'extras_display',
        'options_display',
        'subtotal',
        'special_notes'
    ]
    readonly_fields = [
        'extras_display',
        'options_display',
        'subtotal'
    ]
    can_delete = False
    
    def extras_display(self, obj):
        """Muestra los extras seleccionados"""
        if obj.selected_extras:
            extras_list = []
            for extra in obj.selected_extras:
                qty = extra.get('quantity', 1)
                price = extra.get('price', 0)
                extras_list.append(
                    f"{extra['name']} x{qty} (+${price})"
                )
            return format_html('<br>'.join(extras_list))
        return '-'
    extras_display.short_description = 'Extras'
    
    def options_display(self, obj):
        """Muestra las opciones seleccionadas"""
        if obj.selected_options:
            options_list = []
            for option in obj.selected_options:
                modifier = option.get('price_modifier', 0)
                modifier_text = f" (+${modifier})" if float(modifier) > 0 else ""
                options_list.append(
                    f"{option['group']}: {option['option']}{modifier_text}"
                )
            return format_html('<br>'.join(options_list))
        return '-'
    options_display.short_description = 'Opciones'


class OrderStatusHistoryInline(admin.TabularInline):
    """Inline para historial de estados"""
    model = OrderStatusHistory
    extra = 0
    fields = ['status', 'notes', 'changed_by', 'created_at']
    readonly_fields = ['status', 'notes', 'changed_by', 'created_at']
    can_delete = False
    ordering = ['-created_at']
    
    def has_add_permission(self, request, obj=None):
        return False


# ============================================================================
# ADMIN PRINCIPAL DE ORDERS
# ============================================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Administración de Pedidos"""
    
    list_display = [
        'order_number',
        'status_badge',
        'customer_link',
        'restaurant_link',
        'driver_link',
        'total_items_display',
        'total_display',
        'payment_status',
        'delivery_time_display',
        'created_at_display',
        'quick_actions'
    ]
    
    list_filter = [
        'status',
        'payment_method',
        'is_paid',
        'is_rated',
        'created_at',
        'restaurant',
        'cancellation_reason'
    ]
    
    search_fields = [
        'order_number',
        'customer__first_name',
        'customer__last_name',
        'customer__email',
        'customer__username',
        'restaurant__name',
        'driver__first_name',
        'driver__last_name',
        'delivery_address',
        'transaction_id'
    ]
    
    readonly_fields = [
        'order_number',
        'created_at',
        'updated_at',
        'order_summary',
        'customer_info',
        'restaurant_info',
        'driver_info',
        'delivery_info',
        'payment_info',
        'timeline_display',
        'map_preview'
    ]
    
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('📋 Información del Pedido', {
            'fields': (
                'order_number',
                'status',
                'order_summary'
            )
        }),
        ('👤 Cliente', {
            'fields': (
                'customer',
                'customer_info'
            )
        }),
        ('🏪 Restaurante', {
            'fields': (
                'restaurant',
                'restaurant_info'
            )
        }),
        ('🚗 Repartidor', {
            'fields': (
                'driver',
                'driver_info'
            )
        }),
        ('📍 Dirección de Entrega', {
            'fields': (
                'delivery_address',
                'delivery_reference',
                ('delivery_latitude', 'delivery_longitude'),
                'delivery_distance',
                'delivery_info',
                'map_preview'
            )
        }),
        ('💰 Costos', {
            'fields': (
                ('subtotal', 'delivery_fee'),
                ('service_fee', 'tax'),
                ('discount', 'tip'),
                'total'
            )
        }),
        ('💳 Pago', {
            'fields': (
                'payment_method',
                'is_paid',
                'payment_date',
                'transaction_id',
                'payment_info'
            )
        }),
        ('📝 Notas e Instrucciones', {
            'fields': (
                'special_instructions',
                'coupon_code'
            )
        }),
        ('❌ Cancelación', {
            'fields': (
                'cancellation_reason',
                'cancellation_notes',
                'cancelled_by',
                'cancelled_at'
            ),
            'classes': ('collapse',)
        }),
        ('⏱️ Tiempos', {
            'fields': (
                'estimated_preparation_time',
                'estimated_delivery_time',
                'timeline_display'
            )
        }),
        ('⭐ Calificación', {
            'fields': ('is_rated',)
        }),
        ('ℹ️ Información del Sistema', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'mark_as_confirmed',
        'mark_as_preparing',
        'mark_as_ready',
        'mark_as_delivered',
        'cancel_orders',
        'export_to_csv'
    ]
    
    # ========================================================================
    # DISPLAY METHODS
    # ========================================================================
    
    def status_badge(self, obj):
        """Badge de estado con colores"""
        colors = {
            'PENDING': '#f59e0b',      # Orange
            'CONFIRMED': '#3b82f6',    # Blue
            'PREPARING': '#8b5cf6',    # Purple
            'READY': '#06b6d4',        # Cyan
            'PICKED_UP': '#14b8a6',    # Teal
            'IN_TRANSIT': '#10b981',   # Green
            'DELIVERED': '#22c55e',    # Green
            'CANCELLED': '#ef4444'     # Red
        }
        
        color = colors.get(obj.status, '#6b7280')
        
        # Agregar icono de retraso si aplica
        delay_icon = ''
        if obj.is_delayed:
            delay_icon = ' ⚠️'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold; white-space: nowrap;">'
            '{}{}</span>',
            color,
            obj.get_status_display(),
            delay_icon
        )
    status_badge.short_description = 'Estado'
    status_badge.admin_order_field = 'status'
    
    def customer_link(self, obj):
        """Link al cliente"""
        url = reverse('admin:users_user_change', args=[obj.customer.id])
        return format_html(
            '<a href="{}" style="text-decoration: none;">'
            '<strong>👤 {}</strong><br>'
            '<span style="color: #6b7280; font-size: 11px;">{}</span>'
            '</a>',
            url,
            obj.customer.get_full_name() or obj.customer.username,
            obj.customer.phone or obj.customer.email
        )
    customer_link.short_description = 'Cliente'
    
    def restaurant_link(self, obj):
        """Link al restaurante"""
        url = reverse('admin:restaurants_restaurant_change', args=[obj.restaurant.id])
        rating_stars = '⭐' * int(obj.restaurant.rating)
        return format_html(
            '<a href="{}" style="text-decoration: none;">'
            '<strong>🏪 {}</strong><br>'
            '<span style="color: #6b7280; font-size: 11px;">{}</span>'
            '</a>',
            url,
            obj.restaurant.name,
            rating_stars
        )
    restaurant_link.short_description = 'Restaurante'
    
    def driver_link(self, obj):
        """Link al conductor"""
        if obj.driver:
            url = reverse('admin:users_user_change', args=[obj.driver.id])
            return format_html(
                '<a href="{}" style="text-decoration: none;">'
                '<strong>🚗 {}</strong><br>'
                '<span style="color: #6b7280; font-size: 11px;">{}</span>'
                '</a>',
                url,
                obj.driver.get_full_name(),
                obj.driver.phone
            )
        return format_html(
            '<span style="color: #ef4444; font-style: italic;">Sin asignar</span>'
        )
    driver_link.short_description = 'Repartidor'
    
    def total_items_display(self, obj):
        """Total de items"""
        return format_html(
            '<strong style="font-size: 14px;">{}</strong> items',
            obj.total_items
        )
    total_items_display.short_description = 'Items'
    
    def total_display(self, obj):
        """Total del pedido"""
        return format_html(
            '<strong style="font-size: 16px; color: #16a34a;">${:.2f}</strong>',
            obj.total
        )
    total_display.short_description = 'Total'
    total_display.admin_order_field = 'total'
    
    def payment_status(self, obj):
        """Estado del pago"""
        if obj.is_paid:
            return format_html(
                '<span style="color: #16a34a; font-weight: bold;">✓ Pagado</span><br>'
                '<span style="color: #6b7280; font-size: 11px;">{}</span>',
                obj.get_payment_method_display()
            )
        return format_html(
            '<span style="color: #ef4444; font-weight: bold;">✗ Pendiente</span><br>'
            '<span style="color: #6b7280; font-size: 11px;">{}</span>',
            obj.get_payment_method_display()
        )
    payment_status.short_description = 'Pago'
    
    def delivery_time_display(self, obj):
        """Tiempo estimado de entrega"""
        if obj.estimated_delivery_time:
            now = timezone.now()
            if obj.status == 'DELIVERED':
                if obj.delivered_at:
                    delta = obj.delivered_at - obj.created_at
                    minutes = int(delta.total_seconds() / 60)
                    return format_html(
                        '<span style="color: #16a34a;">✓ Entregado<br>{} min</span>',
                        minutes
                    )
            elif obj.estimated_delivery_time > now:
                delta = obj.estimated_delivery_time - now
                minutes = int(delta.total_seconds() / 60)
                return format_html(
                    '<span style="color: #3b82f6;">⏱️ {} min</span>',
                    minutes
                )
            else:
                return format_html(
                    '<span style="color: #ef4444; font-weight: bold;">⚠️ Retrasado</span>'
                )
        return '-'
    delivery_time_display.short_description = 'Tiempo'
    
    def created_at_display(self, obj):
        """Fecha de creación formateada"""
        return format_html(
            '<strong>{}</strong><br>'
            '<span style="color: #6b7280; font-size: 11px;">{}</span>',
            obj.created_at.strftime('%d/%m/%Y'),
            obj.created_at.strftime('%H:%M:%S')
        )
    created_at_display.short_description = 'Fecha'
    created_at_display.admin_order_field = 'created_at'
    
    def quick_actions(self, obj):
        """Acciones rápidas"""
        actions = []
        
        if obj.status == 'PENDING':
            actions.append(
                '<a href="#" onclick="return confirm(\'¿Confirmar pedido?\');" '
                'style="color: #3b82f6; text-decoration: none;">✓ Confirmar</a>'
            )
        
        if obj.status == 'CONFIRMED':
            actions.append(
                '<a href="#" style="color: #8b5cf6; text-decoration: none;">🍳 Preparar</a>'
            )
        
        if obj.can_be_cancelled():
            actions.append(
                '<a href="#" style="color: #ef4444; text-decoration: none;">✗ Cancelar</a>'
            )
        
        if actions:
            return format_html('<br>'.join(actions))
        return '-'
    quick_actions.short_description = 'Acciones'
    
    # ========================================================================
    # READONLY FIELD DISPLAYS
    # ========================================================================
    
    def order_summary(self, obj):
        """Resumen del pedido"""
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<table style="width: 100%;">'
            '<tr><td><strong>Pedido:</strong></td><td>#{}</td></tr>'
            '<tr><td><strong>Estado:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Items:</strong></td><td>{} items</td></tr>'
            '<tr><td><strong>Total:</strong></td><td style="font-size: 18px; color: #16a34a;"><strong>${:.2f}</strong></td></tr>'
            '<tr><td><strong>Calificado:</strong></td><td>{}</td></tr>'
            '</table>'
            '</div>',
            obj.order_number,
            obj.get_status_display(),
            obj.total_items,
            obj.total,
            '⭐ Sí' if obj.is_rated else '- No'
        )
    order_summary.short_description = 'Resumen'
    
    def customer_info(self, obj):
        """Información del cliente"""
        profile = getattr(obj.customer, 'customer_profile', None)
        total_orders = profile.total_orders if profile else 0
        total_spent = profile.total_spent if profile else 0
        
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<p><strong>Nombre:</strong> {}</p>'
            '<p><strong>Email:</strong> {}</p>'
            '<p><strong>Teléfono:</strong> {}</p>'
            '<p><strong>Pedidos totales:</strong> {}</p>'
            '<p><strong>Total gastado:</strong> ${:.2f}</p>'
            '</div>',
            obj.customer.get_full_name() or obj.customer.username,
            obj.customer.email,
            obj.customer.phone or 'No registrado',
            total_orders,
            total_spent
        )
    customer_info.short_description = 'Info del Cliente'
    
    def restaurant_info(self, obj):
        """Información del restaurante"""
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<p><strong>Restaurante:</strong> {}</p>'
            '<p><strong>Tipo:</strong> {}</p>'
            '<p><strong>Teléfono:</strong> {}</p>'
            '<p><strong>Rating:</strong> {} ({} reseñas)</p>'
            '<p><strong>Tiempo de entrega:</strong> {}-{} min</p>'
            '</div>',
            obj.restaurant.name,
            obj.restaurant.get_cuisine_type_display(),
            obj.restaurant.phone,
            '⭐' * int(obj.restaurant.rating),
            obj.restaurant.total_reviews,
            obj.restaurant.delivery_time_min,
            obj.restaurant.delivery_time_max
        )
    restaurant_info.short_description = 'Info del Restaurante'
    
    def driver_info(self, obj):
        """Información del conductor"""
        if not obj.driver:
            return format_html(
                '<div style="background: #fef2f2; padding: 15px; border-radius: 8px; color: #991b1b;">'
                '<p><strong>⚠️ Sin conductor asignado</strong></p>'
                '</div>'
            )
        
        profile = getattr(obj.driver, 'driver_profile', None)
        
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<p><strong>Nombre:</strong> {}</p>'
            '<p><strong>Teléfono:</strong> {}</p>'
            '<p><strong>Vehículo:</strong> {} - {}</p>'
            '<p><strong>Rating:</strong> {} ({:.1f})</p>'
            '<p><strong>Entregas totales:</strong> {}</p>'
            '</div>',
            obj.driver.get_full_name(),
            obj.driver.phone,
            profile.get_vehicle_type_display() if profile else 'N/A',
            profile.vehicle_plate if profile else 'N/A',
            '⭐' * int(profile.rating) if profile else '',
            profile.rating if profile else 0,
            profile.total_deliveries if profile else 0
        )
    driver_info.short_description = 'Info del Conductor'
    
    def delivery_info(self, obj):
        """Información de la entrega"""
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<p><strong>Dirección:</strong> {}</p>'
            '<p><strong>Referencias:</strong> {}</p>'
            '<p><strong>Distancia:</strong> {} km</p>'
            '<p><strong>Costo de envío:</strong> ${:.2f}</p>'
            '</div>',
            obj.delivery_address,
            obj.delivery_reference or 'Sin referencias',
            obj.delivery_distance or 'No calculada',
            obj.delivery_fee
        )
    delivery_info.short_description = 'Info de Entrega'
    
    def payment_info(self, obj):
        """Información del pago"""
        paid_status = '✅ Pagado' if obj.is_paid else '⏳ Pendiente'
        paid_color = '#16a34a' if obj.is_paid else '#f59e0b'
        
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<p><strong>Estado:</strong> <span style="color: {};">{}</span></p>'
            '<p><strong>Método:</strong> {}</p>'
            '<p><strong>Subtotal:</strong> ${:.2f}</p>'
            '<p><strong>Envío:</strong> ${:.2f}</p>'
            '<p><strong>Servicio:</strong> ${:.2f}</p>'
            '<p><strong>Descuento:</strong> -${:.2f}</p>'
            '<p><strong>Propina:</strong> ${:.2f}</p>'
            '<p><strong style="font-size: 16px;">Total:</strong> <strong style="color: #16a34a; font-size: 18px;">${:.2f}</strong></p>'
            '{}'
            '</div>',
            paid_color,
            paid_status,
            obj.get_payment_method_display(),
            obj.subtotal,
            obj.delivery_fee,
            obj.service_fee,
            obj.discount,
            obj.tip,
            obj.total,
            f'<p><strong>Transacción:</strong> {obj.transaction_id}</p>' if obj.transaction_id else ''
        )
    payment_info.short_description = 'Info de Pago'
    
    def timeline_display(self, obj):
        """Timeline del pedido"""
        timeline = []
        
        timeline.append(f'<p>📝 <strong>Creado:</strong> {obj.created_at.strftime("%d/%m/%Y %H:%M")}</p>')
        
        if obj.confirmed_at:
            timeline.append(f'<p>✅ <strong>Confirmado:</strong> {obj.confirmed_at.strftime("%d/%m/%Y %H:%M")}</p>')
        
        if obj.preparing_at:
            timeline.append(f'<p>🍳 <strong>Preparando:</strong> {obj.preparing_at.strftime("%d/%m/%Y %H:%M")}</p>')
        
        if obj.ready_at:
            timeline.append(f'<p>📦 <strong>Listo:</strong> {obj.ready_at.strftime("%d/%m/%Y %H:%M")}</p>')
        
        if obj.picked_up_at:
            timeline.append(f'<p>🚗 <strong>Recogido:</strong> {obj.picked_up_at.strftime("%d/%m/%Y %H:%M")}</p>')
        
        if obj.delivered_at:
            delta = obj.delivered_at - obj.created_at
            minutes = int(delta.total_seconds() / 60)
            timeline.append(f'<p>✅ <strong>Entregado:</strong> {obj.delivered_at.strftime("%d/%m/%Y %H:%M")} ({minutes} min total)</p>')
        
        if obj.cancelled_at:
            timeline.append(f'<p>❌ <strong>Cancelado:</strong> {obj.cancelled_at.strftime("%d/%m/%Y %H:%M")}</p>')
        
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '{}'
            '</div>',
            ''.join(timeline)
        )
    timeline_display.short_description = 'Timeline'
    
    def map_preview(self, obj):
        """Preview del mapa"""
        # Usando Google Maps Static API (necesitarás una API key)
        # O puedes usar OpenStreetMap
        return format_html(
            '<div style="margin-top: 10px;">'
            '<a href="https://www.google.com/maps?q={},{}" target="_blank" '
            'style="background: #3b82f6; color: white; padding: 8px 16px; '
            'text-decoration: none; border-radius: 6px; display: inline-block;">'
            '🗺️ Ver en Google Maps'
            '</a>'
            '<p style="margin-top: 10px; color: #6b7280; font-size: 12px;">'
            'Lat: {}, Lng: {}'
            '</p>'
            '</div>',
            obj.delivery_latitude,
            obj.delivery_longitude,
            obj.delivery_latitude,
            obj.delivery_longitude
        )
    map_preview.short_description = 'Mapa'
    
    # ========================================================================
    # ACTIONS
    # ========================================================================
    
    @admin.action(description='✅ Marcar como Confirmado')
    def mark_as_confirmed(self, request, queryset):
        """Confirmar pedidos seleccionados"""
        updated = 0
        for order in queryset.filter(status='PENDING'):
            try:
                order.confirm(confirmed_by=request.user)
                updated += 1
            except Exception as e:
                self.message_user(
                    request,
                    f'Error confirmando pedido {order.order_number}: {str(e)}',
                    level=messages.ERROR
                )
        
        if updated:
            self.message_user(
                request,
                f'{updated} pedido(s) confirmado(s) correctamente.',
                level=messages.SUCCESS
            )
    
    @admin.action(description='🍳 Marcar como En Preparación')
    def mark_as_preparing(self, request, queryset):
        """Marcar pedidos como en preparación"""
        updated = 0
        for order in queryset.filter(status='CONFIRMED'):
            try:
                order.start_preparing(changed_by=request.user)
                updated += 1
            except Exception as e:
                self.message_user(
                    request,
                    f'Error en pedido {order.order_number}: {str(e)}',
                    level=messages.ERROR
                )
        
        if updated:
            self.message_user(
                request,
                f'{updated} pedido(s) en preparación.',
                level=messages.SUCCESS
            )
    
    @admin.action(description='📦 Marcar como Listo')
    def mark_as_ready(self, request, queryset):
        """Marcar pedidos como listos"""
        updated = 0
        for order in queryset.filter(status='PREPARING'):
            try:
                order.mark_ready(changed_by=request.user)
                updated += 1
            except Exception as e:
                self.message_user(
                    request,
                    f'Error en pedido {order.order_number}: {str(e)}',
                    level=messages.ERROR
                )
        
        if updated:
            self.message_user(
                request,
                f'{updated} pedido(s) listo(s) para entrega.',
                level=messages.SUCCESS
            )
    
    @admin.action(description='✅ Marcar como Entregado')
    def mark_as_delivered(self, request, queryset):
        """Marcar pedidos como entregados"""
        updated = 0
        for order in queryset.filter(status='IN_TRANSIT'):
            try:
                order.mark_delivered(changed_by=request.user)
                updated += 1
            except Exception as e:
                self.message_user(
                    request,
                    f'Error en pedido {order.order_number}: {str(e)}',
                    level=messages.ERROR
                )
        
        if updated:
            self.message_user(
                request,
                f'{updated} pedido(s) entregado(s) correctamente.',
                level=messages.SUCCESS
            )
    
    @admin.action(description='❌ Cancelar Pedidos')
    def cancel_orders(self, request, queryset):
        """Cancelar pedidos seleccionados"""
        updated = 0
        for order in queryset:
            if order.can_be_cancelled():
                try:
                    order.cancel(
                        reason='OTHER',
                        notes='Cancelado desde admin',
                        cancelled_by=request.user
                    )
                    updated += 1
                except Exception as e:
                    self.message_user(
                        request,
                        f'Error cancelando pedido {order.order_number}: {str(e)}',
                        level=messages.ERROR
                    )
        
        if updated:
            self.message_user(
                request,
                f'{updated} pedido(s) cancelado(s).',
                level=messages.WARNING
            )
    
    @admin.action(description='📥 Exportar a CSV')
    def export_to_csv(self, request, queryset):
        """Exportar pedidos a CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="pedidos.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Número de Pedido',
            'Cliente',
            'Restaurante',
            'Estado',
            'Total',
            'Método de Pago',
            'Pagado',
            'Fecha de Creación'
        ])
        
        for order in queryset:
            writer.writerow([
                order.order_number,
                order.customer.get_full_name(),
                order.restaurant.name,
                order.get_status_display(),
                f'${order.total}',
                order.get_payment_method_display(),
                'Sí' if order.is_paid else 'No',
                order.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    
    # ========================================================================
    # CUSTOM METHODS
    # ========================================================================
    
    def get_queryset(self, request):
        """Optimizar queries"""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'customer',
            'restaurant',
            'driver'
        ).prefetch_related(
            'items',
            'status_history'
        )
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar pedidos, solo cancelar"""
        return False


# ============================================================================
# ADMIN DE ORDER ITEMS
# ============================================================================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Administración de Items de Pedido"""
    
    list_display = [
        'order_number',
        'product_name',
        'quantity',
        'unit_price',
        'subtotal',
        'customizations_preview'
    ]
    
    list_filter = [
        'order__status',
        'order__created_at'
    ]
    
    search_fields = [
        'order__order_number',
        'product_name',
        'product__name'
    ]
    
    readonly_fields = [
        'order',
        'product',
        'extras_total',
        'options_total',
        'subtotal',
        'created_at',
        'customizations_display'
    ]
    
    fieldsets = (
        ('Pedido', {
            'fields': ('order',)
        }),
        ('Producto', {
            'fields': (
                'product',
                'product_name',
                'product_description',
                'product_image'
            )
        }),
        ('Precio y Cantidad', {
            'fields': (
                'unit_price',
                'quantity',
                'subtotal'
            )
        }),
        ('Personalizaciones', {
            'fields': (
                'selected_extras',
                'extras_total',
                'selected_options',
                'options_total',
                'special_notes',
                'customizations_display'
            )
        }),
        ('Información del Sistema', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def order_number(self, obj):
        return obj.order.order_number
    order_number.short_description = 'Pedido'
    order_number.admin_order_field = 'order__order_number'
    
    def customizations_preview(self, obj):
        """Preview de las personalizaciones"""
        custom = obj.get_customizations_display()
        if len(custom) > 50:
            return custom[:50] + '...'
        return custom
    customizations_preview.short_description = 'Personalizaciones'
    
    def customizations_display(self, obj):
        """Display completo de personalizaciones"""
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<p>{}</p>'
            '</div>',
            obj.get_customizations_display().replace(' | ', '<br>')
        )
    customizations_display.short_description = 'Detalles'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================================
# ADMIN DE RATING
# ============================================================================

@admin.register(OrderRating)
class OrderRatingAdmin(admin.ModelAdmin):
    """Administración de Calificaciones"""
    
    list_display = [
        'order_number',
        'overall_rating_stars',
        'food_rating_display',
        'delivery_rating_display',
        'driver_rating_display',
        'would_order_again_display',
        'created_at'
    ]
    
    list_filter = [
        'overall_rating',
        'food_rating',
        'delivery_rating',
        'driver_rating',
        'would_order_again',
        'created_at'
    ]
    
    search_fields = [
        'order__order_number',
        'comment',
        'driver_comment'
    ]
    
    readonly_fields = [
        'order',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Pedido', {
            'fields': ('order',)
        }),
        ('Calificaciones', {
            'fields': (
                'overall_rating',
                'food_rating',
                'delivery_rating',
                'driver_rating'
            )
        }),
        ('Comentarios', {
            'fields': (
                'comment',
                'driver_comment'
            )
        }),
        ('Aspectos', {
            'fields': (
                'liked_aspects',
                'disliked_aspects'
            )
        }),
        ('Feedback', {
            'fields': ('would_order_again',)
        }),
        ('Información del Sistema', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def order_number(self, obj):
        return obj.order.order_number
    order_number.short_description = 'Pedido'
    
    def overall_rating_stars(self, obj):
        stars = '⭐' * obj.overall_rating
        return format_html('<span style="font-size: 16px;">{}</span>', stars)
    overall_rating_stars.short_description = 'Calificación General'
    
    def food_rating_display(self, obj):
        if obj.food_rating:
            return '⭐' * obj.food_rating
        return '-'
    food_rating_display.short_description = 'Comida'
    
    def delivery_rating_display(self, obj):
        if obj.delivery_rating:
            return '⭐' * obj.delivery_rating
        return '-'
    delivery_rating_display.short_description = 'Entrega'
    
    def driver_rating_display(self, obj):
        if obj.driver_rating:
            return '⭐' * obj.driver_rating
        return '-'
    driver_rating_display.short_description = 'Conductor'
    
    def would_order_again_display(self, obj):
        if obj.would_order_again:
            return format_html('<span style="color: #16a34a;">✓ Sí</span>')
        return format_html('<span style="color: #ef4444;">✗ No</span>')
    would_order_again_display.short_description = '¿Ordenaría de nuevo?'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================================
# ADMIN DE STATUS HISTORY
# ============================================================================

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    """Administración de Historial de Estados"""
    
    list_display = [
        'order_number',
        'status_badge',
        'changed_by_display',
        'notes_preview',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'created_at'
    ]
    
    search_fields = [
        'order__order_number',
        'notes'
    ]
    
    readonly_fields = [
        'order',
        'status',
        'notes',
        'changed_by',
        'created_at'
    ]
    
    def order_number(self, obj):
        return obj.order.order_number
    order_number.short_description = 'Pedido'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#f59e0b',
            'CONFIRMED': '#3b82f6',
            'PREPARING': '#8b5cf6',
            'READY': '#06b6d4',
            'PICKED_UP': '#14b8a6',
            'IN_TRANSIT': '#10b981',
            'DELIVERED': '#22c55e',
            'CANCELLED': '#ef4444'
        }
        
        color = colors.get(obj.status, '#6b7280')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def changed_by_display(self, obj):
        if obj.changed_by:
            return obj.changed_by.get_full_name() or obj.changed_by.username
        return 'Sistema'
    changed_by_display.short_description = 'Cambiado por'
    
    def notes_preview(self, obj):
        if obj.notes:
            return obj.notes[:50] + '...' if len(obj.notes) > 50 else obj.notes
        return '-'
    notes_preview.short_description = 'Notas'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False