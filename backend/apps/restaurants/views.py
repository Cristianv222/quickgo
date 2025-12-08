from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Count, Avg
from django.utils import timezone
from .models import Restaurant, RestaurantReview, RestaurantSchedule
from .serializers import (
    RestaurantListSerializer, RestaurantDetailSerializer,
    RestaurantCreateSerializer, RestaurantReviewSerializer,
    ReviewCreateSerializer, RestaurantScheduleSerializer
)


class RestaurantViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar restaurantes
    
    Endpoints:
    - GET /api/restaurants/ - Lista todos los restaurantes
    - GET /api/restaurants/{id}/ - Detalle de restaurante
    - GET /api/restaurants/nearby/ - Restaurantes cercanos
    - GET /api/restaurants/featured/ - Restaurantes destacados
    - GET /api/restaurants/search/ - Búsqueda de restaurantes
    - POST /api/restaurants/{id}/toggle_favorite/ - Agregar/quitar favorito
    """
    
    queryset = Restaurant.objects.filter(
        status=Restaurant.Status.APPROVED
    ).select_related('user').prefetch_related('schedules', 'gallery')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'cuisine_type']
    ordering_fields = ['rating', 'total_reviews', 'delivery_fee', 'created_at']
    ordering = ['-is_featured', '-rating']
    
    def get_permissions(self):
        """Define permisos según la acción"""
        if self.action in ['list', 'retrieve', 'nearby', 'featured', 'search', 'menu']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'retrieve':
            return RestaurantDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RestaurantCreateSerializer
        return RestaurantListSerializer
    
    def get_queryset(self):
        """Filtra restaurantes según parámetros"""
        queryset = super().get_queryset()
        
        # Filtro por tipo de cocina
        cuisine_type = self.request.query_params.get('cuisine_type')
        if cuisine_type:
            queryset = queryset.filter(cuisine_type=cuisine_type)
        
        # Filtro por restaurantes abiertos
        is_open = self.request.query_params.get('is_open')
        if is_open == 'true':
            queryset = queryset.filter(is_open=True, is_accepting_orders=True)
        
        # Filtro por rating mínimo
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            try:
                queryset = queryset.filter(rating__gte=float(min_rating))
            except ValueError:
                pass
        
        # Filtro por rango de precio de envío
        max_delivery_fee = self.request.query_params.get('max_delivery_fee')
        if max_delivery_fee:
            try:
                queryset = queryset.filter(delivery_fee__lte=float(max_delivery_fee))
            except ValueError:
                pass
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Lista restaurantes con ubicación del usuario"""
        # Guarda ubicación del usuario en el request
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        
        if latitude and longitude:
            try:
                request.user_location = {
                    'latitude': float(latitude),
                    'longitude': float(longitude)
                }
            except ValueError:
                pass
        
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """Detalle de restaurante con ubicación del usuario"""
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        
        if latitude and longitude:
            try:
                request.user_location = {
                    'latitude': float(latitude),
                    'longitude': float(longitude)
                }
            except ValueError:
                pass
        
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """
        GET /api/restaurants/nearby/?latitude=X&longitude=Y&radius=5
        Retorna restaurantes cercanos ordenados por distancia
        """
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        radius = request.query_params.get('radius', 5)  # Radio en km
        
        if not latitude or not longitude:
            return Response(
                {'error': 'Se requieren parámetros latitude y longitude'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_lat = float(latitude)
            user_lon = float(longitude)
            radius = float(radius)
        except ValueError:
            return Response(
                {'error': 'Coordenadas inválidas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Guarda ubicación en request
        request.user_location = {
            'latitude': user_lat,
            'longitude': user_lon
        }
        
        # Filtra restaurantes dentro del radio
        nearby_restaurants = []
        for restaurant in self.get_queryset():
            if restaurant.is_within_delivery_radius(user_lat, user_lon):
                nearby_restaurants.append(restaurant)
        
        # Serializa y ordena por distancia
        serializer = self.get_serializer(nearby_restaurants, many=True)
        data = sorted(
            serializer.data,
            key=lambda x: x.get('distance', float('inf'))
        )
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        GET /api/restaurants/featured/
        Retorna restaurantes destacados
        """
        featured = self.get_queryset().filter(is_featured=True)[:10]
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        GET /api/restaurants/search/?q=pizza&cuisine_type=PIZZA
        Búsqueda avanzada de restaurantes
        """
        query = request.query_params.get('q', '')
        
        if len(query) < 2:
            return Response(
                {'error': 'La búsqueda debe tener al menos 2 caracteres'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = self.get_queryset().filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(cuisine_type__icontains=query)
        )
        
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_favorite(self, request, pk=None):
        """
        POST /api/restaurants/{id}/toggle_favorite/
        Agrega o quita restaurante de favoritos
        """
        restaurant = self.get_object()
        user = request.user
        
        # Implementa tu lógica de favoritos aquí
        # Ejemplo: usando un modelo FavoriteRestaurant
        
        return Response({
            'message': 'Funcionalidad de favoritos por implementar',
            'restaurant_id': restaurant.id
        })
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def menu(self, request, pk=None):
        """
        GET /api/restaurants/{id}/menu/
        Retorna el menú (productos) de un restaurante
        """
        from apps.products.models import Product
        from apps.products.serializers import ProductListSerializer
        
        restaurant = self.get_object()
        products = Product.objects.filter(
            restaurant=restaurant,
            is_active=True
        ).select_related('restaurant', 'category').prefetch_related('extras', 'option_groups')
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class RestaurantReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar reseñas de restaurantes
    
    Endpoints:
    - GET /api/restaurant-reviews/ - Lista reseñas
    - GET /api/restaurant-reviews/{id}/ - Detalle de reseña
    - POST /api/restaurant-reviews/ - Crear reseña
    - GET /api/restaurant-reviews/restaurant/{restaurant_id}/ - Reseñas por restaurante
    """
    
    queryset = RestaurantReview.objects.filter(is_visible=True).select_related(
        'restaurant', 'customer'
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado"""
        if self.action == 'create':
            return ReviewCreateSerializer
        return RestaurantReviewSerializer
    
    def get_queryset(self):
        """Filtra reseñas según parámetros"""
        queryset = super().get_queryset()
        
        # Filtro por restaurante
        restaurant_id = self.request.query_params.get('restaurant_id')
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        
        # Filtro por rating mínimo
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            try:
                queryset = queryset.filter(rating__gte=int(min_rating))
            except ValueError:
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'], url_path='restaurant/(?P<restaurant_id>[^/.]+)')
    def by_restaurant(self, request, restaurant_id=None):
        """
        GET /api/restaurant-reviews/restaurant/{restaurant_id}/
        Obtiene todas las reseñas de un restaurante
        """
        reviews = self.get_queryset().filter(restaurant_id=restaurant_id)
        
        # Estadísticas
        stats = reviews.aggregate(
            avg_rating=Avg('rating'),
            avg_food=Avg('food_quality'),
            avg_delivery=Avg('delivery_time'),
            avg_packaging=Avg('packaging'),
            total=Count('id')
        )
        
        serializer = self.get_serializer(reviews, many=True)
        
        return Response({
            'reviews': serializer.data,
            'statistics': {
                'average_rating': round(stats['avg_rating'] or 0, 1),
                'average_food_quality': round(stats['avg_food'] or 0, 1),
                'average_delivery_time': round(stats['avg_delivery'] or 0, 1),
                'average_packaging': round(stats['avg_packaging'] or 0, 1),
                'total_reviews': stats['total']
            }
        })