from django.contrib import admin
from .models import Restaurant, RestaurantSchedule, RestaurantReview, RestaurantGallery

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'cuisine_type', 'status', 'rating', 'is_open', 'is_accepting_orders']
    list_filter = ['status', 'cuisine_type', 'is_open', 'is_accepting_orders', 'is_featured']
    search_fields = ['name', 'description', 'address', 'ruc']
    list_editable = ['is_open', 'is_accepting_orders']
    ordering = ['-is_featured', '-rating', 'name']
    readonly_fields = ['slug', 'created_at', 'updated_at', 'total_orders', 'total_revenue']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'name', 'slug', 'description', 'cuisine_type')
        }),
        ('Contacto', {
            'fields': ('phone', 'email', 'address', 'address_reference', 'latitude', 'longitude')
        }),
        ('Documentos', {
            'fields': ('ruc', 'business_license', 'health_permit')
        }),
        ('Estado', {
            'fields': ('status', 'is_open', 'is_accepting_orders', 'approved_at', 'approved_by', 'notes')
        }),
        ('Configuración de Entregas', {
            'fields': ('delivery_time_min', 'delivery_time_max', 'delivery_fee', 'min_order_amount', 'free_delivery_above', 'delivery_radius_km')
        }),
        ('Estadísticas', {
            'fields': ('rating', 'total_reviews', 'total_orders', 'total_revenue')
        }),
        ('Destacados', {
            'fields': ('is_featured', 'is_new', 'has_promotion', 'promotion_text')
        }),
    )

@admin.register(RestaurantSchedule)
class RestaurantScheduleAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'day_of_week', 'opening_time', 'closing_time', 'is_closed']
    list_filter = ['day_of_week', 'is_closed']
    search_fields = ['restaurant__name']

@admin.register(RestaurantReview)
class RestaurantReviewAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'customer', 'rating', 'is_verified', 'is_visible', 'created_at']
    list_filter = ['rating', 'is_verified', 'is_visible']
    search_fields = ['restaurant__name', 'customer__email', 'comment']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(RestaurantGallery)
class RestaurantGalleryAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'caption', 'is_featured', 'order', 'created_at']
    list_filter = ['is_featured']
    search_fields = ['restaurant__name', 'caption']
