# apps/deliveries/filters.py
import django_filters
from .models import Delivery


class DeliveryFilter(django_filters.FilterSet):
    """Filtros personalizados para entregas"""
    
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
    
    # Filtro por múltiples estados
    status_in = django_filters.MultipleChoiceFilter(
        field_name='status',
        choices=Delivery.Status.choices,
        label='Estados'
    )
    
    # Filtros de prioridad
    min_priority = django_filters.NumberFilter(
        field_name='priority',
        lookup_expr='gte',
        label='Prioridad mínima'
    )
    
    # Filtro por retrasos
    is_delayed = django_filters.BooleanFilter(
        method='filter_delayed',
        label='Retrasado'
    )
    
    class Meta:
        model = Delivery
        fields = [
            'status',
            'driver',
            'priority',
            'delivery_attempts'
        ]
    
    def filter_delayed(self, queryset, name, value):
        """Filtrar entregas retrasadas"""
        from django.utils import timezone
        
        if value:
            return queryset.filter(
                estimated_delivery_time__lt=timezone.now()
            ).exclude(status__in=['DELIVERED', 'CANCELLED', 'FAILED'])
        return queryset