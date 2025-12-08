# apps/products/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ProductViewSet,
    ProductReviewViewSet,
    ProductTagViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'reviews', ProductReviewViewSet, basename='review')
router.register(r'tags', ProductTagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls)),
]