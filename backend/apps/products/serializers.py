# apps/products/serializers.py
from rest_framework import serializers
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
from apps.restaurants.models import Restaurant


# ============================================================================
# SERIALIZERS BÁSICOS
# ============================================================================

class ProductTagSerializer(serializers.ModelSerializer):
    """Serializer para etiquetas de productos"""
    
    class Meta:
        model = ProductTag
        fields = [
            'id',
            'name',
            'slug',
            'tag_type',
            'icon',
            'color'
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer para imágenes adicionales del producto"""
    
    class Meta:
        model = ProductImage
        fields = [
            'id',
            'image',
            'alt_text',
            'order'
        ]


class ProductExtraSerializer(serializers.ModelSerializer):
    """Serializer para extras del producto"""
    
    class Meta:
        model = ProductExtra
        fields = [
            'id',
            'name',
            'description',
            'price',
            'is_available',
            'max_quantity'
        ]


class ProductOptionSerializer(serializers.ModelSerializer):
    """Serializer para opciones individuales"""
    
    price_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductOption
        fields = [
            'id',
            'name',
            'price_modifier',
            'price_display',
            'is_available',
            'is_default'
        ]
    
    def get_price_display(self, obj):
        """Muestra el modificador de precio formateado"""
        if obj.price_modifier > 0:
            return f"+${obj.price_modifier}"
        elif obj.price_modifier < 0:
            return f"-${abs(obj.price_modifier)}"
        return "Gratis"


class ProductOptionGroupSerializer(serializers.ModelSerializer):
    """Serializer para grupos de opciones"""
    
    options = ProductOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductOptionGroup
        fields = [
            'id',
            'name',
            'is_required',
            'min_selections',
            'max_selections',
            'order',
            'options'
        ]


# ============================================================================
# SERIALIZER DE CATEGORÍA
# ============================================================================

class CategoryListSerializer(serializers.ModelSerializer):
    """Serializer simple para listar categorías"""
    
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'image',
            'products_count',
            'order'
        ]
    
    def get_products_count(self, obj):
        return obj.products.filter(is_active=True, is_available=True).count()


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado de categoría con productos"""
    
    products_count = serializers.SerializerMethodField()
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id',
            'restaurant',
            'restaurant_name',
            'name',
            'slug',
            'description',
            'image',
            'is_active',
            'order',
            'products_count',
            'created_at',
            'updated_at'
        ]
    
    def get_products_count(self, obj):
        return obj.products.filter(is_active=True, is_available=True).count()


# ============================================================================
# SERIALIZER DE PRODUCTO
# ============================================================================

class ProductListSerializer(serializers.ModelSerializer):
    """Serializer simple para listar productos"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    tags = ProductTagSerializer(many=True, read_only=True)
    has_discount = serializers.BooleanField(read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'restaurant',
            'restaurant_name',
            'category',
            'category_name',
            'name',
            'slug',
            'short_description',
            'image',
            'price',
            'compare_price',
            'discount_percentage',
            'has_discount',
            'final_price',
            'tags',
            'is_available',
            'is_featured',
            'is_new',
            'is_popular',
            'rating',
            'reviews_count',
            'preparation_time'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer completo del producto con todas las relaciones"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    restaurant_logo = serializers.ImageField(source='restaurant.logo', read_only=True)
    tags = ProductTagSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    extras = ProductExtraSerializer(many=True, read_only=True)
    option_groups = ProductOptionGroupSerializer(many=True, read_only=True)
    has_discount = serializers.BooleanField(read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'restaurant',
            'restaurant_name',
            'restaurant_logo',
            'category',
            'category_name',
            'name',
            'slug',
            'description',
            'short_description',
            'image',
            'images',
            'price',
            'compare_price',
            'discount_percentage',
            'has_discount',
            'final_price',
            'tags',
            'extras',
            'option_groups',
            'is_available',
            'is_active',
            'is_in_stock',
            'stock_quantity',
            'track_inventory',
            'preparation_time',
            'calories',
            'serving_size',
            'is_featured',
            'is_new',
            'is_popular',
            'rating',
            'reviews_count',
            'orders_count',
            'created_at',
            'updated_at'
        ]


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar productos"""
    
    class Meta:
        model = Product
        fields = [
            'restaurant',
            'category',
            'name',
            'description',
            'short_description',
            'image',
            'price',
            'compare_price',
            'is_available',
            'is_active',
            'stock_quantity',
            'track_inventory',
            'preparation_time',
            'calories',
            'serving_size',
            'is_featured',
            'is_new',
            'is_popular',
            'order'
        ]
    
    def validate(self, data):
        """Validaciones personalizadas"""
        
        # Validar que el precio de comparación sea mayor al precio actual
        if data.get('compare_price') and data.get('price'):
            if data['compare_price'] <= data['price']:
                raise serializers.ValidationError({
                    'compare_price': 'El precio de comparación debe ser mayor al precio actual.'
                })
        
        # Validar stock si se controla inventario
        if data.get('track_inventory'):
            if data.get('stock_quantity') is None:
                raise serializers.ValidationError({
                    'stock_quantity': 'Debe especificar la cantidad en stock si controla inventario.'
                })
        
        return data


# ============================================================================
# SERIALIZER DE RESEÑAS
# ============================================================================

class ProductReviewSerializer(serializers.ModelSerializer):
    """Serializer para reseñas de productos"""
    
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    customer_avatar = serializers.ImageField(source='customer.avatar', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = ProductReview
        fields = [
            'id',
            'product',
            'product_name',
            'customer',
            'customer_name',
            'customer_avatar',
            'order_item',
            'rating',
            'comment',
            'image1',
            'image2',
            'image3',
            'is_verified',
            'is_visible',
            'helpful_count',
            'created_at'
        ]
        read_only_fields = ['customer', 'is_verified', 'helpful_count']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("La calificación debe estar entre 1 y 5.")
        return value


class ProductReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear reseñas"""
    
    class Meta:
        model = ProductReview
        fields = [
            'product',
            'order_item',
            'rating',
            'comment',
            'image1',
            'image2',
            'image3'
        ]
    
    def validate(self, data):
        """Validar que el usuario haya comprado el producto"""
        request = self.context.get('request')
        product = data.get('product')
        
        # Verificar que no haya reseñado este producto antes
        if ProductReview.objects.filter(
            product=product,
            customer=request.user
        ).exists():
            raise serializers.ValidationError(
                "Ya has reseñado este producto anteriormente."
            )
        
        return data
    
    def create(self, validated_data):
        """Crear reseña y marcar como verificada si tiene order_item"""
        request = self.context.get('request')
        validated_data['customer'] = request.user
        
        # Si tiene order_item, es verificada
        if validated_data.get('order_item'):
            validated_data['is_verified'] = True
        
        return super().create(validated_data)


# ============================================================================
# SERIALIZERS ADICIONALES
# ============================================================================

class ProductSearchSerializer(serializers.ModelSerializer):
    """Serializer optimizado para búsqueda de productos"""
    
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'image',
            'price',
            'restaurant_name',
            'category_name',
            'rating',
            'is_available'
        ]


class ProductMinimalSerializer(serializers.ModelSerializer):
    """Serializer mínimo para referencias rápidas"""
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'image',
            'price'
        ]