# apps/orders/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Order, OrderItem, OrderRating
from .serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    OrderCreateSerializer,
    OrderUpdateSerializer,
    OrderCancelSerializer,
    OrderStatusUpdateSerializer,
    OrderRatingSerializer
)
from .filters import OrderFilter
from .permissions import IsOrderOwner, IsRestaurantOwner, IsDriverAssigned


# ============================================================================
# VIEWSET DE ORDERS
# ============================================================================

class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar pedidos
    
    list: Listar pedidos del usuario (clientes ven sus pedidos, restaurantes ven pedidos de su local)
    retrieve: Detalle completo de un pedido
    create: Crear nuevo pedido (solo clientes)
    update: Actualizar pedido (solo en estados tempranos)
    
    Acciones adicionales:
    - confirm: Confirmar pedido (restaurante)
    - prepare: Marcar como en preparación (restaurante)
    - ready: Marcar como listo (restaurante)
    - pickup: Marcar como recogido (conductor)
    - in_transit: Marcar como en camino (conductor)
    - deliver: Marcar como entregado (conductor)
    - cancel: Cancelar pedido
    - rate: Calificar pedido (cliente)
    - my_orders: Pedidos del cliente actual
    - restaurant_orders: Pedidos de un restaurante (solo dueño)
    - driver_orders: Pedidos asignados al conductor
    - statistics: Estadísticas generales
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ['order_number', 'delivery_address', 'special_instructions']
    ordering_fields = ['created_at', 'total', 'estimated_delivery_time']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderUpdateSerializer
        elif self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderListSerializer
    
    def get_queryset(self):
        """Filtrar pedidos según tipo de usuario"""
        user = self.request.user
        queryset = Order.objects.all()
        
        # Optimizar queries
        queryset = queryset.select_related(
            'customer',
            'restaurant',
            'driver',
            'rating'
        ).prefetch_related(
            'items',
            'status_history'
        )
        
        # Filtrar según rol
        if user.user_type == 'CUSTOMER':
            # Clientes ven solo sus pedidos
            queryset = queryset.filter(customer=user)
        
        elif user.user_type == 'RESTAURANT':
            # Restaurantes ven solo pedidos de su local
            if hasattr(user, 'restaurant_profile'):
                queryset = queryset.filter(restaurant=user.restaurant_profile)
            else:
                queryset = queryset.none()
        
        elif user.user_type == 'DRIVER':
            # Conductores ven pedidos asignados a ellos o disponibles
            queryset = queryset.filter(
                Q(driver=user) | Q(driver__isnull=True, status='READY')
            )
        
        elif user.user_type == 'ADMIN':
            # Admins ven todos los pedidos
            pass
        
        else:
            queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Crear pedido con el usuario actual como cliente"""
        serializer.save()
    
    # ========================================================================
    # ACCIONES DE CAMBIO DE ESTADO
    # ========================================================================
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def confirm(self, request, pk=None):
        """
        Confirmar un pedido (solo restaurante dueño)
        """
        order = self.get_object()
        
        # Verificar permisos
        if not hasattr(request.user, 'restaurant_profile'):
            return Response(
                {'error': 'Solo restaurantes pueden confirmar pedidos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if order.restaurant != request.user.restaurant_profile:
            return Response(
                {'error': 'No tienes permisos para confirmar este pedido'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            order.confirm(confirmed_by=request.user)
            serializer = OrderDetailSerializer(order)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def prepare(self, request, pk=None):
        """
        Marcar pedido como en preparación (solo restaurante dueño)
        """
        order = self.get_object()
        
        # Verificar permisos
        if not hasattr(request.user, 'restaurant_profile'):
            return Response(
                {'error': 'Solo restaurantes pueden cambiar el estado'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if order.restaurant != request.user.restaurant_profile:
            return Response(
                {'error': 'No tienes permisos para modificar este pedido'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            order.start_preparing(changed_by=request.user)
            serializer = OrderDetailSerializer(order)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def ready(self, request, pk=None):
        """
        Marcar pedido como listo para recoger (solo restaurante dueño)
        """
        order = self.get_object()
        
        # Verificar permisos
        if not hasattr(request.user, 'restaurant_profile'):
            return Response(
                {'error': 'Solo restaurantes pueden cambiar el estado'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if order.restaurant != request.user.restaurant_profile:
            return Response(
                {'error': 'No tienes permisos para modificar este pedido'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            order.mark_ready(changed_by=request.user)
            serializer = OrderDetailSerializer(order)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def pickup(self, request, pk=None):
        """
        Marcar pedido como recogido (solo conductor)
        """
        order = self.get_object()
        
        # Verificar que el usuario es un conductor
        if request.user.user_type != 'DRIVER':
            return Response(
                {'error': 'Solo conductores pueden recoger pedidos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar que el conductor está aprobado y disponible
        if hasattr(request.user, 'driver_profile'):
            driver_profile = request.user.driver_profile
            if driver_profile.status != 'APPROVED':
                return Response(
                    {'error': 'El conductor no está aprobado'},
                    status=status.HTTP_403_FORBIDDEN
                )
            if not driver_profile.is_available:
                return Response(
                    {'error': 'El conductor no está disponible'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        try:
            order.mark_picked_up(driver=request.user, changed_by=request.user)
            serializer = OrderDetailSerializer(order)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def in_transit(self, request, pk=None):
        """
        Marcar pedido como en camino (solo conductor asignado)
        """
        order = self.get_object()
        
        # Verificar que el usuario es el conductor asignado
        if order.driver != request.user:
            return Response(
                {'error': 'Solo el conductor asignado puede cambiar el estado'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            order.mark_in_transit(changed_by=request.user)
            serializer = OrderDetailSerializer(order)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def deliver(self, request, pk=None):
        """
        Marcar pedido como entregado (solo conductor asignado)
        """
        order = self.get_object()
        
        # Verificar que el usuario es el conductor asignado
        if order.driver != request.user:
            return Response(
                {'error': 'Solo el conductor asignado puede entregar el pedido'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            order.mark_delivered(changed_by=request.user)
            serializer = OrderDetailSerializer(order)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        """
        Cancelar un pedido
        """
        order = self.get_object()
        serializer = OrderCancelSerializer(
            data=request.data,
            context={'order': order}
        )
        
        if serializer.is_valid():
            # Verificar permisos
            user = request.user
            can_cancel = (
                user == order.customer or  # Cliente puede cancelar su pedido
                (hasattr(user, 'restaurant_profile') and 
                 user.restaurant_profile == order.restaurant) or  # Restaurante puede cancelar
                user.user_type == 'ADMIN'  # Admin puede cancelar
            )
            
            if not can_cancel:
                return Response(
                    {'error': 'No tienes permisos para cancelar este pedido'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            try:
                order.cancel(
                    reason=serializer.validated_data['cancellation_reason'],
                    notes=serializer.validated_data.get('cancellation_notes', ''),
                    cancelled_by=request.user
                )
                
                return Response(
                    OrderDetailSerializer(order).data,
                    status=status.HTTP_200_OK
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # ========================================================================
    # ACCIONES DE CALIFICACIÓN
    # ========================================================================
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rate(self, request, pk=None):
        """
        Calificar un pedido (solo cliente que hizo el pedido)
        """
        order = self.get_object()
        
        # Verificar que el usuario es el cliente del pedido
        if order.customer != request.user:
            return Response(
                {'error': 'Solo el cliente puede calificar el pedido'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = OrderRatingSerializer(
            data=request.data,
            context={'order': order}
        )
        
        if serializer.is_valid():
            serializer.save(order=order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def rating(self, request, pk=None):
        """
        Obtener la calificación de un pedido
        """
        order = self.get_object()
        
        if hasattr(order, 'rating'):
            serializer = OrderRatingSerializer(order.rating)
            return Response(serializer.data)
        
        return Response(
            {'message': 'Este pedido aún no ha sido calificado'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # ========================================================================
    # ACCIONES DE LISTADOS ESPECÍFICOS
    # ========================================================================
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_orders(self, request):
        """
        Obtener todos los pedidos del cliente actual
        """
        if request.user.user_type != 'CUSTOMER':
            return Response(
                {'error': 'Solo los clientes pueden ver sus pedidos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        orders = Order.objects.filter(customer=request.user).select_related(
            'restaurant',
            'driver'
        ).prefetch_related('items')
        
        # Filtrar por estado si se proporciona
        status_filter = request.query_params.get('status')
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        # Paginar
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = OrderListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def active_orders(self, request):
        """
        Obtener pedidos activos del cliente (no entregados ni cancelados)
        """
        if request.user.user_type != 'CUSTOMER':
            return Response(
                {'error': 'Solo los clientes pueden ver sus pedidos activos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        active_statuses = ['PENDING', 'CONFIRMED', 'PREPARING', 'READY', 'PICKED_UP', 'IN_TRANSIT']
        
        orders = Order.objects.filter(
            customer=request.user,
            status__in=active_statuses
        ).select_related(
            'restaurant',
            'driver'
        ).prefetch_related('items')
        
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def order_history(self, request):
        """
        Historial de pedidos completados del cliente
        """
        if request.user.user_type != 'CUSTOMER':
            return Response(
                {'error': 'Solo los clientes pueden ver su historial'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        orders = Order.objects.filter(
            customer=request.user,
            status__in=['DELIVERED', 'CANCELLED']
        ).select_related(
            'restaurant',
            'driver'
        ).prefetch_related('items')
        
        # Paginar
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = OrderListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def restaurant_orders(self, request):
        """
        Obtener pedidos del restaurante del usuario actual
        """
        if not hasattr(request.user, 'restaurant_profile'):
            return Response(
                {'error': 'Solo restaurantes pueden ver sus pedidos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        restaurant = request.user.restaurant_profile
        orders = Order.objects.filter(restaurant=restaurant).select_related(
            'customer',
            'driver'
        ).prefetch_related('items')
        
        # Filtrar por estado si se proporciona
        status_filter = request.query_params.get('status')
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        # Filtrar por fecha
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            orders = orders.filter(created_at__gte=date_from)
        if date_to:
            orders = orders.filter(created_at__lte=date_to)
        
        # Paginar
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = OrderListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def restaurant_active(self, request):
        """
        Obtener pedidos activos del restaurante (pendientes de completar)
        """
        if not hasattr(request.user, 'restaurant_profile'):
            return Response(
                {'error': 'Solo restaurantes pueden ver sus pedidos activos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        active_statuses = ['PENDING', 'CONFIRMED', 'PREPARING', 'READY']
        
        orders = Order.objects.filter(
            restaurant=request.user.restaurant_profile,
            status__in=active_statuses
        ).select_related(
            'customer',
            'driver'
        ).prefetch_related('items').order_by('created_at')
        
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def driver_orders(self, request):
        """
        Obtener pedidos asignados al conductor actual
        """
        if request.user.user_type != 'DRIVER':
            return Response(
                {'error': 'Solo conductores pueden ver sus pedidos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        orders = Order.objects.filter(driver=request.user).select_related(
            'customer',
            'restaurant'
        ).prefetch_related('items')
        
        # Filtrar por estado si se proporciona
        status_filter = request.query_params.get('status')
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        # Paginar
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = OrderListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def driver_active(self, request):
        """
        Obtener pedidos activos del conductor
        """
        if request.user.user_type != 'DRIVER':
            return Response(
                {'error': 'Solo conductores pueden ver sus pedidos activos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        active_statuses = ['PICKED_UP', 'IN_TRANSIT']
        
        orders = Order.objects.filter(
            driver=request.user,
            status__in=active_statuses
        ).select_related(
            'customer',
            'restaurant'
        ).prefetch_related('items')
        
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def available_for_pickup(self, request):
        """
        Obtener pedidos disponibles para ser recogidos por conductores
        """
        if request.user.user_type != 'DRIVER':
            return Response(
                {'error': 'Solo conductores pueden ver pedidos disponibles'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar que el conductor está aprobado
        if hasattr(request.user, 'driver_profile'):
            if request.user.driver_profile.status != 'APPROVED':
                return Response(
                    {'error': 'El conductor no está aprobado'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Pedidos listos sin conductor asignado
        orders = Order.objects.filter(
            status='READY',
            driver__isnull=True
        ).select_related(
            'customer',
            'restaurant'
        ).prefetch_related('items').order_by('created_at')
        
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    # ========================================================================
    # ESTADÍSTICAS
    # ========================================================================
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def statistics(self, request):
        """
        Estadísticas generales según tipo de usuario
        """
        user = request.user
        
        if user.user_type == 'CUSTOMER':
            # Estadísticas del cliente
            orders = Order.objects.filter(customer=user)
            
            stats = {
                'total_orders': orders.count(),
                'active_orders': orders.filter(
                    status__in=['PENDING', 'CONFIRMED', 'PREPARING', 'READY', 'PICKED_UP', 'IN_TRANSIT']
                ).count(),
                'completed_orders': orders.filter(status='DELIVERED').count(),
                'cancelled_orders': orders.filter(status='CANCELLED').count(),
                'total_spent': orders.filter(status='DELIVERED').aggregate(
                    total=Sum('total')
                )['total'] or 0,
                'average_order_value': orders.filter(status='DELIVERED').aggregate(
                    avg=Avg('total')
                )['avg'] or 0,
                'favorite_restaurant': None
            }
            
            # Restaurante favorito
            favorite = orders.filter(status='DELIVERED').values(
                'restaurant__id',
                'restaurant__name'
            ).annotate(
                count=Count('id')
            ).order_by('-count').first()
            
            if favorite:
                stats['favorite_restaurant'] = {
                    'id': favorite['restaurant__id'],
                    'name': favorite['restaurant__name'],
                    'order_count': favorite['count']
                }
            
            return Response(stats)
        
        elif user.user_type == 'RESTAURANT':
            # Estadísticas del restaurante
            if not hasattr(user, 'restaurant_profile'):
                return Response(
                    {'error': 'Usuario no tiene restaurante asociado'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            restaurant = user.restaurant_profile
            orders = Order.objects.filter(restaurant=restaurant)
            
            # Filtrar por rango de fechas si se proporciona
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            
            if date_from:
                orders = orders.filter(created_at__gte=date_from)
            if date_to:
                orders = orders.filter(created_at__lte=date_to)
            
            stats = {
                'total_orders': orders.count(),
                'pending_orders': orders.filter(status='PENDING').count(),
                'preparing_orders': orders.filter(status='PREPARING').count(),
                'ready_orders': orders.filter(status='READY').count(),
                'completed_orders': orders.filter(status='DELIVERED').count(),
                'cancelled_orders': orders.filter(status='CANCELLED').count(),
                'total_revenue': orders.filter(status='DELIVERED').aggregate(
                    total=Sum('total')
                )['total'] or 0,
                'average_order_value': orders.filter(status='DELIVERED').aggregate(
                    avg=Avg('total')
                )['avg'] or 0,
                'average_rating': restaurant.rating,
                'total_reviews': restaurant.total_reviews
            }
            
            return Response(stats)
        
        elif user.user_type == 'DRIVER':
            # Estadísticas del conductor
            orders = Order.objects.filter(driver=user)
            
            stats = {
                'total_deliveries': orders.filter(status='DELIVERED').count(),
                'active_deliveries': orders.filter(
                    status__in=['PICKED_UP', 'IN_TRANSIT']
                ).count(),
                'total_earnings': orders.filter(status='DELIVERED').aggregate(
                    total=Sum('delivery_fee')
                )['total'] or 0,
                'total_tips': orders.filter(status='DELIVERED').aggregate(
                    total=Sum('tip')
                )['total'] or 0,
                'average_rating': user.driver_profile.rating if hasattr(user, 'driver_profile') else 0,
                'completed_today': orders.filter(
                    status='DELIVERED',
                    delivered_at__date=timezone.now().date()
                ).count()
            }
            
            return Response(stats)
        
        elif user.user_type == 'ADMIN':
            # Estadísticas generales de la plataforma
            orders = Order.objects.all()
            
            # Filtrar por rango de fechas si se proporciona
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            
            if date_from:
                orders = orders.filter(created_at__gte=date_from)
            if date_to:
                orders = orders.filter(created_at__lte=date_to)
            
            stats = {
                'total_orders': orders.count(),
                'active_orders': orders.filter(
                    status__in=['PENDING', 'CONFIRMED', 'PREPARING', 'READY', 'PICKED_UP', 'IN_TRANSIT']
                ).count(),
                'completed_orders': orders.filter(status='DELIVERED').count(),
                'cancelled_orders': orders.filter(status='CANCELLED').count(),
                'total_revenue': orders.filter(status='DELIVERED').aggregate(
                    total=Sum('total')
                )['total'] or 0,
                'average_order_value': orders.filter(status='DELIVERED').aggregate(
                    avg=Avg('total')
                )['avg'] or 0,
                'orders_by_status': {
                    status_choice[0]: orders.filter(status=status_choice[0]).count()
                    for status_choice in Order.Status.choices
                },
                'orders_today': orders.filter(
                    created_at__date=timezone.now().date()
                ).count(),
                'revenue_today': orders.filter(
                    created_at__date=timezone.now().date(),
                    status='DELIVERED'
                ).aggregate(total=Sum('total'))['total'] or 0
            }
            
            return Response(stats)
        
        return Response(
            {'error': 'Tipo de usuario no válido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def track(self, request, pk=None):
        """
        Tracking en tiempo real del pedido
        """
        order = self.get_object()
        
        # Verificar permisos (cliente, restaurante o conductor)
        user = request.user
        can_track = (
            user == order.customer or
            (hasattr(user, 'restaurant_profile') and 
             user.restaurant_profile == order.restaurant) or
            user == order.driver or
            user.user_type == 'ADMIN'
        )
        
        if not can_track:
            return Response(
                {'error': 'No tienes permisos para rastrear este pedido'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        tracking_data = {
            'order_number': order.order_number,
            'status': order.status,
            'status_display': order.get_status_display(),
            'estimated_delivery_time': order.estimated_delivery_time,
            'is_delayed': order.is_delayed,
            'current_location': None,
            'restaurant_location': {
                'latitude': float(order.restaurant.latitude),
                'longitude': float(order.restaurant.longitude),
                'address': order.restaurant.address
            },
            'delivery_location': {
                'latitude': float(order.delivery_latitude),
                'longitude': float(order.delivery_longitude),
                'address': order.delivery_address
            },
            'driver': None,
            'timeline': []
        }
        
        # Información del conductor y ubicación actual
        if order.driver and hasattr(order.driver, 'driver_profile'):
            driver_profile = order.driver.driver_profile
            tracking_data['driver'] = {
                'name': order.driver.get_full_name(),
                'phone': order.driver.phone,
                'vehicle_type': driver_profile.get_vehicle_type_display(),
                'vehicle_plate': driver_profile.vehicle_plate,
                'rating': float(driver_profile.rating)
            }
            
            if driver_profile.current_latitude and driver_profile.current_longitude:
                tracking_data['current_location'] = {
                    'latitude': float(driver_profile.current_latitude),
                    'longitude': float(driver_profile.current_longitude)
                }
        
        # Timeline del pedido
        timeline = []
        
        timeline.append({
            'status': 'PENDING',
            'title': 'Pedido Creado',
            'timestamp': order.created_at,
            'completed': True
        })
        
        if order.confirmed_at:
            timeline.append({
                'status': 'CONFIRMED',
                'title': 'Confirmado por el Restaurante',
                'timestamp': order.confirmed_at,
                'completed': True
            })
        
        if order.preparing_at:
            timeline.append({
                'status': 'PREPARING',
                'title': 'En Preparación',
                'timestamp': order.preparing_at,
                'completed': True
            })
        
        if order.ready_at:
            timeline.append({
                'status': 'READY',
                'title': 'Listo para Recoger',
                'timestamp': order.ready_at,
                'completed': True
            })
        
        if order.picked_up_at:
            timeline.append({
                'status': 'PICKED_UP',
                'title': 'Recogido por el Conductor',
                'timestamp': order.picked_up_at,
                'completed': True
            })
        
        if order.status == 'IN_TRANSIT':
            timeline.append({
                'status': 'IN_TRANSIT',
                'title': 'En Camino',
                'timestamp': timezone.now(),
                'completed': True
            })
        
        if order.delivered_at:
            timeline.append({
                'status': 'DELIVERED',
                'title': 'Entregado',
                'timestamp': order.delivered_at,
                'completed': True
            })
        
        if order.cancelled_at:
            timeline.append({
                'status': 'CANCELLED',
                'title': 'Cancelado',
                'timestamp': order.cancelled_at,
                'completed': True,
                'reason': order.get_cancellation_reason_display()
            })
        
        tracking_data['timeline'] = timeline
        
        return Response(tracking_data)