from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet, RestaurantReviewViewSet

router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet, basename='restaurant')
router.register(r'restaurant-reviews', RestaurantReviewViewSet, basename='restaurant-review')

urlpatterns = [
    path('', include(router.urls)),
]