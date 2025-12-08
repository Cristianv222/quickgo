# apps/products/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django.db.models import Q, Count, Avg
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Category,
    Product,
    ProductReview,
    ProductTag
)
from .serializers import (
    CategoryListSerializer,
    CategoryDetailSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    ProductReviewSerializer,
    ProductReviewCreateSerializer,
    ProductSearchSerializer,
    ProductTagSerializer
)
from .filters import ProductFilter
from .permissions import IsRestaurantOwnerOrReadOnly


# ============================================================================
# VIEWSET DE CATEGORÍAS
# ============================================================================

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar categorías de productos
    
    list: Listar todas las categorías activas
    retrieve: Detalle de una categoría
    create: Crear nueva categoría (solo restaurantes)
    update: Actualizar categoría (solo propietario)
    destroy: Eliminar categoría (solo propietario)
    """
    
    queryset = Category.objects.filter(is_active=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['restaurant', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name', 'created_at']
    ordering = ['order', 'name']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoryDetailSerializer
        return CategoryListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por restaurante si se proporciona
        restaurant_id = self.request.query_params.get('restaurant', None)
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        
        return queryset.select_related('restaurant').prefetch_related('products')
    
    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Obtener todos los productos de una categoría"""
        category = self.get_object()
        products = category.products.filter(
            is_active=True,
            is_available=True
        ).select_related('restaurant', 'category').prefetch_related('tags')
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


# ============================================================================
# VIEWSET DE PRODUCTOS
# ============================================================================

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar productos
    
    list: Listar todos los productos disponibles
    retrieve: Detalle completo de un producto
    create: Crear nuevo producto (solo restaurantes)
    update: Actualizar producto (solo propietario)
    destroy: Eliminar producto (solo propietario)
    
    Filtros disponibles:
    - restaurant: ID del restaurante
    - category: ID de categoría
    - is_featured: true/false
    - is_new: true/false
    - is_popular: true/false
    - min_price: precio mínimo
    - max_price: precio máximo
    - tags: IDs de etiquetas (separados por coma)
    
    Búsqueda: name, description
    Ordenamiento: price, -price, rating, -rating, orders_count, -orders_count
    """
    
    queryset = Product.objects.filter(is_active=True, is_available=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'short_description']
    ordering_fields = ['price', 'rating', 'orders_count', 'created_at', 'preparation_time']
    ordering = ['-is_featured', '-rating', 'name']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Optimizar queries
        queryset = queryset.select_related(
            'restaurant',
            'category'
        ).prefetch_related(
            'tags',
            'images',
            'extras',
            'option_groups__options'
        )
        
        # Filtros adicionales desde query params
        restaurant_id = self.request.query_params.get('restaurant', None)
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        
        category_slug = self.request.query_params.get('category_slug', None)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filtrar por etiquetas
        tags = self.request.query_params.get('tags', None)
        if tags:
            tag_ids = tags.split(',')
            queryset = queryset.filter(tags__id__in=tag_ids).distinct()
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Incrementar contador de vistas al ver detalle"""
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    # ========================================================================
    # ACCIONES PERSONALIZADAS
    # ========================================================================
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Obtener productos destacados"""
        products = self.get_queryset().filter(is_featured=True)[:10]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Obtener productos populares (más ordenados)"""
        products = self.get_queryset().filter(
            is_popular=True
        ).order_by('-orders_count')[:10]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def new_arrivals(self, request):
        """Obtener productos nuevos"""
        products = self.get_queryset().filter(
            is_new=True
        ).order_by('-created_at')[:10]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def on_sale(self, request):
        """Obtener productos en oferta"""
        products = self.get_queryset().filter(
            compare_price__isnull=False
        ).exclude(
            compare_price=0
        ).order_by('-discount_percentage')[:20]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Búsqueda avanzada de productos"""
        query = request.query_params.get('q', '')
        
        if not query:
            return Response(
                {'error': 'Parámetro de búsqueda "q" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        products = self.get_queryset().filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()[:20]
        
        serializer = ProductSearchSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, slug=None):
        """Obtener reseñas de un producto"""
        product = self.get_object()
        reviews = product.reviews.filter(is_visible=True).select_related('customer')
        
        serializer = ProductReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def related(self, request, slug=None):
        """Obtener productos relacionados (misma categoría)"""
        product = self.get_object()
        
        related_products = self.get_queryset().filter(
            category=product.category
        ).exclude(id=product.id)[:6]
        
        serializer = ProductListSerializer(related_products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_availability(self, request, slug=None):
        """Cambiar disponibilidad del producto (solo propietario)"""
        product = self.get_object()
        
        # Verificar que el usuario sea el propietario del restaurante
        if product.restaurant.user != request.user:
            return Response(
                {'error': 'No tienes permisos para modificar este producto'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        product.is_available = not product.is_available
        product.save()
        
        return Response({
            'message': f'Producto {"disponible" if product.is_available else "no disponible"}',
            'is_available': product.is_available
        })


# ============================================================================
# VIEWSET DE RESEÑAS
# ============================================================================

class ProductReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar reseñas de productos
    
    list: Listar todas las reseñas visibles
    retrieve: Detalle de una reseña
    create: Crear nueva reseña (requiere autenticación)
    update: Actualizar reseña (solo autor)
    destroy: Eliminar reseña (solo autor)
    """
    
    queryset = ProductReview.objects.filter(is_visible=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'rating', 'is_verified']
    ordering_fields = ['rating', 'created_at', 'helpful_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProductReviewCreateSerializer
        return ProductReviewSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por producto si se proporciona
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        return queryset.select_related('customer', 'product')
    
    def perform_create(self, serializer):
        """Guardar reseña con el usuario actual"""
        serializer.save(customer=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_helpful(self, request, pk=None):
        """Marcar reseña como útil"""
        review = self.get_object()
        review.helpful_count += 1
        review.save()
        
        return Response({
            'message': 'Reseña marcada como útil',
            'helpful_count': review.helpful_count
        })


# ============================================================================
# VIEWSET DE ETIQUETAS
# ============================================================================

class ProductTagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar etiquetas de productos
    
    list: Listar todas las etiquetas activas
    retrieve: Detalle de una etiqueta
    """
    
    queryset = ProductTag.objects.filter(is_active=True)
    serializer_class = ProductTagSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['tag_type', 'name']
    lookup_field = 'slug'
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Obtener etiquetas agrupadas por tipo"""
        tags = self.get_queryset()
        
        grouped_tags = {}
        for tag in tags:
            tag_type = tag.get_tag_type_display()
            if tag_type not in grouped_tags:
                grouped_tags[tag_type] = []
            
            grouped_tags[tag_type].append(ProductTagSerializer(tag).data)
        
        return Response(grouped_tags)