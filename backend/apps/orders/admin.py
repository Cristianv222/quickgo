from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory, OrderRating


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product_name', 'unit_price', 'quantity', 'subtotal', 'customizations']
    readonly_fields = ['subtotal']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    fields = ['status', 'notes', 'changed_by', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'restaurant', 'status', 'total', 'payment_method', 'is_paid', 'created_at']
    list_filter = ['status', 'payment_method', 'is_paid', 'created_at']
    search_fields = ['order_number', 'customer__email', 'customer__first_name', 'customer__last_name', 'restaurant__name']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'confirmed_at', 'ready_at', 'picked_up_at', 'delivered_at', 'cancelled_at']
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('order_number', 'customer', 'restaurant', 'driver', 'status')
        }),
        ('Dirección de Entrega', {
            'fields': ('delivery_address', 'delivery_reference', 'delivery_latitude', 'delivery_longitude')
        }),
        ('Costos', {
            'fields': ('subtotal', 'delivery_fee', 'service_fee', 'discount', 'total')
        }),
        ('Pago', {
            'fields': ('payment_method', 'is_paid', 'payment_date')
        }),
        ('Notas', {
            'fields': ('special_instructions', 'cancellation_reason')
        }),
        ('Tiempos', {
            'fields': ('estimated_delivery_time', 'confirmed_at', 'ready_at', 'picked_up_at', 'delivered_at', 'cancelled_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_preparing', 'mark_as_ready', 'mark_as_delivered']
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='CONFIRMED')
        self.message_user(request, f"{queryset.count()} pedidos marcados como confirmados")
    mark_as_confirmed.short_description = "Marcar como Confirmado"
    
    def mark_as_preparing(self, request, queryset):
        queryset.update(status='PREPARING')
        self.message_user(request, f"{queryset.count()} pedidos marcados como en preparación")
    mark_as_preparing.short_description = "Marcar como Preparando"
    
    def mark_as_ready(self, request, queryset):
        queryset.update(status='READY')
        self.message_user(request, f"{queryset.count()} pedidos marcados como listos")
    mark_as_ready.short_description = "Marcar como Listo"
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='DELIVERED')
        self.message_user(request, f"{queryset.count()} pedidos marcados como entregados")
    mark_as_delivered.short_description = "Marcar como Entregado"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'unit_price', 'subtotal']
    list_filter = ['order__status', 'created_at']
    search_fields = ['product_name', 'order__order_number']
    readonly_fields = ['subtotal', 'created_at']


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'changed_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number', 'notes']
    readonly_fields = ['created_at']


@admin.register(OrderRating)
class OrderRatingAdmin(admin.ModelAdmin):
    list_display = ['order', 'overall_rating', 'driver_rating', 'would_order_again', 'created_at']
    list_filter = ['overall_rating', 'driver_rating', 'would_order_again', 'created_at']
    search_fields = ['order__order_number', 'comment', 'driver_comment']
    readonly_fields = ['created_at']
