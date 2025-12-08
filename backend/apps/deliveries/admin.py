# apps/deliveries/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Avg, Sum
from django.contrib import messages
from .models import (
    Delivery,
    DeliveryStatusHistory,
    DeliveryLocation,
    DeliveryIssue
)


# ============================================================================
# INLINES
# ============================================================================

class DeliveryStatusHistoryInline(admin.TabularInline):
    """Inline para historial de estados"""
    model = DeliveryStatusHistory
    extra = 0
    fields = ['status', 'notes', 'changed_by', 'created_at']
    readonly_fields = ['status', 'notes', 'changed_by', 'created_at']
    can_delete = False
    ordering = ['-created_at']
    
    def has_add_permission(self, request, obj=None):
        return False


class DeliveryIssueInline(admin.TabularInline):
    """Inline para problemas de entrega"""
    model = DeliveryIssue
    extra = 0
    fields = ['issue_type', 'description', 'is_resolved', 'created_at']
    readonly_fields = ['created_at']


class DeliveryLocationInline(admin.TabularInline):
    """Inline para ubicaciones (últimas 10)"""
    model = DeliveryLocation
    extra = 0
    fields = ['latitude', 'longitude', 'speed', 'accuracy', 'timestamp']
    readonly_fields = ['latitude', 'longitude', 'speed', 'accuracy', 'timestamp']
    can_delete = False
    ordering = ['-timestamp']
    
    def get_queryset(self, request):
        """Mostrar solo las últimas 10 ubicaciones"""
        queryset = super().get_queryset(request)
        return queryset[:10]
    
    def has_add_permission(self, request, obj=None):
        return False


