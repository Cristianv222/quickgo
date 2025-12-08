from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet, RestaurantReviewViewSet

router = DefaultRouter()
router.register(r'', RestaurantViewSet, basename='restaurant')
router.register(r'reviews', RestaurantReviewViewSet, basename='restaurant-review')

urlpatterns = [
    path('', include(router.urls)),
]