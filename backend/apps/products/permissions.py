# apps/products/permissions.py
from rest_framework import permissions


class IsRestaurantOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo al propietario del restaurante
    modificar sus productos.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permitir lectura a todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permitir escritura solo al propietario del restaurante
        return obj.restaurant.user == request.user


class IsReviewAuthorOrReadOnly(permissions.BasePermission):
    """
    Permiso para que solo el autor pueda modificar su reseña
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.customer == request.user