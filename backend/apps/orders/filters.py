# apps/orders/filters.py
import django_filters
from .models import Order
from django.db.models import Q


class OrderFilter(django_filters.FilterSet):
    """Filtros personalizados para pedidos"""
    
    # Filtros por fecha
    date_from = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Fecha desde'
    )
    date_to = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Fecha hasta'
    )
    
    # Filtros por monto
    min_total = django_filters.NumberFilter(
        field_name='total',
        lookup_expr='gte',
        label='Total mínimo'
    )
    max_total = django_filters.NumberFilter(
        field_name='total',
        lookup_expr='lte',
        label='Total máximo'
    )
    
    # Filtro por múltiples estados
    status_in = django_filters.MultipleChoiceFilter(
        field_name='status',
        choices=Order.Status.choices,
        label='Estados'
    )
    
    # Filtro por pago
    is_paid = django_filters.BooleanFilter(
        field_name='is_paid',
        label='Pagado'
    )
    
    # Filtro por calificación
    is_rated = django_filters.BooleanFilter(
        field_name='is_rated',
        label='Calificado'
    )
    
    # Filtro de búsqueda en múltiples campos
    search = django_filters.CharFilter(
        method='filter_search',
        label='Búsqueda'
    )
    
    class Meta:
        model = Order
        fields = [
            'status',
            'payment_method',
            'is_paid',
            'is_rated',
            'customer',
            'restaurant',
            'driver'
        ]
    
    def filter_search(self, queryset, name, value):
        """Búsqueda en múltiples campos"""
        return queryset.filter(
            Q(order_number__icontains=value) |
            Q(customer__first_name__icontains=value) |
            Q(customer__last_name__icontains=value) |
            Q(customer__email__icontains=value) |
            Q(restaurant__name__icontains=value) |
            Q(delivery_address__icontains=value)
        )