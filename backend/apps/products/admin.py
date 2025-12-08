# apps/products/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Category,
    ProductTag,
    Product,
    ProductImage,
    ProductExtra,
    ProductOptionGroup,
    ProductOption,
    ProductReview
)


# ============================================================================
# INLINES
# ============================================================================

class ProductImageInline(admin.TabularInline):
    """Inline para imágenes adicionales del producto"""
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 100px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Vista Previa'


class ProductExtraInline(admin.TabularInline):
    """Inline para extras del producto"""
    model = ProductExtra
    extra = 1
    fields = ['name', 'description', 'price', 'is_available', 'max_quantity', 'order']


class ProductOptionInline(admin.TabularInline):
    """Inline para opciones dentro de un grupo"""
    model = ProductOption
    extra = 1
    fields = ['name', 'price_modifier', 'is_available', 'is_default', 'order']


class ProductOptionGroupInline(admin.StackedInline):
    """Inline para grupos de opciones del producto"""
    model = ProductOptionGroup
    extra = 0
    fields = [
        'name',
        'is_required',
        ('min_selections', 'max_selections'),
        'order'
    ]
    show_change_link = True


# ============================================================================
# ADMIN MODELS
# ============================================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Administración de Categorías"""
    
    list_display = [
        'name',
        'restaurant_link',
        'products_count',
        'image_preview',
        'is_active',
        'order',
        'created_at'
    ]
    
    list_filter = [
        'is_active',
        'restaurant',
        'created_at'
    ]
    
    search_fields = [
        'name',
        'description',
        'restaurant__name'
    ]
    
    readonly_fields = [
        'slug',
        'image_preview',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'restaurant',
                'name',
                'slug',
                'description'
            )
        }),
        ('Imagen', {
            'fields': (
                'image',
                'image_preview'
            )
        }),
        ('Configuración', {
            'fields': (
                'is_active',
                'order'
            )
        }),
        ('Información del Sistema', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def restaurant_link(self, obj):
        url = reverse('admin:restaurants_restaurant_change', args=[obj.restaurant.id])
        return format_html('<a href="{}">{}</a>', url, obj.restaurant.name)
    restaurant_link.short_description = 'Restaurante'
    
    def products_count(self, obj):
        count = obj.products.filter(is_active=True).count()
        return format_html(
            '<span style="color: {};">{} productos</span>',
            'green' if count > 0 else 'red',
            count
        )
    products_count.short_description = 'Productos'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 200px; border-radius: 8px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Vista Previa'


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    """Administración de Etiquetas de Productos"""
    
    list_display = [
        'name_with_icon',
        'tag_type',
        'color_preview',
        'products_count',
        'is_active'
    ]
    
    list_filter = [
        'tag_type',
        'is_active'
    ]
    
    search_fields = [
        'name',
        'slug'
    ]
    
    readonly_fields = ['slug']
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'name',
                'slug',
                'tag_type'
            )
        }),
        ('Apariencia', {
            'fields': (
                'icon',
                'color'
            )
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )
    
    def name_with_icon(self, obj):
        return f"{obj.icon} {obj.name}" if obj.icon else obj.name
    name_with_icon.short_description = 'Etiqueta'
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 50px; height: 20px; background-color: {}; border-radius: 4px; border: 1px solid #ccc;"></div>',
            obj.color
        )
    color_preview.short_description = 'Color'
    
    def products_count(self, obj):
        count = obj.products.count()
        return f"{count} productos"
    products_count.short_description = 'Productos'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Administración de Productos"""
    
    list_display = [
        'image_thumbnail',
        'name',
        'restaurant_link',
        'category',
        'price_display',
        'discount_badge',
        'stock_status',
        'rating_display',
        'orders_count',
        'status_badges',
        'created_at'
    ]
    
    list_filter = [
        'is_active',
        'is_available',
        'is_featured',
        'is_new',
        'is_popular',
        'track_inventory',
        'restaurant',
        'category',
        'tags',
        'created_at'
    ]
    
    search_fields = [
        'name',
        'description',
        'restaurant__name',
        'category__name'
    ]
    
    readonly_fields = [
        'slug',
        'discount_percentage',
        'image_preview',
        'views_count',
        'orders_count',
        'rating',
        'reviews_count',
        'created_at',
        'updated_at'
    ]
    
    filter_horizontal = ['tags']
    
    inlines = [
        ProductImageInline,
        ProductExtraInline,
        ProductOptionGroupInline
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'restaurant',
                'category',
                'name',
                'slug',
                'description',
                'short_description'
            )
        }),
        ('Imagen Principal', {
            'fields': (
                'image',
                'image_preview'
            )
        }),
        ('Precios y Descuentos', {
            'fields': (
                ('price', 'compare_price'),
                'discount_percentage'
            )
        }),
        ('Etiquetas', {
            'fields': ('tags',)
        }),
        ('Disponibilidad e Inventario', {
            'fields': (
                ('is_active', 'is_available'),
                'track_inventory',
                'stock_quantity',
                'preparation_time'
            )
        }),
        ('Información Nutricional', {
            'fields': (
                'calories',
                'serving_size'
            ),
            'classes': ('collapse',)
        }),
        ('Destacados y Promociones', {
            'fields': (
                'is_featured',
                'is_new',
                'is_popular'
            )
        }),
        ('Estadísticas', {
            'fields': (
                'views_count',
                'orders_count',
                ('rating', 'reviews_count')
            ),
            'classes': ('collapse',)
        }),
        ('Orden de Visualización', {
            'fields': ('order',)
        }),
        ('SEO', {
            'fields': (
                'meta_title',
                'meta_description'
            ),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'make_active',
        'make_inactive',
        'make_available',
        'make_unavailable',
        'mark_as_featured',
        'unmark_as_featured'
    ]
    
    # ========================================================================
    # DISPLAY METHODS
    # ========================================================================
    
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;" />',
                obj.image.url
            )
        return '-'
    image_thumbnail.short_description = 'Imagen'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 300px; max-width: 400px; border-radius: 8px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Vista Previa'
    
    def restaurant_link(self, obj):
        url = reverse('admin:restaurants_restaurant_change', args=[obj.restaurant.id])
        return format_html('<a href="{}">{}</a>', url, obj.restaurant.name)
    restaurant_link.short_description = 'Restaurante'
    
    def price_display(self, obj):
        if obj.has_discount:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">${}</span> '
                '<strong style="color: #16a34a;">${}</strong>',
                obj.compare_price,
                obj.price
            )
        return format_html('<strong>${}</strong>', obj.price)
    price_display.short_description = 'Precio'
    
    def discount_badge(self, obj):
        if obj.has_discount:
            return format_html(
                '<span style="background-color: #dc2626; color: white; padding: 2px 8px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">-{}%</span>',
                int(obj.discount_percentage)
            )
        return '-'
    discount_badge.short_description = 'Descuento'
    
    def stock_status(self, obj):
        if not obj.track_inventory:
            return format_html(
                '<span style="color: #3b82f6;">∞ Sin control</span>'
            )
        
        if obj.is_in_stock:
            color = '#16a34a' if obj.stock_quantity > 10 else '#f59e0b'
            return format_html(
                '<span style="color: {};">{} unidades</span>',
                color,
                obj.stock_quantity
            )
        
        return format_html(
            '<span style="color: #dc2626; font-weight: bold;">Agotado</span>'
        )
    stock_status.short_description = 'Stock'
    
    def rating_display(self, obj):
        stars = '⭐' * int(obj.rating)
        return format_html(
            '{} <span style="color: #666;">({:.1f})</span>',
            stars,
            obj.rating
        )
    rating_display.short_description = 'Calificación'
    
    def status_badges(self, obj):
        badges = []
        
        if not obj.is_active:
            badges.append(
                '<span style="background-color: #dc2626; color: white; padding: 2px 6px; '
                'border-radius: 4px; font-size: 10px;">INACTIVO</span>'
            )
        
        if not obj.is_available:
            badges.append(
                '<span style="background-color: #f59e0b; color: white; padding: 2px 6px; '
                'border-radius: 4px; font-size: 10px;">NO DISPONIBLE</span>'
            )
        
        if obj.is_featured:
            badges.append(
                '<span style="background-color: #8b5cf6; color: white; padding: 2px 6px; '
                'border-radius: 4px; font-size: 10px;">DESTACADO</span>'
            )
        
        if obj.is_new:
            badges.append(
                '<span style="background-color: #3b82f6; color: white; padding: 2px 6px; '
                'border-radius: 4px; font-size: 10px;">NUEVO</span>'
            )
        
        if obj.is_popular:
            badges.append(
                '<span style="background-color: #f59e0b; color: white; padding: 2px 6px; '
                'border-radius: 4px; font-size: 10px;">POPULAR</span>'
            )
        
        return format_html(' '.join(badges)) if badges else '-'
    status_badges.short_description = 'Estado'
    
    # ========================================================================
    # ACTIONS
    # ========================================================================
    
    @admin.action(description='✅ Activar productos seleccionados')
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} productos activados correctamente.')
    
    @admin.action(description='❌ Desactivar productos seleccionados')
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} productos desactivados correctamente.')
    
    @admin.action(description='🟢 Marcar como disponibles')
    def make_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} productos marcados como disponibles.')
    
    @admin.action(description='🔴 Marcar como no disponibles')
    def make_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} productos marcados como no disponibles.')
    
    @admin.action(description='⭐ Marcar como destacados')
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} productos marcados como destacados.')
    
    @admin.action(description='Quitar de destacados')
    def unmark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} productos quitados de destacados.')


@admin.register(ProductOptionGroup)
class ProductOptionGroupAdmin(admin.ModelAdmin):
    """Administración de Grupos de Opciones"""
    
    list_display = [
        'name',
        'product_link',
        'is_required',
        'selections_range',
        'options_count',
        'order'
    ]
    
    list_filter = [
        'is_required',
        'product__restaurant'
    ]
    
    search_fields = [
        'name',
        'product__name'
    ]
    
    inlines = [ProductOptionInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'product',
                'name'
            )
        }),
        ('Configuración de Selección', {
            'fields': (
                'is_required',
                ('min_selections', 'max_selections')
            )
        }),
        ('Orden', {
            'fields': ('order',)
        }),
    )
    
    def product_link(self, obj):
        url = reverse('admin:products_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Producto'
    
    def selections_range(self, obj):
        if obj.min_selections == obj.max_selections:
            return f"Exactamente {obj.min_selections}"
        return f"{obj.min_selections} - {obj.max_selections}"
    selections_range.short_description = 'Selecciones'
    
    def options_count(self, obj):
        count = obj.options.count()
        return format_html(
            '<span style="color: {};">{} opciones</span>',
            'green' if count > 0 else 'red',
            count
        )
    options_count.short_description = 'Opciones'


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """Administración de Reseñas de Productos"""
    
    list_display = [
        'customer_name',
        'product_link',
        'rating_stars',
        'comment_preview',
        'is_verified',
        'is_visible',
        'helpful_count',
        'created_at'
    ]
    
    list_filter = [
        'rating',
        'is_verified',
        'is_visible',
        'created_at',
        'product__restaurant'
    ]
    
    search_fields = [
        'customer__first_name',
        'customer__last_name',
        'customer__username',
        'product__name',
        'comment'
    ]
    
    readonly_fields = [
        'customer',
        'product',
        'order_item',
        'created_at',
        'updated_at',
        'images_preview'
    ]
    
    fieldsets = (
        ('Información de la Reseña', {
            'fields': (
                'customer',
                'product',
                'order_item',
                'rating',
                'comment'
            )
        }),
        ('Imágenes', {
            'fields': (
                ('image1', 'image2', 'image3'),
                'images_preview'
            )
        }),
        ('Estado y Estadísticas', {
            'fields': (
                'is_verified',
                'is_visible',
                'helpful_count'
            )
        }),
        ('Información del Sistema', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_reviews', 'hide_reviews']
    
    def customer_name(self, obj):
        return obj.customer.get_full_name() or obj.customer.username
    customer_name.short_description = 'Cliente'
    
    def product_link(self, obj):
        url = reverse('admin:products_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Producto'
    
    def rating_stars(self, obj):
        stars = '⭐' * obj.rating
        return format_html('<span style="font-size: 16px;">{}</span>', stars)
    rating_stars.short_description = 'Calificación'
    
    def comment_preview(self, obj):
        if obj.comment:
            preview = obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
            return preview
        return '-'
    comment_preview.short_description = 'Comentario'
    
    def images_preview(self, obj):
        images = []
        for img_field in ['image1', 'image2', 'image3']:
            img = getattr(obj, img_field)
            if img:
                images.append(
                    f'<img src="{img.url}" style="max-height: 100px; max-width: 150px; '
                    f'margin-right: 10px; border-radius: 8px;" />'
                )
        
        return format_html(''.join(images)) if images else '-'
    images_preview.short_description = 'Imágenes de la Reseña'
    
    @admin.action(description='✅ Aprobar y hacer visible')
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_visible=True, is_verified=True)
        self.message_user(request, f'{updated} reseñas aprobadas correctamente.')
    
    @admin.action(description='❌ Ocultar reseñas')
    def hide_reviews(self, request, queryset):
        updated = queryset.update(is_visible=False)
        self.message_user(request, f'{updated} reseñas ocultadas correctamente.')


# ============================================================================
# REGISTRO DE MODELOS SIMPLES
# ============================================================================

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Administración simple de imágenes de productos"""
    
    list_display = ['product', 'image_preview', 'alt_text', 'order', 'created_at']
    list_filter = ['product__restaurant', 'created_at']
    search_fields = ['product__name', 'alt_text']
    readonly_fields = ['image_preview', 'created_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px; border-radius: 8px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Vista Previa'


@admin.register(ProductExtra)
class ProductExtraAdmin(admin.ModelAdmin):
    """Administración de Extras de Productos"""
    
    list_display = ['name', 'product', 'price', 'is_available', 'max_quantity', 'order']
    list_filter = ['is_available', 'product__restaurant']
    search_fields = ['name', 'product__name']