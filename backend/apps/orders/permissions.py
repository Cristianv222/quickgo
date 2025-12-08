# apps/orders/permissions.py
from rest_framework import permissions


class IsOrderOwner(permissions.BasePermission):
    """
    Permiso para que solo el dueño del pedido pueda acceder
    """
    
    def has_object_permission(self, request, view, obj):
        # El cliente que hizo el pedido
        return obj.customer == request.user


class IsRestaurantOwner(permissions.BasePermission):
    """
    Permiso para que solo el restaurante del pedido pueda acceder
    """
    
    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'restaurant_profile'):
            return obj.restaurant == request.user.restaurant_profile
        return False


class IsDriverAssigned(permissions.BasePermission):
    """
    Permiso para que solo el conductor asignado pueda acceder
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.driver == request.user


class CanModifyOrder(permissions.BasePermission):
    """
    Permiso para modificar un pedido
    """
    
    def has_object_permission(self, request, view, obj):
        # Solo en estados tempranos
        if obj.status not in ['PENDING', 'CONFIRMED']:
            return False
        
        # Solo el cliente puede modificar
        return obj.customer == request.user