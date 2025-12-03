from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Sum, Avg
from .models import User, Customer, Driver


# ========================================
# USER ADMIN
# ========================================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username', 
        'email', 
        'get_full_name_display',
        'user_type_badge',
        'phone', 
        'is_verified_badge',
        'is_active',
        'created_at'
    )
    list_filter = (
        'user_type', 
        'is_active', 
        'is_verified', 
        'is_staff',
        'created_at'
    )
    search_fields = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'phone'
    )
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Información Personal'), {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')
        }),
        (_('Tipo de Usuario'), {
            'fields': ('user_type',)
        }),
        (_('Estado de Verificación'), {
            'fields': ('is_verified',)
        }),
        (_('Permisos'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Fechas Importantes'), {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 
                'email',
                'first_name',
                'last_name',
                'user_type',
                'phone',
                'password1', 
                'password2',
                'is_active',
                'is_verified'
            ),
        }),
    )
    
    actions = ['verify_users', 'unverify_users', 'activate_users', 'deactivate_users']
    
    def get_full_name_display(self, obj):
        """Mostrar nombre completo del usuario"""
        return obj.get_full_name() or '-'
    get_full_name_display.short_description = 'Nombre Completo'
    
    def user_type_badge(self, obj):
        """Badge con color para el tipo de usuario"""
        colors = {
            'ADMIN': '#dc3545',        # Rojo
            'CUSTOMER': '#28a745',     # Verde
            'DRIVER': '#007bff',       # Azul
            'RESTAURANT': '#ffc107',   # Amarillo
        }
        color = colors.get(obj.user_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_user_type_display()
        )
    user_type_badge.short_description = 'Tipo'
    
    def is_verified_badge(self, obj):
        """Badge para estado de verificación"""
        if obj.is_verified:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-weight: bold; font-size: 11px;">✓ Verificado</span>'
            )
        return format_html(
            '<span style="background-color: #ffc107; color: #333; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold; font-size: 11px;">⚠ Sin verificar</span>'
        )
    is_verified_badge.short_description = 'Verificación'
    
    # Acciones masivas
    def verify_users(self, request, queryset):
        """Verificar usuarios seleccionados"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} usuario(s) verificado(s) exitosamente.')
    verify_users.short_description = '✓ Verificar usuarios seleccionados'
    
    def unverify_users(self, request, queryset):
        """Desverificar usuarios seleccionados"""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} usuario(s) desverificado(s).')
    unverify_users.short_description = '✗ Desverificar usuarios seleccionados'
    
    def activate_users(self, request, queryset):
        """Activar usuarios seleccionados"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} usuario(s) activado(s).')
    activate_users.short_description = '▶ Activar usuarios seleccionados'
    
    def deactivate_users(self, request, queryset):
        """Desactivar usuarios seleccionados"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} usuario(s) desactivado(s).')
    deactivate_users.short_description = '■ Desactivar usuarios seleccionados'


# ========================================
# CUSTOMER ADMIN
# ========================================
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'get_customer_name',
        'get_email',
        'get_phone',
        'address_short',
        'total_orders_badge',
        'total_spent_badge',
        'created_at'
    )
    list_filter = ('created_at', 'updated_at')
    search_fields = (
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'user__phone',
        'address'
    )
    readonly_fields = (
        'user',
        'total_orders',
        'total_spent',
        'created_at',
        'updated_at',
        'get_location_map'
    )
    ordering = ('-created_at',)
    
    fieldsets = (
        (_('Información del Cliente'), {
            'fields': ('user',)
        }),
        (_('Dirección de Entrega'), {
            'fields': (
                'address',
                'address_reference',
                'latitude',
                'longitude',
                'get_location_map'
            )
        }),
        (_('Estadísticas'), {
            'fields': ('total_orders', 'total_spent'),
            'classes': ('collapse',)
        }),
        (_('Fechas'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_customer_name(self, obj):
        """Nombre completo del cliente"""
        return obj.user.get_full_name() or obj.user.username
    get_customer_name.short_description = 'Cliente'
    get_customer_name.admin_order_field = 'user__first_name'
    
    def get_email(self, obj):
        """Email del cliente"""
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
    
    def get_phone(self, obj):
        """Teléfono del cliente"""
        return obj.user.phone or '-'
    get_phone.short_description = 'Teléfono'
    
    def address_short(self, obj):
        """Dirección resumida"""
        if obj.address:
            return obj.address[:50] + '...' if len(obj.address) > 50 else obj.address
        return '-'
    address_short.short_description = 'Dirección'
    
    def total_orders_badge(self, obj):
        """Badge para total de pedidos"""
        color = '#28a745' if obj.total_orders > 0 else '#6c757d'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{} pedidos</span>',
            color,
            obj.total_orders
        )
    total_orders_badge.short_description = 'Pedidos'
    total_orders_badge.admin_order_field = 'total_orders'
    
    def total_spent_badge(self, obj):
        """Badge para total gastado"""
        color = '#007bff' if obj.total_spent > 0 else '#6c757d'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">${}</span>',
            color,
            f'{obj.total_spent:.2f}'
        )
    total_spent_badge.short_description = 'Total Gastado'
    total_spent_badge.admin_order_field = 'total_spent'
    
    def get_location_map(self, obj):
        """Mostrar mapa de Google Maps con la ubicación"""
        if obj.latitude and obj.longitude:
            map_url = f"https://www.google.com/maps?q={obj.latitude},{obj.longitude}"
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #007bff; color: white; '
                'padding: 5px 15px; border-radius: 3px; text-decoration: none; display: inline-block;">'
                '📍 Ver en Google Maps</a><br><br>'
                '<iframe width="100%" height="300" frameborder="0" style="border:0" '
                'src="https://www.google.com/maps?q={},{}&output=embed"></iframe>',
                map_url,
                obj.latitude,
                obj.longitude
            )
        return '-'
    get_location_map.short_description = 'Ubicación en Mapa'


# ========================================
# DRIVER ADMIN
# ========================================
@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = (
        'get_driver_name',
        'get_email',
        'vehicle_info',
        'license_number',
        'status_badge',
        'availability_badge',
        'rating_badge',
        'total_deliveries_badge',
        'total_earnings_badge',
        'created_at'
    )
    list_filter = (
        'status',
        'vehicle_type',
        'is_available',
        'is_online',
        'created_at',
        'approved_at'
    )
    search_fields = (
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'user__phone',
        'vehicle_plate',
        'license_number'
    )
    readonly_fields = (
        'user',
        'total_deliveries',
        'total_earnings',
        'rating',
        'created_at',
        'updated_at',
        'approved_at',
        'approved_by',
        'get_documents_preview',
        'get_location_map'
    )
    ordering = ('-created_at',)
    
    fieldsets = (
        (_('Información del Conductor'), {
            'fields': ('user',)
        }),
        (_('Información del Vehículo'), {
            'fields': (
                'vehicle_type',
                'vehicle_plate',
                'vehicle_brand',
                'vehicle_model',
                'vehicle_color'
            )
        }),
        (_('Licencia y Documentos'), {
            'fields': (
                'license_number',
                'license_photo',
                'vehicle_photo',
                'id_photo',
                'get_documents_preview'
            )
        }),
        (_('Estado y Aprobación'), {
            'fields': (
                'status',
                'notes',
                'approved_at',
                'approved_by'
            )
        }),
        (_('Disponibilidad'), {
            'fields': (
                'is_available',
                'is_online'
            )
        }),
        (_('Ubicación Actual'), {
            'fields': (
                'current_latitude',
                'current_longitude',
                'get_location_map'
            )
        }),
        (_('Estadísticas'), {
            'fields': (
                'rating',
                'total_deliveries',
                'total_earnings'
            ),
            'classes': ('collapse',)
        }),
        (_('Fechas'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'approve_drivers',
        'reject_drivers',
        'suspend_drivers',
        'activate_drivers',
        'mark_online',
        'mark_offline'
    ]
    
    def get_driver_name(self, obj):
        """Nombre completo del conductor"""
        return obj.user.get_full_name() or obj.user.username
    get_driver_name.short_description = 'Conductor'
    get_driver_name.admin_order_field = 'user__first_name'
    
    def get_email(self, obj):
        """Email del conductor"""
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
    
    def vehicle_info(self, obj):
        """Información del vehículo resumida"""
        vehicle = f"{obj.get_vehicle_type_display()}"
        if obj.vehicle_brand or obj.vehicle_model:
            vehicle += f" - {obj.vehicle_brand or ''} {obj.vehicle_model or ''}".strip()
        return vehicle
    vehicle_info.short_description = 'Vehículo'
    
    def status_badge(self, obj):
        """Badge de color para el estado"""
        colors = {
            'PENDING': '#ffc107',      # Amarillo/Naranja
            'APPROVED': '#28a745',     # Verde
            'REJECTED': '#dc3545',     # Rojo
            'SUSPENDED': '#6c757d',    # Gris
        }
        icons = {
            'PENDING': '⏳',
            'APPROVED': '✓',
            'REJECTED': '✗',
            'SUSPENDED': '⊘',
        }
        color = colors.get(obj.status, '#6c757d')
        icon = icons.get(obj.status, '?')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold; font-size: 11px;">{} {}</span>',
            color,
            icon,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    status_badge.admin_order_field = 'status'
    
    def availability_badge(self, obj):
        """Badge para disponibilidad"""
        if obj.is_online:
            color = '#28a745'
            icon = '🟢'
            text = 'En Línea'
        elif obj.is_available:
            color = '#ffc107'
            icon = '🟡'
            text = 'Disponible'
        else:
            color = '#dc3545'
            icon = '🔴'
            text = 'No Disponible'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold; font-size: 11px;">{} {}</span>',
            color,
            icon,
            text
        )
    availability_badge.short_description = 'Disponibilidad'
    
    def rating_badge(self, obj):
        """Badge para rating con estrellas"""
        stars = '⭐' * int(obj.rating)
        color = '#ffc107' if obj.rating >= 4.0 else '#dc3545' if obj.rating < 3.0 else '#6c757d'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{} {}</span>',
            color,
            stars,
            f'{obj.rating:.1f}'
        )
    rating_badge.short_description = 'Rating'
    rating_badge.admin_order_field = 'rating'
    
    def total_deliveries_badge(self, obj):
        """Badge para total de entregas"""
        color = '#007bff' if obj.total_deliveries > 0 else '#6c757d'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.total_deliveries
        )
    total_deliveries_badge.short_description = 'Entregas'
    total_deliveries_badge.admin_order_field = 'total_deliveries'
    
    def total_earnings_badge(self, obj):
        """Badge para ganancias totales"""
        color = '#28a745' if obj.total_earnings > 0 else '#6c757d'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">${}</span>',
            color,
            f'{obj.total_earnings:.2f}'
        )
    total_earnings_badge.short_description = 'Ganancias'
    total_earnings_badge.admin_order_field = 'total_earnings'
    
    def get_documents_preview(self, obj):
        """Vista previa de documentos"""
        html = '<div style="display: flex; gap: 20px; flex-wrap: wrap;">'
        
        if obj.license_photo:
            html += f'''
                <div>
                    <strong>Licencia:</strong><br>
                    <a href="{obj.license_photo.url}" target="_blank">
                        <img src="{obj.license_photo.url}" style="max-width: 200px; border: 1px solid #ddd; border-radius: 5px;">
                    </a>
                </div>
            '''
        
        if obj.vehicle_photo:
            html += f'''
                <div>
                    <strong>Vehículo:</strong><br>
                    <a href="{obj.vehicle_photo.url}" target="_blank">
                        <img src="{obj.vehicle_photo.url}" style="max-width: 200px; border: 1px solid #ddd; border-radius: 5px;">
                    </a>
                </div>
            '''
        
        if obj.id_photo:
            html += f'''
                <div>
                    <strong>Cédula/ID:</strong><br>
                    <a href="{obj.id_photo.url}" target="_blank">
                        <img src="{obj.id_photo.url}" style="max-width: 200px; border: 1px solid #ddd; border-radius: 5px;">
                    </a>
                </div>
            '''
        
        html += '</div>'
        return format_html(html) if any([obj.license_photo, obj.vehicle_photo, obj.id_photo]) else '-'
    get_documents_preview.short_description = 'Vista Previa de Documentos'
    
    def get_location_map(self, obj):
        """Mostrar ubicación actual en el mapa"""
        if obj.current_latitude and obj.current_longitude:
            map_url = f"https://www.google.com/maps?q={obj.current_latitude},{obj.current_longitude}"
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #007bff; color: white; '
                'padding: 5px 15px; border-radius: 3px; text-decoration: none; display: inline-block;">'
                '📍 Ver Ubicación Actual</a><br><br>'
                '<iframe width="100%" height="300" frameborder="0" style="border:0" '
                'src="https://www.google.com/maps?q={},{}&output=embed"></iframe>',
                map_url,
                obj.current_latitude,
                obj.current_longitude
            )
        return '-'
    get_location_map.short_description = 'Ubicación Actual en Mapa'
    
    # ===== ACCIONES MASIVAS =====
    
    def approve_drivers(self, request, queryset):
        """Aprobar conductores seleccionados"""
        count = 0
        for driver in queryset.filter(status='PENDING'):
            driver.approve(approved_by=request.user)
            count += 1
        self.message_user(request, f'{count} conductor(es) aprobado(s) exitosamente.')
    approve_drivers.short_description = '✓ Aprobar conductores seleccionados'
    
    def reject_drivers(self, request, queryset):
        """Rechazar conductores seleccionados"""
        count = 0
        for driver in queryset.filter(status='PENDING'):
            driver.reject()
            count += 1
        self.message_user(request, f'{count} conductor(es) rechazado(s).')
    reject_drivers.short_description = '✗ Rechazar conductores seleccionados'
    
    def suspend_drivers(self, request, queryset):
        """Suspender conductores seleccionados"""
        count = 0
        for driver in queryset.exclude(status='SUSPENDED'):
            driver.suspend()
            count += 1
        self.message_user(request, f'{count} conductor(es) suspendido(s).')
    suspend_drivers.short_description = '⊘ Suspender conductores seleccionados'
    
    def activate_drivers(self, request, queryset):
        """Activar conductores suspendidos"""
        updated = queryset.filter(status='SUSPENDED').update(
            status='APPROVED',
            is_available=True
        )
        self.message_user(request, f'{updated} conductor(es) reactivado(s).')
    activate_drivers.short_description = '▶ Reactivar conductores suspendidos'
    
    def mark_online(self, request, queryset):
        """Marcar como en línea"""
        updated = queryset.filter(status='APPROVED').update(
            is_online=True,
            is_available=True
        )
        self.message_user(request, f'{updated} conductor(es) marcado(s) como en línea.')
    mark_online.short_description = '🟢 Marcar como En Línea'
    
    def mark_offline(self, request, queryset):
        """Marcar como fuera de línea"""
        updated = queryset.update(is_online=False)
        self.message_user(request, f'{updated} conductor(es) marcado(s) como fuera de línea.')
    mark_offline.short_description = '🔴 Marcar como Fuera de Línea'


# ========================================
# PERSONALIZACIÓN DEL SITIO
# ========================================
admin.site.site_header = "QuickGo - Panel de Administración"
admin.site.site_title = "QuickGo Admin"
admin.site.index_title = "Bienvenido al Panel de Control de QuickGo"