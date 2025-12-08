from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from django.shortcuts import get_object_or_404
from decimal import Decimal

from .models import (
    Payment,
    PaymentStatusHistory,
    Refund,
    PaymentMethod,
    Payout
)
from .serializers import (
    PaymentListSerializer,
    PaymentDetailSerializer,
    PaymentCreateSerializer,
    PaymentProcessSerializer,
    PaymentRefundSerializer,
    PaymentMethodSerializer,
    PaymentMethodCreateSerializer,
    PayoutSerializer,
    PayoutCreateSerializer,
    PaymentStatisticsSerializer
)


# ============================================================================
# VIEWSET DE PAYMENTS
# ============================================================================

class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar pagos
    
    list: Listar pagos del usuario
    retrieve: Detalle completo de un pago
    create: Crear nuevo pago
    
    Acciones adicionales:
    - process: Procesar un pago pendiente
    - complete: Marcar pago como completado (admin)
    - fail: Marcar pago como fallido (admin)
    - cancel: Cancelar un pago
    - refund: Solicitar reembolso
    - my_payments: Pagos del usuario actual
    - statistics: Estadísticas de pagos
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'transaction_id',
        'order__order_number',
        'user__email',
        'card_last4'
    ]
    filterset_fields = [
        'status',
        'payment_method',
        'transaction_type',
        'order'
    ]
    ordering_fields = ['created_at', 'amount', 'completed_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        elif self.action == 'retrieve':
            return PaymentDetailSerializer
        elif self.action == 'process':
            return PaymentProcessSerializer
        elif self.action == 'refund':
            return PaymentRefundSerializer
        return PaymentListSerializer
    
    def get_queryset(self):
        """Filtrar pagos según tipo de usuario"""
        user = self.request.user
        queryset = Payment.objects.all()
        
        # Optimizar queries
        queryset = queryset.select_related(
            'order',
            'order__customer',
            'order__restaurant',
            'user',
            'refunded_by'
        ).prefetch_related(
            'status_history',
            'refunds'
        )
        
        # Filtrar según rol
        if user.user_type == 'CUSTOMER':
            # Clientes ven solo sus pagos
            queryset = queryset.filter(user=user)
        
        elif user.user_type == 'RESTAURANT':
            # Restaurantes ven pagos de sus pedidos
            if hasattr(user, 'restaurant_profile'):
                queryset = queryset.filter(order__restaurant=user.restaurant_profile)
            else:
                queryset = queryset.none()
        
        elif user.user_type == 'DRIVER':
            # Conductores ven pagos de pedidos asignados
            queryset = queryset.filter(order__driver=user)
        
        elif user.user_type == 'ADMIN':
            # Admins ven todos los pagos
            pass
        
        else:
            queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Crear pago con el usuario actual"""
        serializer.save()
    
    # ========================================================================
    # ACCIONES DE PROCESAMIENTO
    # ========================================================================
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def process(self, request, pk=None):
        """
        Procesar un pago pendiente
        """
        payment = self.get_object()
        
        # Verificar que el usuario es el dueño del pago
        if payment.user != request.user and request.user.user_type != 'ADMIN':
            return Response(
                {'error': 'No tienes permisos para procesar este pago'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PaymentProcessSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Marcar como procesando
                payment.mark_as_processing()
                
                # Aquí iría la integración con la pasarela de pago
                # Por ahora, simplemente lo marcamos como completado
                
                # TODO: Integrar con Stripe/PayPal/MercadoPago
                # stripe_payment_method = serializer.validated_data.get('stripe_payment_method_id')
                # if stripe_payment_method:
                #     # Procesar con Stripe
                #     pass
                
                # Marcar como completado
                payment.mark_as_completed()
                
                return Response(
                    PaymentDetailSerializer(payment).data,
                    status=status.HTTP_200_OK
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def complete(self, request, pk=None):
        """
        Marcar pago como completado (solo admin)
        """
        payment = self.get_object()
        
        try:
            payment.mark_as_completed()
            return Response(
                PaymentDetailSerializer(payment).data,
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def fail(self, request, pk=None):
        """
        Marcar pago como fallido (solo admin)
        """
        payment = self.get_object()
        
        reason = request.data.get('reason', 'OTHER')
        message = request.data.get('message', 'Pago marcado como fallido')
        
        try:
            payment.mark_as_failed(reason=reason, message=message)
            return Response(
                PaymentDetailSerializer(payment).data,
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        """
        Cancelar un pago
        """
        payment = self.get_object()
        
        # Verificar permisos
        if payment.user != request.user and request.user.user_type != 'ADMIN':
            return Response(
                {'error': 'No tienes permisos para cancelar este pago'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reason = request.data.get('reason', 'Cancelado por el usuario')
        
        try:
            payment.cancel(reason=reason)
            return Response(
                PaymentDetailSerializer(payment).data,
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def refund(self, request, pk=None):
        """
        Solicitar reembolso de un pago
        """
        payment = self.get_object()
        
        # Verificar permisos
        can_refund = (
            payment.user == request.user or
            (hasattr(request.user, 'restaurant_profile') and
             payment.order.restaurant == request.user.restaurant_profile) or
            request.user.user_type == 'ADMIN'
        )
        
        if not can_refund:
            return Response(
                {'error': 'No tienes permisos para reembolsar este pago'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PaymentRefundSerializer(
            data=request.data,
            context={'payment': payment}
        )
        
        if serializer.is_valid():
            try:
                amount = serializer.validated_data.get('amount')
                reason = serializer.validated_data['reason']
                
                payment.refund(
                    amount=amount,
                    reason=reason,
                    refunded_by=request.user
                )
                
                return Response(
                    PaymentDetailSerializer(payment).data,
                    status=status.HTTP_200_OK
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # ========================================================================
    # LISTADOS ESPECÍFICOS
    # ========================================================================
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_payments(self, request):
        """
        Obtener todos los pagos del usuario actual
        """
        payments = Payment.objects.filter(user=request.user).select_related(
            'order',
            'order__restaurant'
        ).prefetch_related('refunds')
        
        # Filtrar por estado si se proporciona
        status_filter = request.query_params.get('status')
        if status_filter:
            payments = payments.filter(status=status_filter)
        
        # Paginar
        page = self.paginate_queryset(payments)
        if page is not None:
            serializer = PaymentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def pending(self, request):
        """
        Obtener pagos pendientes del usuario
        """
        if request.user.user_type != 'CUSTOMER':
            return Response(
                {'error': 'Solo clientes pueden ver pagos pendientes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        payments = Payment.objects.filter(
            user=request.user,
            status__in=['PENDING', 'PROCESSING']
        ).select_related('order', 'order__restaurant')
        
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def completed(self, request):
        """
        Obtener pagos completados del usuario
        """
        payments = Payment.objects.filter(
            user=request.user,
            status='COMPLETED'
        ).select_related('order', 'order__restaurant')
        
        # Paginar
        page = self.paginate_queryset(payments)
        if page is not None:
            serializer = PaymentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def restaurant_payments(self, request):
        """
        Obtener pagos del restaurante del usuario
        """
        if not hasattr(request.user, 'restaurant_profile'):
            return Response(
                {'error': 'Solo restaurantes pueden ver estos pagos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        restaurant = request.user.restaurant_profile
        payments = Payment.objects.filter(
            order__restaurant=restaurant
        ).select_related('order', 'user')
        
        # Filtrar por estado
        status_filter = request.query_params.get('status')
        if status_filter:
            payments = payments.filter(status=status_filter)
        
        # Filtrar por fecha
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            payments = payments.filter(created_at__gte=date_from)
        if date_to:
            payments = payments.filter(created_at__lte=date_to)
        
        # Paginar
        page = self.paginate_queryset(payments)
        if page is not None:
            serializer = PaymentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)
    
    # ========================================================================
    # ESTADÍSTICAS
    # ========================================================================
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def statistics(self, request):
        """
        Estadísticas de pagos según tipo de usuario
        """
        user = request.user
        
        if user.user_type == 'CUSTOMER':
            # Estadísticas del cliente
            payments = Payment.objects.filter(user=user)
            
            stats = {
                'total_payments': payments.count(),
                'completed_payments': payments.filter(status='COMPLETED').count(),
                'pending_payments': payments.filter(status__in=['PENDING', 'PROCESSING']).count(),
                'failed_payments': payments.filter(status='FAILED').count(),
                'total_spent': payments.filter(status='COMPLETED').aggregate(
                    total=Sum('amount')
                )['total'] or Decimal('0.00'),
                'total_refunded': payments.aggregate(
                    total=Sum('refunded_amount')
                )['total'] or Decimal('0.00'),
                'average_payment': payments.filter(status='COMPLETED').aggregate(
                    avg=Avg('amount')
                )['avg'] or Decimal('0.00'),
                'payments_by_method': {},
                'payments_by_status': {}
            }
            
            # Pagos por método
            for method in Payment.PaymentMethod.choices:
                count = payments.filter(payment_method=method[0]).count()
                if count > 0:
                    stats['payments_by_method'][method[1]] = count
            
            # Pagos por estado
            for status_choice in Payment.Status.choices:
                count = payments.filter(status=status_choice[0]).count()
                if count > 0:
                    stats['payments_by_status'][status_choice[1]] = count
            
            serializer = PaymentStatisticsSerializer(stats)
            return Response(serializer.data)
        
        elif user.user_type == 'RESTAURANT':
            # Estadísticas del restaurante
            if not hasattr(user, 'restaurant_profile'):
                return Response(
                    {'error': 'Usuario no tiene restaurante asociado'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            restaurant = user.restaurant_profile
            payments = Payment.objects.filter(order__restaurant=restaurant)
            
            # Filtrar por rango de fechas
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            
            if date_from:
                payments = payments.filter(created_at__gte=date_from)
            if date_to:
                payments = payments.filter(created_at__lte=date_to)
            
            stats = {
                'total_payments': payments.count(),
                'completed_payments': payments.filter(status='COMPLETED').count(),
                'failed_payments': payments.filter(status='FAILED').count(),
                'total_amount': payments.filter(status='COMPLETED').aggregate(
                    total=Sum('amount')
                )['total'] or Decimal('0.00'),
                'total_refunded': payments.aggregate(
                    total=Sum('refunded_amount')
                )['total'] or Decimal('0.00'),
                'restaurant_earnings': payments.filter(status='COMPLETED').aggregate(
                    total=Sum('restaurant_amount')
                )['total'] or Decimal('0.00'),
                'platform_fees': payments.filter(status='COMPLETED').aggregate(
                    total=Sum('platform_fee')
                )['total'] or Decimal('0.00'),
                'average_payment': payments.filter(status='COMPLETED').aggregate(
                    avg=Avg('amount')
                )['avg'] or Decimal('0.00'),
                'payments_by_method': {},
                'payments_by_status': {}
            }
            
            # Pagos por método
            for method in Payment.PaymentMethod.choices:
                count = payments.filter(payment_method=method[0]).count()
                if count > 0:
                    stats['payments_by_method'][method[1]] = count
            
            # Pagos por estado
            for status_choice in Payment.Status.choices:
                count = payments.filter(status=status_choice[0]).count()
                if count > 0:
                    stats['payments_by_status'][status_choice[1]] = count
            
            serializer = PaymentStatisticsSerializer(stats)
            return Response(serializer.data)
        
        elif user.user_type == 'DRIVER':
            # Estadísticas del conductor
            payments = Payment.objects.filter(order__driver=user)
            
            stats = {
                'total_deliveries': payments.filter(status='COMPLETED').count(),
                'total_earnings': payments.filter(status='COMPLETED').aggregate(
                    total=Sum('driver_amount')
                )['total'] or Decimal('0.00'),
                'total_tips': payments.filter(status='COMPLETED').aggregate(
                    total=Sum('tip')
                )['total'] or Decimal('0.00'),
                'average_delivery_fee': payments.filter(status='COMPLETED').aggregate(
                    avg=Avg('delivery_fee')
                )['avg'] or Decimal('0.00'),
                'deliveries_today': payments.filter(
                    status='COMPLETED',
                    completed_at__date=timezone.now().date()
                ).count(),
                'earnings_today': payments.filter(
                    status='COMPLETED',
                    completed_at__date=timezone.now().date()
                ).aggregate(
                    total=Sum('driver_amount')
                )['total'] or Decimal('0.00')
            }
            
            return Response(stats)
        
        elif user.user_type == 'ADMIN':
            # Estadísticas generales de la plataforma
            payments = Payment.objects.all()
            
            # Filtrar por rango de fechas
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            
            if date_from:
                payments = payments.filter(created_at__gte=date_from)
            if date_to:
                payments = payments.filter(created_at__lte=date_to)
            
            stats = {
                'total_payments': payments.count(),
                'completed_payments': payments.filter(status='COMPLETED').count(),
                'pending_payments': payments.filter(status__in=['PENDING', 'PROCESSING']).count(),
                'failed_payments': payments.filter(status='FAILED').count(),
                'total_amount': payments.filter(status='COMPLETED').aggregate(
                    total=Sum('amount')
                )['total'] or Decimal('0.00'),
                'total_refunded': payments.aggregate(
                    total=Sum('refunded_amount')
                )['total'] or Decimal('0.00'),
                'average_payment': payments.filter(status='COMPLETED').aggregate(
                    avg=Avg('amount')
                )['avg'] or Decimal('0.00'),
                'platform_revenue': payments.filter(status='COMPLETED').aggregate(
                    total=Sum('platform_fee')
                )['total'] or Decimal('0.00'),
                'payments_by_method': {},
                'payments_by_status': {},
                'payments_today': payments.filter(
                    created_at__date=timezone.now().date()
                ).count(),
                'revenue_today': payments.filter(
                    created_at__date=timezone.now().date(),
                    status='COMPLETED'
                ).aggregate(
                    total=Sum('platform_fee')
                )['total'] or Decimal('0.00')
            }
            
            # Pagos por método
            for method in Payment.PaymentMethod.choices:
                count = payments.filter(payment_method=method[0]).count()
                if count > 0:
                    stats['payments_by_method'][method[1]] = count
            
            # Pagos por estado
            for status_choice in Payment.Status.choices:
                count = payments.filter(status=status_choice[0]).count()
                if count > 0:
                    stats['payments_by_status'][status_choice[1]] = count
            
            serializer = PaymentStatisticsSerializer(stats)
            return Response(serializer.data)
        
        return Response(
            {'error': 'Tipo de usuario no válido'},
            status=status.HTTP_400_BAD_REQUEST
        )


# ============================================================================
# VIEWSET DE PAYMENT METHODS
# ============================================================================

class PaymentMethodViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar métodos de pago guardados
    
    list: Listar métodos de pago del usuario
    retrieve: Detalle de un método de pago
    create: Agregar nuevo método de pago
    update: Actualizar método de pago
    destroy: Eliminar método de pago
    
    Acciones adicionales:
    - set_default: Establecer como método por defecto
    - deactivate: Desactivar método de pago
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentMethodSerializer
    
    def get_queryset(self):
        """Solo métodos de pago del usuario actual"""
        return PaymentMethod.objects.filter(
            user=self.request.user
        ).order_by('-is_default', '-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentMethodCreateSerializer
        return PaymentMethodSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_default(self, request, pk=None):
        """
        Establecer como método de pago por defecto
        """
        payment_method = self.get_object()
        
        # Quitar default de los demás
        PaymentMethod.objects.filter(
            user=request.user,
            is_default=True
        ).update(is_default=False)
        
        # Establecer este como default
        payment_method.is_default = True
        payment_method.save()
        
        serializer = PaymentMethodSerializer(payment_method)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def deactivate(self, request, pk=None):
        """
        Desactivar método de pago
        """
        payment_method = self.get_object()
        
        payment_method.is_active = False
        payment_method.save()
        
        serializer = PaymentMethodSerializer(payment_method)
        return Response(serializer.data)


# ============================================================================
# VIEWSET DE PAYOUTS
# ============================================================================

class PayoutViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar pagos salientes (payouts)
    
    list: Listar payouts
    retrieve: Detalle de un payout
    create: Crear nuevo payout (solo admin)
    
    Acciones adicionales:
    - complete: Marcar como completado (admin)
    - fail: Marcar como fallido (admin)
    - my_payouts: Payouts del usuario actual
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = PayoutSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'recipient_type']
    ordering_fields = ['created_at', 'amount', 'completed_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filtrar payouts según usuario"""
        user = self.request.user
        queryset = Payout.objects.select_related('recipient', 'processed_by')
        
        if user.user_type == 'ADMIN':
            # Admins ven todos
            return queryset
        else:
            # Usuarios ven solo sus payouts
            return queryset.filter(recipient=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PayoutCreateSerializer
        return PayoutSerializer
    
    def get_permissions(self):
        """Solo admins pueden crear payouts"""
        if self.action == 'create':
            return [IsAdminUser()]
        return super().get_permissions()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def complete(self, request, pk=None):
        """
        Marcar payout como completado (solo admin)
        """
        payout = self.get_object()
        
        try:
            payout.mark_as_completed()
            serializer = PayoutSerializer(payout)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def fail(self, request, pk=None):
        """
        Marcar payout como fallido (solo admin)
        """
        payout = self.get_object()
        
        message = request.data.get('message', 'Payout fallido')
        
        try:
            payout.mark_as_failed(message=message)
            serializer = PayoutSerializer(payout)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_payouts(self, request):
        """
        Obtener payouts del usuario actual
        """
        payouts = Payout.objects.filter(recipient=request.user)
        
        # Filtrar por estado
        status_filter = request.query_params.get('status')
        if status_filter:
            payouts = payouts.filter(status=status_filter)
        
        # Paginar
        page = self.paginate_queryset(payouts)
        if page is not None:
            serializer = PayoutSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PayoutSerializer(payouts, many=True)
        return Response(serializer.data)