# ============================================================================
# ADMIN PRINCIPAL DE DELIVERY
# ============================================================================

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    """Administración de Entregas"""
    
    list_display = [
        'order_number',
        'status_badge',
        'driver_link',
        'customer_info',
        'restaurant_info',
        'distance_display',
        'earnings_display',
        'time_info',
        'priority_badge',
        'quick_actions'
    ]
    
    list_filter = [
        'status',
        'priority',
        'delivery_attempts',
        'failure_reason',
        'created_at',
        'driver'
    ]
    
    search_fields = [
        'order__order_number',
        'driver__first_name',
        'driver__last_name',
        'customer_name',
        'customer_phone',
        'delivery_address',
        'pickup_address'
    ]
    
    readonly_fields = [
        'order',
        'created_at',
        'updated_at',
        'delivery_summary',
        'driver_info_display',
        'customer_info_display',
        'restaurant_info_display',
        'pickup_info',
        'delivery_info',
        'timeline_display',
        'map_preview',
        'proof_display',
        'location_tracking_display',
        'driver_earnings'
    ]
    
    inlines = [
        DeliveryStatusHistoryInline,
        DeliveryIssueInline,
        DeliveryLocationInline
    ]
    
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('📦 Información de la Entrega', {
            'fields': (
                'order',
                'status',
                'priority',
                'delivery_summary'
            )
        }),
        ('🚗 Conductor', {
            'fields': (
                'driver',
                'driver_info_display'
            )
        }),
        ('👤 Cliente', {
            'fields': (
                'customer_name',
                'customer_phone',
                'customer_info_display'
            )
        }),
        ('🏪 Restaurante (Pickup)', {
            'fields': (
                'pickup_address',
                ('pickup_latitude', 'pickup_longitude'),
                'pickup_info',
                'restaurant_info_display'
            )
        }),
        ('📍 Entrega (Delivery)', {
            'fields': (
                'delivery_address',
                'delivery_reference',
                ('delivery_latitude', 'delivery_longitude'),
                'delivery_info'
            )
        }),
        ('📏 Distancias y Tiempos', {
            'fields': (
                'total_distance',
                'estimated_pickup_time',
                'estimated_delivery_time',
                'timeline_display'
            )
        }),
        ('💰 Costos y Ganancias', {
            'fields': (
                'delivery_fee',
                'tip',
                'driver_earnings'
            )
        }),
        ('📝 Instrucciones', {
            'fields': (
                'special_instructions',
            )
        }),
        ('✅ Prueba de Entrega', {
            'fields': (
                'delivery_proof_photo',
                'delivery_signature',
                'delivery_notes',
                'proof_display'
            ),
            'classes': ('collapse',)
        }),
        ('❌ Información de Falla', {
            'fields': (
                'delivery_attempts',
                'max_delivery_attempts',
                'failure_reason',
                'failure_notes',
                'failure_photo'
            ),
            'classes': ('collapse',)
        }),
        ('🗺️ Tracking', {
            'fields': (
                'map_preview',
                'location_tracking_display'
            ),
            'classes': ('collapse',)
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
        'assign_to_driver',
        'mark_as_picked_up',
        'mark_as_in_transit',
        'mark_as_delivered',
        'cancel_deliveries',
        'increase_priority'
    ]
    
    # ========================================================================
    # DISPLAY METHODS
    # ========================================================================
    
    def order_number(self, obj):
        """Número de pedido"""
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html(
            '<a href="{}" style="text-decoration: none; font-weight: bold;">'
            '📦 #{}</a>',
            url,
            obj.order.order_number
        )
    order_number.short_description = 'Pedido'
    order_number.admin_order_field = 'order__order_number'
    
    def status_badge(self, obj):
        """Badge de estado con colores"""
        colors = {
            'PENDING': '#f59e0b',        # Orange
            'ASSIGNED': '#3b82f6',       # Blue
            'PICKING_UP': '#8b5cf6',     # Purple
            'PICKED_UP': '#06b6d4',      # Cyan
            'IN_TRANSIT': '#10b981',     # Green
            'ARRIVED': '#14b8a6',        # Teal
            'DELIVERED': '#22c55e',      # Green
            'FAILED': '#ef4444',         # Red
            'CANCELLED': '#6b7280'       # Gray
        }
        
        color = colors.get(obj.status, '#6b7280')
        
        # Agregar icono de retraso
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
    driver_link.short_description = 'Conductor'
    
    def customer_info(self, obj):
        """Información del cliente"""
        return format_html(
            '<strong>👤 {}</strong><br>'
            '<span style="color: #6b7280; font-size: 11px;">{}</span>',
            obj.customer_name,
            obj.customer_phone
        )
    customer_info.short_description = 'Cliente'
    
    def restaurant_info(self, obj):
        """Información del restaurante"""
        url = reverse('admin:restaurants_restaurant_change', args=[obj.order.restaurant.id])
        return format_html(
            '<a href="{}" style="text-decoration: none;">'
            '<strong>🏪 {}</strong>'
            '</a>',
            url,
            obj.order.restaurant.name
        )
    restaurant_info.short_description = 'Restaurante'
    
    def distance_display(self, obj):
        """Distancia total"""
        if obj.total_distance:
            return format_html(
                '<strong style="color: #3b82f6;">{} km</strong>',
                obj.total_distance
            )
        return '-'
    distance_display.short_description = 'Distancia'
    
    def earnings_display(self, obj):
        """Ganancias del conductor"""
        return format_html(
            '<strong style="color: #16a34a; font-size: 14px;">${:.2f}</strong><br>'
            '<span style="color: #6b7280; font-size: 10px;">Fee: ${:.2f} | Tip: ${:.2f}</span>',
            obj.driver_earnings,
            obj.delivery_fee,
            obj.tip
        )
    earnings_display.short_description = 'Ganancias'
    
    def time_info(self, obj):
        """Información de tiempos"""
        if obj.status == 'DELIVERED' and obj.total_delivery_time:
            return format_html(
                '<span style="color: #16a34a;">✓ {} min</span>',
                obj.total_delivery_time
            )
        elif obj.estimated_delivery_time:
            now = timezone.now()
            if obj.estimated_delivery_time > now:
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
    time_info.short_description = 'Tiempo'
    
    def priority_badge(self, obj):
        """Badge de prioridad"""
        if obj.priority > 5:
            color = '#ef4444'
            icon = '🔴'
        elif obj.priority > 2:
            color = '#f59e0b'
            icon = '🟡'
        else:
            color = '#6b7280'
            icon = '⚪'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icon,
            obj.priority
        )
    priority_badge.short_description = 'Prioridad'
    priority_badge.admin_order_field = 'priority'
    
    def quick_actions(self, obj):
        """Acciones rápidas"""
        actions = []
        
        if obj.status == 'PENDING':
            actions.append('<span style="color: #3b82f6;">📋 Pendiente</span>')
        
        if obj.status == 'ASSIGNED':
            actions.append('<span style="color: #8b5cf6;">🚗 Asignado</span>')
        
        if obj.status in ['PICKING_UP', 'PICKED_UP', 'IN_TRANSIT']:
            actions.append('<span style="color: #10b981;">🔄 En Proceso</span>')
        
        if obj.status == 'DELIVERED':
            actions.append('<span style="color: #16a34a;">✅ Entregado</span>')
        
        if actions:
            return format_html('<br>'.join(actions))
        return '-'
    quick_actions.short_description = 'Estado Actual'
    
    # ========================================================================
    # READONLY FIELD DISPLAYS
    # ========================================================================
    
    def delivery_summary(self, obj):
        """Resumen de la entrega"""
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<table style="width: 100%;">'
            '<tr><td><strong>Pedido:</strong></td><td>#{}</td></tr>'
            '<tr><td><strong>Estado:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Conductor:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Distancia:</strong></td><td>{} km</td></tr>'
            '<tr><td><strong>Ganancias:</strong></td><td style="font-size: 16px; color: #16a34a;"><strong>${:.2f}</strong></td></tr>'
            '<tr><td><strong>Intentos:</strong></td><td>{}/{}</td></tr>'
            '</table>'
            '</div>',
            obj.order.order_number,
            obj.get_status_display(),
            obj.driver.get_full_name() if obj.driver else 'Sin asignar',
            obj.total_distance or 'No calculada',
            obj.driver_earnings,
            obj.delivery_attempts,
            obj.max_delivery_attempts
        )
    delivery_summary.short_description = 'Resumen'
    
    def driver_info_display(self, obj):
        """Información detallada del conductor"""
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
            '<p><strong>Estado:</strong> {}</p>'
            '<p><strong>Rating:</strong> {} ({:.1f})</p>'
            '<p><strong>Entregas totales:</strong> {}</p>'
            '</div>',
            obj.driver.get_full_name(),
            obj.driver.phone,
            profile.get_vehicle_type_display() if profile else 'N/A',
            profile.vehicle_plate if profile else 'N/A',
            profile.get_status_display() if profile else 'N/A',
            '⭐' * int(profile.rating) if profile else '',
            profile.rating if profile else 0,
            profile.total_deliveries if profile else 0
        )
    driver_info_display.short_description = 'Info del Conductor'
    
    def customer_info_display(self, obj):
        """Información del cliente"""
        url = reverse('admin:users_user_change', args=[obj.order.customer.id])
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<p><strong>Nombre:</strong> {}</p>'
            '<p><strong>Teléfono:</strong> {}</p>'
            '<p><strong>Email:</strong> {}</p>'
            '<p><a href="{}" style="color: #3b82f6;">Ver perfil completo →</a></p>'
            '</div>',
            obj.customer_name,
            obj.customer_phone,
            obj.order.customer.email,
            url
        )
    customer_info_display.short_description = 'Info del Cliente'
    
    def restaurant_info_display(self, obj):
        """Información del restaurante"""
        restaurant = obj.order.restaurant
        url = reverse('admin:restaurants_restaurant_change', args=[restaurant.id])
        
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<p><strong>Restaurante:</strong> {}</p>'
            '<p><strong>Teléfono:</strong> {}</p>'
            '<p><strong>Dirección:</strong> {}</p>'
            '<p><a href="{}" style="color: #3b82f6;">Ver restaurante →</a></p>'
            '</div>',
            restaurant.name,
            restaurant.phone,
            restaurant.address,
            url
        )
    restaurant_info_display.short_description = 'Info del Restaurante'
    
    def pickup_info(self, obj):
        """Información de recogida"""
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<p><strong>Dirección:</strong> {}</p>'
            '<p><strong>Coordenadas:</strong> {}, {}</p>'
            '</div>',
            obj.pickup_address,
            obj.pickup_latitude,
            obj.pickup_longitude
        )
    pickup_info.short_description = 'Info de Recogida'
    
    def delivery_info(self, obj):
        """Información de entrega"""
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<p><strong>Dirección:</strong> {}</p>'
            '<p><strong>Referencias:</strong> {}</p>'
            '<p><strong>Coordenadas:</strong> {}, {}</p>'
            '</div>',
            obj.delivery_address,
            obj.delivery_reference or 'Sin referencias',
            obj.delivery_latitude,
            obj.delivery_longitude
        )
    delivery_info.short_description = 'Info de Entrega'
    
    def timeline_display(self, obj):
        """Timeline de la entrega"""
        timeline = []
        
        timeline.append(f'<p>📝 <strong>Creado:</strong> {obj.created_at.strftime("%d/%m/%Y %H:%M")}</p>')
        
        if obj.assigned_at:
            timeline.append(f'<p>✅ <strong>Asignado:</strong> {obj.assigned_at.strftime("%d/%m/%Y %H:%M")}</p>')
        
        if obj.pickup_started_at:
            timeline.append(f'<p>🚗 <strong>Inicio recogida:</strong> {obj.pickup_started_at.strftime("%d/%m/%Y %H:%M")}</p>')
        
        if obj.picked_up_at:
            timeline.append(f'<p>📦 <strong>Recogido:</strong> {obj.picked_up_at.strftime("%d/%m/%Y %H:%M")}</p>')
            if obj.pickup_time:
                timeline.append(f'<p style="color: #6b7280; margin-left: 20px;">⏱️ Tiempo de recogida: {obj.pickup_time} min</p>')
        
        if obj.in_transit_at:
            timeline.append(f'<p>🚙 <strong>En tránsito:</strong> {obj.in_transit_at.strftime("%d/%m/%Y %H:%M")}</p>')
        
        if obj.arrived_at:
            timeline.append(f'<p>📍 <strong>Llegada:</strong> {obj.arrived_at.strftime("%d/%m/%Y %H:%M")}</p>')
        
        if obj.delivered_at:
            timeline.append(f'<p>✅ <strong>Entregado:</strong> {obj.delivered_at.strftime("%d/%m/%Y %H:%M")}</p>')
            if obj.total_delivery_time:
                timeline.append(f'<p style="color: #16a34a; font-weight: bold; margin-left: 20px;">⏱️ Tiempo total: {obj.total_delivery_time} min</p>')
        
        if obj.failed_at:
            timeline.append(f'<p>❌ <strong>Fallido:</strong> {obj.failed_at.strftime("%d/%m/%Y %H:%M")}</p>')
            timeline.append(f'<p style="color: #ef4444; margin-left: 20px;">Razón: {obj.get_failure_reason_display()}</p>')
        
        if obj.cancelled_at:
            timeline.append(f'<p>🚫 <strong>Cancelado:</strong> {obj.cancelled_at.strftime("%d/%m/%Y %H:%M")}</p>')
        
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '{}'
            '</div>',
            ''.join(timeline)
        )
    timeline_display.short_description = 'Timeline'
    
    def map_preview(self, obj):
        """Preview del mapa con ruta"""
        return format_html(
            '<div style="margin-top: 10px;">'
            '<a href="https://www.google.com/maps/dir/{},{}/{},{}/" target="_blank" '
            'style="background: #3b82f6; color: white; padding: 8px 16px; '
            'text-decoration: none; border-radius: 6px; display: inline-block;">'
            '🗺️ Ver Ruta en Google Maps'
            '</a>'
            '<p style="margin-top: 10px; color: #6b7280; font-size: 12px;">'
            '📍 Pickup: {}, {}<br>'
            '📍 Delivery: {}, {}'
            '</p>'
            '</div>',
            obj.pickup_latitude,
            obj.pickup_longitude,
            obj.delivery_latitude,
            obj.delivery_longitude,
            obj.pickup_latitude,
            obj.pickup_longitude,
            obj.delivery_latitude,
            obj.delivery_longitude
        )
    map_preview.short_description = 'Mapa'
    
    def proof_display(self, obj):
        """Display de prueba de entrega"""
        if obj.status != 'DELIVERED':
            return format_html(
                '<p style="color: #6b7280;">Disponible cuando se complete la entrega</p>'
            )
        
        proof_html = []
        
        if obj.delivery_proof_photo:
            proof_html.append(
                f'<div style="margin-bottom: 10px;">'
                f'<strong>📸 Foto de prueba:</strong><br>'
                f'<img src="{obj.delivery_proof_photo.url}" style="max-width: 300px; border-radius: 8px; margin-top: 5px;" />'
                f'</div>'
            )
        
        if obj.delivery_signature:
            proof_html.append(
                f'<div style="margin-bottom: 10px;">'
                f'<strong>✍️ Firma digital:</strong> Registrada'
                f'</div>'
            )
        
        if obj.delivery_notes:
            proof_html.append(
                f'<div style="margin-bottom: 10px;">'
                f'<strong>📝 Notas:</strong><br>'
                f'<p style="background: #f3f4f6; padding: 10px; border-radius: 6px;">{obj.delivery_notes}</p>'
                f'</div>'
            )
        
        if not proof_html:
            return format_html('<p style="color: #f59e0b;">⚠️ Sin prueba de entrega registrada</p>')
        
        return format_html(''.join(proof_html))
    proof_display.short_description = 'Prueba de Entrega'
    
    def location_tracking_display(self, obj):
        """Display del tracking de ubicación"""
        locations = obj.location_tracking.order_by('-timestamp')[:5]
        
        if not locations:
            return format_html(
                '<p style="color: #6b7280;">No hay datos de tracking disponibles</p>'
            )
        
        location_html = ['<table style="width: 100%; border-collapse: collapse;">']
        location_html.append(
            '<tr style="background: #f3f4f6;">'
            '<th style="padding: 8px; text-align: left;">Timestamp</th>'
            '<th style="padding: 8px; text-align: left;">Ubicación</th>'
            '<th style="padding: 8px; text-align: left;">Velocidad</th>'
            '</tr>'
        )
        
        for loc in locations:
            speed_text = f"{loc.speed:.1f} km/h" if loc.speed else '-'
            location_html.append(
                f'<tr>'
                f'<td style="padding: 8px;">{loc.timestamp.strftime("%H:%M:%S")}</td>'
                f'<td style="padding: 8px;">{loc.latitude}, {loc.longitude}</td>'
                f'<td style="padding: 8px;">{speed_text}</td>'
                f'</tr>'
            )
        
        location_html.append('</table>')
        
        return format_html(''.join(location_html))
    location_tracking_display.short_description = 'Últimas Ubicaciones'
    
    # ========================================================================
    # ACTIONS
    # ========================================================================
    
    @admin.action(description='👤 Asignar a conductor')
    def assign_to_driver(self, request, queryset):
        """Acción para asignar conductores (requiere selección manual)"""
        # Esta acción solo marca para revisión, la asignación real se hace en el formulario
        pending = queryset.filter(status='PENDING').count()
        
        if pending == 0:
            self.message_user(
                request,
                'No hay entregas pendientes seleccionadas',
                level=messages.WARNING
            )
        else:
            self.message_user(
                request,
                f'{pending} entrega(s) pendiente(s) de asignación',
                level=messages.INFO
            )
    
    @admin.action(description='📦 Marcar como Recogido')
    def mark_as_picked_up(self, request, queryset):
        """Marcar entregas como recogidas"""
        updated = 0
        for delivery in queryset:
            if delivery.status in ['ASSIGNED', 'PICKING_UP']:
                try:
                    delivery.confirm_pickup()
                    updated += 1
                except Exception as e:
                    self.message_user(
                        request,
                        f'Error en entrega {delivery.order.order_number}: {str(e)}',
                        level=messages.ERROR
                    )
        
        if updated:
            self.message_user(
                request,
                f'{updated} entrega(s) marcada(s) como recogida(s)',
                level=messages.SUCCESS
            )
    
    @admin.action(description='🚗 Marcar como En Tránsito')
    def mark_as_in_transit(self, request, queryset):
        """Marcar entregas como en tránsito"""
        updated = 0
        for delivery in queryset.filter(status='PICKED_UP'):
            try:
                delivery.start_transit()
                updated += 1
            except Exception as e:
                self.message_user(
                    request,
                    f'Error en entrega {delivery.order.order_number}: {str(e)}',
                    level=messages.ERROR
                )
        
        if updated:
            self.message_user(
                request,
                f'{updated} entrega(s) marcada(s) como en tránsito',
                level=messages.SUCCESS
            )
    
    @admin.action(description='✅ Marcar como Entregado')
    def mark_as_delivered(self, request, queryset):
        """Marcar entregas como entregadas"""
        updated = 0
        for delivery in queryset.filter(status__in=['IN_TRANSIT', 'ARRIVED']):
            try:
                delivery.complete_delivery(notes='Completado desde admin')
                updated += 1
            except Exception as e:
                self.message_user(
                    request,
                    f'Error en entrega {delivery.order.order_number}: {str(e)}',
                    level=messages.ERROR
                )
        
        if updated:
            self.message_user(
                request,
                f'{updated} entrega(s) completada(s)',
                level=messages.SUCCESS
            )
    
    @admin.action(description='❌ Cancelar Entregas')
    def cancel_deliveries(self, request, queryset):
        """Cancelar entregas"""
        updated = 0
        for delivery in queryset:
            if delivery.status not in ['DELIVERED', 'FAILED']:
                try:
                    delivery.cancel(reason='Cancelado desde admin')
                    updated += 1
                except Exception as e:
                    self.message_user(
                        request,
                        f'Error cancelando entrega {delivery.order.order_number}: {str(e)}',
                        level=messages.ERROR
                    )
        
        if updated:
            self.message_user(
                request,
                f'{updated} entrega(s) cancelada(s)',
                level=messages.WARNING
            )
    
    @admin.action(description='⬆️ Aumentar Prioridad')
    def increase_priority(self, request, queryset):
        """Aumentar prioridad de entregas"""
        for delivery in queryset:
            if delivery.priority < 10:
                delivery.priority += 1
                delivery.save()
        
        self.message_user(
            request,
            f'Prioridad aumentada para {queryset.count()} entrega(s)',
            level=messages.SUCCESS
        )
    
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
            'driver'
        ).prefetch_related(
            'status_history',
            'issues',
            'location_tracking'
        )
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar entregas"""
        return False


# ============================================================================
# ADMIN DE DELIVERY LOCATION
# ============================================================================

@admin.register(DeliveryLocation)
class DeliveryLocationAdmin(admin.ModelAdmin):
    """Administración de Ubicaciones de Entrega"""
    
    list_display = [
        'delivery_order',
        'driver_name',
        'coordinates',
        'speed_display',
        'accuracy_display',
        'battery_display',
        'timestamp'
    ]
    
    list_filter = [
        'driver',
        'timestamp'
    ]
    
    search_fields = [
        'delivery__order__order_number',
        'driver__first_name',
        'driver__last_name'
    ]
    
    readonly_fields = [
        'delivery',
        'driver',
        'latitude',
        'longitude',
        'accuracy',
        'speed',
        'heading',
        'battery_level',
        'timestamp',
        'map_link'
    ]
    
    def delivery_order(self, obj):
        return f"#{obj.delivery.order.order_number}"
    delivery_order.short_description = 'Pedido'
    
    def driver_name(self, obj):
        return obj.driver.get_full_name()
    driver_name.short_description = 'Conductor'
    
    def coordinates(self, obj):
        return format_html(
            '<span style="font-family: monospace;">{}, {}</span>',
            obj.latitude,
            obj.longitude
        )
    coordinates.short_description = 'Coordenadas'
    
    def speed_display(self, obj):
        if obj.speed:
            color = '#ef4444' if obj.speed > 60 else '#16a34a'
            return format_html(
                '<span style="color: {};">{:.1f} km/h</span>',
                color,
                obj.speed
            )
        return '-'
    speed_display.short_description = 'Velocidad'
    
    def accuracy_display(self, obj):
        if obj.accuracy:
            color = '#16a34a' if obj.accuracy < 20 else '#f59e0b' if obj.accuracy < 50 else '#ef4444'
            return format_html(
                '<span style="color: {};">±{:.1f}m</span>',
                color,
                obj.accuracy
            )
        return '-'
    accuracy_display.short_description = 'Precisión'
    
    def battery_display(self, obj):
        if obj.battery_level:
            color = '#ef4444' if obj.battery_level < 20 else '#f59e0b' if obj.battery_level < 50 else '#16a34a'
            return format_html(
                '<span style="color: {};">🔋 {}%</span>',
                color,
                obj.battery_level
            )
        return '-'
    battery_display.short_description = 'Batería'
    
    def map_link(self, obj):
        return format_html(
            '<a href="https://www.google.com/maps?q={},{}" target="_blank" '
            'style="background: #3b82f6; color: white; padding: 6px 12px; '
            'text-decoration: none; border-radius: 6px; display: inline-block;">'
            '🗺️ Ver en Mapa'
            '</a>',
            obj.latitude,
            obj.longitude
        )
    map_link.short_description = 'Mapa'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================================
# ADMIN DE DELIVERY ISSUE
# ============================================================================

@admin.register(DeliveryIssue)
class DeliveryIssueAdmin(admin.ModelAdmin):
    """Administración de Problemas de Entrega"""
    
    list_display = [
        'delivery_order',
        'issue_type_badge',
        'description_preview',
        'reported_by_display',
        'status_badge',
        'created_at'
    ]
    
    list_filter = [
        'issue_type',
        'is_resolved',
        'created_at'
    ]
    
    search_fields = [
        'delivery__order__order_number',
        'description',
        'resolution_notes'
    ]
    
    readonly_fields = [
        'delivery',
        'reported_by',
        'created_at',
        'photo_preview'
    ]
    
    fieldsets = (
        ('Información del Problema', {
            'fields': (
                'delivery',
                'issue_type',
                'description',
                'photo',
                'photo_preview',
                'reported_by'
            )
        }),
        ('Resolución', {
            'fields': (
                'is_resolved',
                'resolution_notes',
                'resolved_at'
            )
        }),
        ('Información del Sistema', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def delivery_order(self, obj):
        return f"#{obj.delivery.order.order_number}"
    delivery_order.short_description = 'Pedido'
    
    def issue_type_badge(self, obj):
        colors = {
            'TRAFFIC': '#f59e0b',
            'WEATHER': '#3b82f6',
            'VEHICLE': '#ef4444',
            'ACCIDENT': '#dc2626',
            'WRONG_ADDRESS': '#f59e0b',
            'CUSTOMER_ISSUE': '#8b5cf6',
            'RESTAURANT_DELAY': '#f97316',
            'OTHER': '#6b7280'
        }
        
        color = colors.get(obj.issue_type, '#6b7280')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_issue_type_display()
        )
    issue_type_badge.short_description = 'Tipo'
    
    def description_preview(self, obj):
        if len(obj.description) > 50:
            return obj.description[:50] + '...'
        return obj.description
    description_preview.short_description = 'Descripción'
    
    def reported_by_display(self, obj):
        return obj.reported_by.get_full_name()
    reported_by_display.short_description = 'Reportado por'
    
    def status_badge(self, obj):
        if obj.is_resolved:
            return format_html(
                '<span style="color: #16a34a; font-weight: bold;">✅ Resuelto</span>'
            )
        return format_html(
            '<span style="color: #ef4444; font-weight: bold;">⏳ Pendiente</span>'
        )
    status_badge.short_description = 'Estado'
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-width: 300px; border-radius: 8px;" />',
                obj.photo.url
            )
        return '-'
    photo_preview.short_description = 'Foto de Evidencia'


# ============================================================================
# ADMIN DE DELIVERY STATUS HISTORY
# ============================================================================

@admin.register(DeliveryStatusHistory)
class DeliveryStatusHistoryAdmin(admin.ModelAdmin):
    """Administración de Historial de Estados de Entrega"""
    
    list_display = [
        'delivery_order',
        'status_badge',
        'notes_preview',
        'changed_by_display',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'created_at'
    ]
    
    search_fields = [
        'delivery__order__order_number',
        'notes'
    ]
    
    readonly_fields = [
        'delivery',
        'status',
        'notes',
        'changed_by',
        'created_at'
    ]
    
    def delivery_order(self, obj):
        return f"#{obj.delivery.order.order_number}"
    delivery_order.short_description = 'Pedido'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#f59e0b',
            'ASSIGNED': '#3b82f6',
            'PICKING_UP': '#8b5cf6',
            'PICKED_UP': '#06b6d4',
            'IN_TRANSIT': '#10b981',
            'ARRIVED': '#14b8a6',
            'DELIVERED': '#22c55e',
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
    
    def notes_preview(self, obj):
        if obj.notes:
            return obj.notes[:50] + '...' if len(obj.notes) > 50 else obj.notes
        return '-'
    notes_preview.short_description = 'Notas'
    
    def changed_by_display(self, obj):
        if obj.changed_by:
            return obj.changed_by.get_full_name()
        return 'Sistema'
    changed_by_display.short_description = 'Cambiado por'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False