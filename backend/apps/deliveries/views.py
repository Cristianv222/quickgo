# apps/deliveries/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import (
    Delivery,
    DeliveryLocation,
    DeliveryIssue
)
from .serializers import (
    DeliveryListSerializer,
    DeliveryDetailSerializer,
    DeliveryCreateSerializer,
    DeliveryAssignSerializer,
    DeliveryProofSerializer,
    DeliveryFailSerializer,
    DeliveryCancelSerializer,
    DeliveryLocationSerializer,
    DeliveryLocationCreateSerializer,
    DeliveryIssueSerializer,
    DeliveryIssueCreateSerializer,
    DeliveryTrackingSerializer
)
from .filters import DeliveryFilter
from .permissions import IsDeliveryDriver, IsDeliveryParticipant


# ============================================================================
# VIEWSET DE DELIVERIES
# ============================================================================

class DeliveryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar entregas
    
    list: Listar entregas (según rol del usuario)
    retrieve: Detalle completo de una entrega
    create: Crear nueva entrega (automático, solo admins)
    
    Acciones adicionales:
    - assign: Asignar conductor
    - accept: Conductor acepta la entrega
    - start_pickup: Iniciar recogida
    - confirm_pickup: Confirmar recogida
    - start_transit: Iniciar tránsito
    - mark_arrived: Marcar llegada
    - complete: Completar entrega con prueba
    - fail: Marcar como fallida
    - cancel: Cancelar entrega
    - track: Tracking en tiempo real
    - my_deliveries: Entregas del conductor
    - available: Entregas disponibles para recoger
    - statistics: Estadísticas
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DeliveryFilter
    search_fields = [
        'order__order_number',
        'customer_name',
        'customer_phone',
        'delivery_address',
        'pickup_address'
    ]
    ordering_fields = ['created_at', 'priority', 'estimated_delivery_time']
    ordering = ['-priority', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DeliveryCreateSerializer
        elif self.action == 'retrieve' or self.action == 'track':
            return DeliveryDetailSerializer
        return DeliveryListSerializer
    
    def get_queryset(self):
        """Filtrar entregas según tipo de usuario"""
        user = self.request.user
        queryset = Delivery.objects.all()
        
        # Optimizar queries
        queryset = queryset.select_related(
            'order',
            'order__customer',
            'order__restaurant',
            'driver'
        ).prefetch_related(
            'status_history',
            'issues',
            'location_tracking'
        )
        
        # Filtrar según rol
        if user.user_type == 'CUSTOMER':
            # Clientes ven solo entregas de sus pedidos
            queryset = queryset.filter(order__customer=user)
        
        elif user.user_type == 'RESTAURANT':
            # Restaurantes ven entregas de sus pedidos
            if hasattr(user, 'restaurant_profile'):
                queryset = queryset.filter(order__restaurant=user.restaurant_profile)
            else:
                queryset = queryset.none()
        
        elif user.user_type == 'DRIVER':
            # Conductores ven sus entregas o disponibles
            queryset = queryset.filter(
                Q(driver=user) | Q(status='PENDING', driver__isnull=True)
            )
        
        elif user.user_type == 'ADMIN':
            # Admins ven todas las entregas
            pass
        
        else:
            queryset = queryset.none()
        
        return queryset
    
    # ========================================================================
    # ACCIONES DE ASIGNACIÓN Y ACEPTACIÓN
    # ========================================================================
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def assign(self, request, pk=None):
        """
        Asignar conductor a una entrega (admin o sistema)
        """
        delivery = self.get_object()
        
        # Solo admins pueden asignar manualmente
        if request.user.user_type != 'ADMIN':
            return Response(
                {'error': 'Solo administradores pueden asignar conductores manualmente'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = DeliveryAssignSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                from apps.users.models import User
                driver = User.objects.get(id=serializer.validated_data['driver_id'])
                delivery.assign_driver(driver)
                
                return Response(
                    DeliveryDetailSerializer(delivery).data,
                    status=status.HTTP_200_OK
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def accept(self, request, pk=None):
        """
        Conductor acepta una entrega pendiente (auto-asignación)
        """
        delivery = self.get_object()
        
        # Verificar que el usuario es conductor
        if request.user.user_type != 'DRIVER':
            return Response(
                {'error': 'Solo conductores pueden aceptar entregas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar que la entrega está pendiente
        if delivery.status != 'PENDING':
            return Response(
                {'error': 'Esta entrega ya fue asignada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            delivery.assign_driver(request.user)
            return Response(
                DeliveryDetailSerializer(delivery).data,
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # ========================================================================
    # ACCIONES DE FLUJO DE ENTREGA
    # ========================================================================
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def start_pickup(self, request, pk=None):
        """
        Conductor inicia recogida del pedido
        """
        delivery = self.get_object()
        
        # Verificar que el usuario es el conductor asignado
        if delivery.driver != request.user:
            return Response(
                {'error': 'Solo el conductor asignado puede iniciar la recogida'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            delivery.start_pickup()
            return Response(
                DeliveryDetailSerializer(delivery).data,
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def confirm_pickup(self, request, pk=None):
        """
        Confirmar que se recogió el pedido del restaurante
        """
        delivery = self.get_object()
        
        # Verificar que el usuario es el conductor asignado
        if delivery.driver != request.user:
            return Response(
                {'error': 'Solo el conductor asignado puede confirmar la recogida'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            delivery.confirm_pickup()
            return Response(
                DeliveryDetailSerializer(delivery).data,
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def start_transit(self, request, pk=None):
        """
        Iniciar tránsito hacia el cliente
        """
        delivery = self.get_object()
        
        # Verificar que el usuario es el conductor asignado
        if delivery.driver != request.user:
            return Response(
                {'error': 'Solo el conductor asignado puede iniciar el tránsito'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            delivery.start_transit()
            return Response(
                DeliveryDetailSerializer(delivery).data,
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_arrived(self, request, pk=None):
        """
        Marcar llegada al destino
        """
        delivery = self.get_object()
        
        # Verificar que el usuario es el conductor asignado
        if delivery.driver != request.user:
            return Response(
                {'error': 'Solo el conductor asignado puede marcar la llegada'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            delivery.mark_arrived()
            return Response(
                DeliveryDetailSerializer(delivery).data,
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        """
        Completar entrega con prueba (foto/firma)
        """
        delivery = self.get_object()
        
        # Verificar que el usuario es el conductor asignado
        if delivery.driver != request.user:
            return Response(
                {'error': 'Solo el conductor asignado puede completar la entrega'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = DeliveryProofSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                delivery.complete_delivery(
                    proof_photo=serializer.validated_data.get('proof_photo'),
                    signature=serializer.validated_data.get('signature'),
                    notes=serializer.validated_data.get('notes', '')
                )
                
                return Response(
                    DeliveryDetailSerializer(delivery).data,
                    status=status.HTTP_200_OK
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def fail(self, request, pk=None):
        """
        Marcar entrega como fallida
        """
        delivery = self.get_object()
        
        # Verificar que el usuario es el conductor asignado
        if delivery.driver != request.user:
            return Response(
                {'error': 'Solo el conductor asignado puede marcar la entrega como fallida'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = DeliveryFailSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                delivery.mark_failed(
                    reason=serializer.validated_data['reason'],
                    notes=serializer.validated_data['notes'],
                    photo=serializer.validated_data.get('photo')
                )
                
                return Response(
                    DeliveryDetailSerializer(delivery).data,
                    status=status.HTTP_200_OK
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        """
        Cancelar entrega
        """
        delivery = self.get_object()
        
        # Verificar permisos
        user = request.user
        can_cancel = (
            user == delivery.driver or
            (hasattr(user, 'restaurant_profile') and 
             user.restaurant_profile == delivery.order.restaurant) or
            user.user_type == 'ADMIN'
        )
        
        if not can_cancel:
            return Response(
                {'error': 'No tienes permisos para cancelar esta entrega'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = DeliveryCancelSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                delivery.cancel(reason=serializer.validated_data.get('reason', ''))
                
                return Response(
                    DeliveryDetailSerializer(delivery).data,
                    status=status.HTTP_200_OK
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # ========================================================================
    # ACCIONES DE TRACKING
    # ========================================================================
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def track(self, request, pk=None):
        """
        Tracking en tiempo real de la entrega
        """
        delivery = self.get_object()
        
        # Verificar permisos (cliente, restaurante, conductor o admin)
        user = request.user
        can_track = (
            user == delivery.order.customer or
            (hasattr(user, 'restaurant_profile') and 
             user.restaurant_profile == delivery.order.restaurant) or
            user == delivery.driver or
            user.user_type == 'ADMIN'
        )
        
        if not can_track:
            return Response(
                {'error': 'No tienes permisos para rastrear esta entrega'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = DeliveryTrackingSerializer(delivery)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def update_location(self, request, pk=None):
        """
        Actualizar ubicación del conductor (GPS tracking)
        """
        delivery = self.get_object()
        
        # Verificar que el usuario es el conductor asignado
        if delivery.driver != request.user:
            return Response(
                {'error': 'Solo el conductor asignado puede actualizar la ubicación'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar que la entrega está activa
        if delivery.status not in ['ASSIGNED', 'PICKING_UP', 'PICKED_UP', 'IN_TRANSIT', 'ARRIVED']:
            return Response(
                {'error': 'La entrega no está activa'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = DeliveryLocationCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            # Crear registro de ubicación
            location = DeliveryLocation.objects.create(
                delivery=delivery,
                driver=request.user,
                **serializer.validated_data
            )
            
            # Actualizar ubicación actual del conductor en su perfil
            if hasattr(request.user, 'driver_profile'):
                profile = request.user.driver_profile
                profile.current_latitude = location.latitude
                profile.current_longitude = location.longitude
                profile.save(update_fields=['current_latitude', 'current_longitude'])
            
            return Response(
                DeliveryLocationSerializer(location).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def location_history(self, request, pk=None):
        """
        Historial de ubicaciones de la entrega
        """
        delivery = self.get_object()
        
        # Verificar permisos
        user = request.user
        can_view = (
            user == delivery.order.customer or
            (hasattr(user, 'restaurant_profile') and 
             user.restaurant_profile == delivery.order.restaurant) or
            user == delivery.driver or
            user.user_type == 'ADMIN'
        )
        
        if not can_view:
            return Response(
                {'error': 'No tienes permisos para ver el historial de ubicaciones'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Obtener últimas ubicaciones
        limit = int(request.query_params.get('limit', 50))
        locations = delivery.location_tracking.all()[:limit]
        
        serializer = DeliveryLocationSerializer(locations, many=True)
        return Response(serializer.data)
    
    # ========================================================================
    # ACCIONES DE LISTADOS ESPECÍFICOS
    # ========================================================================
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_deliveries(self, request):
        """
        Entregas del conductor actual
        """
        if request.user.user_type != 'DRIVER':
            return Response(
                {'error': 'Solo conductores pueden ver sus entregas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        deliveries = Delivery.objects.filter(driver=request.user).select_related(
            'order',
            'order__restaurant'
        ).prefetch_related('status_history')
        
        # Filtrar por estado si se proporciona
        status_filter = request.query_params.get('status')
        if status_filter:
            deliveries = deliveries.filter(status=status_filter)
        
        # Paginar
        page = self.paginate_queryset(deliveries)
        if page is not None:
            serializer = DeliveryListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = DeliveryListSerializer(deliveries, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def active_deliveries(self, request):
        """
        Entregas activas del conductor
        """
        if request.user.user_type != 'DRIVER':
            return Response(
                {'error': 'Solo conductores pueden ver entregas activas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        active_statuses = ['ASSIGNED', 'PICKING_UP', 'PICKED_UP', 'IN_TRANSIT', 'ARRIVED']
        
        deliveries = Delivery.objects.filter(
            driver=request.user,
            status__in=active_statuses
        ).select_related(
            'order',
            'order__restaurant'
        ).prefetch_related('status_history')
        
        serializer = DeliveryListSerializer(deliveries, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def available(self, request):
        """
        Entregas disponibles para ser recogidas por conductores
        """
        if request.user.user_type != 'DRIVER':
            return Response(
                {'error': 'Solo conductores pueden ver entregas disponibles'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar que el conductor está aprobado
        if hasattr(request.user, 'driver_profile'):
            if request.user.driver_profile.status != 'APPROVED':
                return Response(
                    {'error': 'El conductor no está aprobado'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Entregas pendientes sin conductor
        deliveries = Delivery.objects.filter(
            status='PENDING',
            driver__isnull=True
        ).select_related(
            'order',
            'order__restaurant'
        ).order_by('-priority', 'created_at')
        
        serializer = DeliveryListSerializer(deliveries, many=True)
        return Response(serializer.data)
    
    # ========================================================================
    # ESTADÍSTICAS
    # ========================================================================
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def statistics(self, request):
        """
        Estadísticas de entregas según tipo de usuario
        """
        user = request.user
        
        if user.user_type == 'DRIVER':
            # Estadísticas del conductor
            deliveries = Delivery.objects.filter(driver=user)
            
            stats = {
                'total_deliveries': deliveries.count(),
                'active_deliveries': deliveries.filter(
                    status__in=['ASSIGNED', 'PICKING_UP', 'PICKED_UP', 'IN_TRANSIT', 'ARRIVED']
                ).count(),
                'completed_deliveries': deliveries.filter(status='DELIVERED').count(),
                'failed_deliveries': deliveries.filter(status='FAILED').count(),
                'cancelled_deliveries': deliveries.filter(status='CANCELLED').count(),
                'total_earnings': deliveries.filter(status='DELIVERED').aggregate(
                    total=Sum('driver_earnings')
                )['total'] or 0,
                'average_delivery_time': deliveries.filter(status='DELIVERED').aggregate(
                    avg=Avg('total_delivery_time')
                )['avg'] or 0,
                'total_distance': deliveries.filter(status='DELIVERED').aggregate(
                    total=Sum('total_distance')
                )['total'] or 0,
                'deliveries_today': deliveries.filter(
                    status='DELIVERED',
                    delivered_at__date=timezone.now().date()
                ).count(),
                'earnings_today': deliveries.filter(
                    status='DELIVERED',
                    delivered_at__date=timezone.now().date()
                ).aggregate(total=Sum('driver_earnings'))['total'] or 0
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
            deliveries = Delivery.objects.filter(order__restaurant=restaurant)
            
            stats = {
                'total_deliveries': deliveries.count(),
                'pending_pickup': deliveries.filter(
                    status__in=['PENDING', 'ASSIGNED', 'PICKING_UP']
                ).count(),
                'in_progress': deliveries.filter(
                    status__in=['PICKED_UP', 'IN_TRANSIT', 'ARRIVED']
                ).count(),
                'completed_deliveries': deliveries.filter(status='DELIVERED').count(),
                'failed_deliveries': deliveries.filter(status='FAILED').count(),
                'average_pickup_time': deliveries.filter(status='DELIVERED').aggregate(
                    avg=Avg('pickup_time')
                )['avg'] or 0
            }
            
            return Response(stats)
        
        elif user.user_type == 'ADMIN':
            # Estadísticas generales
            deliveries = Delivery.objects.all()
            
            # Filtrar por rango de fechas si se proporciona
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            
            if date_from:
                deliveries = deliveries.filter(created_at__gte=date_from)
            if date_to:
                deliveries = deliveries.filter(created_at__lte=date_to)
            
            stats = {
                'total_deliveries': deliveries.count(),
                'pending_deliveries': deliveries.filter(status='PENDING').count(),
                'active_deliveries': deliveries.filter(
                    status__in=['ASSIGNED', 'PICKING_UP', 'PICKED_UP', 'IN_TRANSIT', 'ARRIVED']
                ).count(),
                'completed_deliveries': deliveries.filter(status='DELIVERED').count(),
                'failed_deliveries': deliveries.filter(status='FAILED').count(),
                'cancelled_deliveries': deliveries.filter(status='CANCELLED').count(),
                'total_driver_earnings': deliveries.filter(status='DELIVERED').aggregate(
                    total=Sum('driver_earnings')
                )['total'] or 0,
                'average_delivery_time': deliveries.filter(status='DELIVERED').aggregate(
                    avg=Avg('total_delivery_time')
                )['avg'] or 0,
                'total_distance': deliveries.filter(status='DELIVERED').aggregate(
                    total=Sum('total_distance')
                )['total'] or 0,
                'deliveries_by_status': {
                    status_choice[0]: deliveries.filter(status=status_choice[0]).count()
                    for status_choice in Delivery.Status.choices
                },
                'deliveries_today': deliveries.filter(
                    created_at__date=timezone.now().date()
                ).count()
            }
            
            return Response(stats)
        
        return Response(
            {'error': 'Tipo de usuario no válido'},
            status=status.HTTP_400_BAD_REQUEST
        )


# ============================================================================
# VIEWSET DE DELIVERY ISSUES
# ============================================================================

class DeliveryIssueViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar problemas de entrega
    
    list: Listar problemas
    retrieve: Detalle de un problema
    create: Reportar nuevo problema
    update: Actualizar problema (resolver)
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['delivery', 'issue_type', 'is_resolved']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DeliveryIssueCreateSerializer
        return DeliveryIssueSerializer
    
    def get_queryset(self):
        """Filtrar problemas según usuario"""
        user = self.request.user
        queryset = DeliveryIssue.objects.all()
        
        if user.user_type == 'DRIVER':
            queryset = queryset.filter(
                Q(delivery__driver=user) | Q(reported_by=user)
            )
        elif user.user_type == 'RESTAURANT':
            if hasattr(user, 'restaurant_profile'):
                queryset = queryset.filter(
                    delivery__order__restaurant=user.restaurant_profile
                )
        elif user.user_type == 'CUSTOMER':
            queryset = queryset.filter(delivery__order__customer=user)
        elif user.user_type != 'ADMIN':
            queryset = queryset.none()
        
        return queryset.select_related('delivery', 'reported_by')
    
    def perform_create(self, serializer):
        """Crear problema con el usuario actual"""
        serializer.save(reported_by=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def resolve(self, request, pk=None):
        """
        Marcar problema como resuelto
        """
        issue = self.get_object()
        
        # Solo admins pueden resolver
        if request.user.user_type != 'ADMIN':
            return Response(
                {'error': 'Solo administradores pueden resolver problemas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        resolution_notes = request.data.get('resolution_notes', '')
        
        issue.is_resolved = True
        issue.resolution_notes = resolution_notes
        issue.resolved_at = timezone.now()
        issue.save()
        
        serializer = DeliveryIssueSerializer(issue)
        return Response(serializer.data)