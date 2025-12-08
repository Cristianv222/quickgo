# apps/products/filters.py
import django_filters
from .models import Product
from decimal import Decimal


class ProductFilter(django_filters.FilterSet):
    """Filtros personalizados para productos"""
    
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.NumberFilter(field_name='category__id')
    restaurant = django_filters.NumberFilter(field_name='restaurant__id')
    tags = django_filters.CharFilter(method='filter_by_tags')
    has_discount = django_filters.BooleanFilter(method='filter_has_discount')
    
    class Meta:
        model = Product
        fields = [
            'restaurant',
            'category',
            'is_featured',
            'is_new',
            'is_popular',
            'is_available',
            'min_price',
            'max_price',
            'tags',
            'has_discount'
        ]
    
    def filter_by_tags(self, queryset, name, value):
        """Filtrar por múltiples tags (IDs separados por coma)"""
        tag_ids = value.split(',')
        return queryset.filter(tags__id__in=tag_ids).distinct()
    
    def filter_has_discount(self, queryset, name, value):
        """Filtrar productos con descuento"""
        if value:
            return queryset.filter(compare_price__isnull=False).exclude(compare_price=Decimal('0.00'))
        return queryset.filter(compare_price__isnull=True) | queryset.filter(compare_price=Decimal('0.00'))