# apps/deliveries/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeliveryViewSet, DeliveryIssueViewSet

router = DefaultRouter()
router.register(r'deliveries', DeliveryViewSet, basename='delivery')
router.register(r'issues', DeliveryIssueViewSet, basename='delivery-issue')

urlpatterns = [
    path('', include(router.urls)),
]