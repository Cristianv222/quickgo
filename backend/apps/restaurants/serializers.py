from rest_framework import serializers
from django.db.models import Avg, Q
from django.utils import timezone
from .models import (
    Restaurant, RestaurantSchedule, RestaurantReview, 
    RestaurantGallery
)


class RestaurantScheduleSerializer(serializers.ModelSerializer):
    """Serializer para horarios del restaurante"""
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = RestaurantSchedule
        fields = [
            'id', 'day_of_week', 'day_name', 'opening_time', 
            'closing_time', 'is_closed'
        ]


class RestaurantGallerySerializer(serializers.ModelSerializer):
    """Serializer para galería de fotos"""
    
    class Meta:
        model = RestaurantGallery
        fields = ['id', 'image', 'caption', 'is_featured', 'order']


class RestaurantReviewSerializer(serializers.ModelSerializer):
    """Serializer para reseñas"""
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    customer_avatar = serializers.ImageField(source='customer.avatar', read_only=True)
    
    class Meta:
        model = RestaurantReview
        fields = [
            'id', 'customer_name', 'customer_avatar', 'rating',
            'comment', 'food_quality', 'delivery_time', 'packaging',
            'restaurant_response', 'response_date', 'created_at'
        ]
        read_only_fields = ['customer_name', 'customer_avatar', 'created_at']


class RestaurantListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listado de restaurantes (card view)"""
    cuisine_name = serializers.CharField(source='get_cuisine_type_display', read_only=True)
    distance = serializers.SerializerMethodField()
    is_open_now = serializers.SerializerMethodField()
    
    class Meta:
        model = Restaurant
        fields = [
            'id', 'slug', 'name', 'logo', 'cuisine_type', 'cuisine_name',
            'rating', 'total_reviews', 'delivery_time_min', 'delivery_time_max',
            'delivery_fee', 'min_order_amount', 'free_delivery_above',
            'is_open', 'is_open_now', 'is_accepting_orders', 'is_featured',
            'is_new', 'has_promotion', 'promotion_text', 'distance'
        ]
    
    def get_distance(self, obj):
        """Calcula distancia desde ubicación del usuario"""
        request = self.context.get('request')
        if request and hasattr(request, 'user_location'):
            user_lat = request.user_location.get('latitude')
            user_lon = request.user_location.get('longitude')
            if user_lat and user_lon:
                return self._calculate_distance(
                    float(obj.latitude), float(obj.longitude),
                    float(user_lat), float(user_lon)
                )
        return None
    
    def get_is_open_now(self, obj):
        """Verifica si el restaurante está abierto ahora"""
        now = timezone.localtime()
        current_day = now.isoweekday()
        current_time = now.time()
        
        schedule = obj.schedules.filter(day_of_week=current_day).first()
        if not schedule or schedule.is_closed:
            return False
        
        return schedule.opening_time <= current_time <= schedule.closing_time
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calcula distancia en km usando fórmula de Haversine"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Radio de la Tierra en km
        
        lat1, lon1 = radians(lat1), radians(lon1)
        lat2, lon2 = radians(lat2), radians(lon2)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        return round(distance, 2)


class RestaurantDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle de restaurante"""
    cuisine_name = serializers.CharField(source='get_cuisine_type_display', read_only=True)
    schedules = RestaurantScheduleSerializer(many=True, read_only=True)
    gallery = RestaurantGallerySerializer(many=True, read_only=True)
    recent_reviews = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    is_open_now = serializers.SerializerMethodField()
    average_ratings = serializers.SerializerMethodField()
    
    class Meta:
        model = Restaurant
        fields = [
            'id', 'slug', 'name', 'description', 'logo', 'banner',
            'cuisine_type', 'cuisine_name', 'phone', 'email',
            'address', 'address_reference', 'latitude', 'longitude',
            'rating', 'total_reviews', 'total_orders',
            'delivery_time_min', 'delivery_time_max', 'delivery_fee',
            'min_order_amount', 'free_delivery_above', 'delivery_radius_km',
            'is_open', 'is_open_now', 'is_accepting_orders',
            'is_featured', 'is_new', 'has_promotion', 'promotion_text',
            'accepts_cash', 'accepts_card', 'has_parking', 'has_wifi',
            'is_eco_friendly', 'schedules', 'gallery', 'recent_reviews',
            'distance', 'average_ratings', 'created_at'
        ]
    
    def get_recent_reviews(self, obj):
        """Obtiene las últimas 5 reseñas"""
        reviews = obj.reviews.filter(is_visible=True).order_by('-created_at')[:5]
        return RestaurantReviewSerializer(reviews, many=True).data
    
    def get_distance(self, obj):
        """Calcula distancia desde ubicación del usuario"""
        request = self.context.get('request')
        if request and hasattr(request, 'user_location'):
            user_lat = request.user_location.get('latitude')
            user_lon = request.user_location.get('longitude')
            if user_lat and user_lon:
                return self._calculate_distance(
                    float(obj.latitude), float(obj.longitude),
                    float(user_lat), float(user_lon)
                )
        return None
    
    def get_is_open_now(self, obj):
        """Verifica si el restaurante está abierto ahora"""
        now = timezone.localtime()
        current_day = now.isoweekday()
        current_time = now.time()
        
        schedule = obj.schedules.filter(day_of_week=current_day).first()
        if not schedule or schedule.is_closed:
            return False
        
        return schedule.opening_time <= current_time <= schedule.closing_time
    
    def get_average_ratings(self, obj):
        """Calcula promedios de ratings específicos"""
        reviews = obj.reviews.filter(is_visible=True)
        if not reviews.exists():
            return None
        
        return {
            'food_quality': round(reviews.aggregate(Avg('food_quality'))['food_quality__avg'] or 0, 1),
            'delivery_time': round(reviews.aggregate(Avg('delivery_time'))['delivery_time__avg'] or 0, 1),
            'packaging': round(reviews.aggregate(Avg('packaging'))['packaging__avg'] or 0, 1),
        }
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calcula distancia en km"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371
        lat1, lon1 = radians(lat1), radians(lon1)
        lat2, lon2 = radians(lat2), radians(lon2)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return round(R * c, 2)


class RestaurantCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar restaurante"""
    
    class Meta:
        model = Restaurant
        fields = [
            'name', 'description', 'logo', 'banner', 'cuisine_type',
            'phone', 'email', 'address', 'address_reference',
            'latitude', 'longitude', 'ruc', 'business_license',
            'health_permit', 'delivery_time_min', 'delivery_time_max',
            'delivery_fee', 'min_order_amount', 'free_delivery_above',
            'delivery_radius_km', 'accepts_cash', 'accepts_card',
            'has_parking', 'has_wifi', 'is_eco_friendly'
        ]
    
    def validate_ruc(self, value):
        """Valida que el RUC sea único"""
        restaurant_id = self.instance.id if self.instance else None
        if Restaurant.objects.filter(ruc=value).exclude(id=restaurant_id).exists():
            raise serializers.ValidationError("Este RUC ya está registrado.")
        return value
    
    def validate(self, data):
        """Validaciones generales"""
        if data.get('delivery_time_max') and data.get('delivery_time_min'):
            if data['delivery_time_max'] < data['delivery_time_min']:
                raise serializers.ValidationError({
                    'delivery_time_max': 'El tiempo máximo debe ser mayor al mínimo.'
                })
        
        if data.get('free_delivery_above') and data.get('min_order_amount'):
            if data['free_delivery_above'] < data['min_order_amount']:
                raise serializers.ValidationError({
                    'free_delivery_above': 'El monto para envío gratis debe ser mayor al pedido mínimo.'
                })
        
        return data


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear reseñas"""
    
    class Meta:
        model = RestaurantReview
        fields = [
            'restaurant', 'rating', 'comment', 'food_quality',
            'delivery_time', 'packaging', 'order'
        ]
    
    def validate(self, data):
        """Valida que el usuario haya realizado el pedido"""
        request = self.context.get('request')
        order = data.get('order')
        
        if order and order.customer != request.user:
            raise serializers.ValidationError({
                'order': 'No puedes calificar un pedido que no es tuyo.'
            })
        
        # Verifica que no haya calificado antes
        if RestaurantReview.objects.filter(
            restaurant=data['restaurant'],
            customer=request.user,
            order=order
        ).exists():
            raise serializers.ValidationError({
                'restaurant': 'Ya has calificado este pedido.'
            })
        
        return data
    
    def create(self, validated_data):
        """Crea la reseña y marca como verificada si hay pedido"""
        validated_data['customer'] = self.context['request'].user
        if validated_data.get('order'):
            validated_data['is_verified'] = True
        return super().create(validated_data)