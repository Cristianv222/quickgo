from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PaymentViewSet,
    PaymentMethodViewSet,
    PayoutViewSet
)

app_name = 'payments'

# Router para ViewSets
router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'payment-methods', PaymentMethodViewSet, basename='paymentmethod')
router.register(r'payouts', PayoutViewSet, basename='payout')

urlpatterns = [
    # Incluir las rutas del router
    path('', include(router.urls)),
]