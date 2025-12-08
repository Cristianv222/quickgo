# apps/deliveries/permissions.py
from rest_framework import permissions


class IsDeliveryDriver(permissions.BasePermission):
    """
    Permiso que verifica que el usuario sea el conductor asignado a la entrega.
    Se usa a nivel de objeto para verificar que el conductor puede realizar
    acciones sobre entregas que le pertenecen.
    """
    
    def has_permission(self, request, view):
        """Verificar que el usuario está autenticado y es conductor"""
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'DRIVER'
        )
    
    def has_object_permission(self, request, view, obj):
        """
        Verificar que el conductor es el asignado a esta entrega específica.
        obj es una instancia de Delivery.
        """
        # Permitir si el usuario es el conductor asignado
        return obj.driver == request.user


class IsDeliveryParticipant(permissions.BasePermission):
    """
    Permiso que verifica que el usuario es un participante de la entrega:
    - El cliente que hizo el pedido
    - El restaurante que prepara el pedido
    - El conductor asignado
    - Un administrador
    
    Útil para acciones de lectura/tracking donde múltiples actores
    pueden ver la información de la entrega.
    """
    
    def has_permission(self, request, view):
        """Verificar que el usuario está autenticado"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Verificar que el usuario tiene relación con esta entrega.
        obj es una instancia de Delivery.
        """
        user = request.user
        
        # Administradores tienen acceso total
        if user.user_type == 'ADMIN':
            return True
        
        # Cliente que hizo el pedido
        if user.user_type == 'CUSTOMER' and obj.order.customer == user:
            return True
        
        # Restaurante que prepara el pedido
        if user.user_type == 'RESTAURANT':
            if hasattr(user, 'restaurant_profile'):
                if obj.order.restaurant == user.restaurant_profile:
                    return True
        
        # Conductor asignado
        if user.user_type == 'DRIVER' and obj.driver == user:
            return True
        
        return False


class CanCancelDelivery(permissions.BasePermission):
    """
    Permiso para verificar quién puede cancelar una entrega:
    - El conductor asignado
    - El restaurante del pedido
    - Un administrador
    """
    
    def has_permission(self, request, view):
        """Verificar que el usuario está autenticado"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Verificar que el usuario puede cancelar esta entrega.
        obj es una instancia de Delivery.
        """
        user = request.user
        
        # Administradores pueden cancelar
        if user.user_type == 'ADMIN':
            return True
        
        # Conductor asignado puede cancelar
        if obj.driver == user:
            return True
        
        # Restaurante puede cancelar
        if user.user_type == 'RESTAURANT':
            if hasattr(user, 'restaurant_profile'):
                if obj.order.restaurant == user.restaurant_profile:
                    return True
        
        return False


class IsDeliveryIssueParticipant(permissions.BasePermission):
    """
    Permiso para ver/crear issues de delivery.
    Permite acceso a:
    - Conductor de la entrega
    - Cliente del pedido
    - Restaurante del pedido
    - Usuario que reportó el issue
    - Administradores
    """
    
    def has_permission(self, request, view):
        """Verificar que el usuario está autenticado"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Verificar que el usuario tiene relación con este issue.
        obj es una instancia de DeliveryIssue.
        """
        user = request.user
        
        # Administradores tienen acceso total
        if user.user_type == 'ADMIN':
            return True
        
        # Usuario que reportó el issue
        if obj.reported_by == user:
            return True
        
        # Conductor de la entrega
        if obj.delivery.driver == user:
            return True
        
        # Cliente del pedido
        if obj.delivery.order.customer == user:
            return True
        
        # Restaurante del pedido
        if user.user_type == 'RESTAURANT':
            if hasattr(user, 'restaurant_profile'):
                if obj.delivery.order.restaurant == user.restaurant_profile:
                    return True
        
        return False