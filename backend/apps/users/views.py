from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .models import Customer, Driver
from .serializers import (
    UserSerializer,
    CustomerSerializer,
    CustomerRegistrationSerializer,
    DriverSerializer,
    DriverRegistrationSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    UpdateProfileSerializer,
    UpdateCustomerAddressSerializer,
    UpdateDriverLocationSerializer
)

User = get_user_model()


# ========================================
# AUTHENTICATION VIEWS
# ========================================

class CustomerRegistrationView(APIView):
    """
    Vista para registro de clientes
    POST /api/auth/register/customer/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            
            # Generar tokens JWT
            refresh = RefreshToken.for_user(customer.user)
            
            return Response({
                'message': '¡Registro exitoso! Bienvenido a QuickGo.',
                'user': UserSerializer(customer.user).data,
                'customer': CustomerSerializer(customer).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DriverRegistrationView(APIView):
    """
    Vista para registro de conductores
    POST /api/auth/register/driver/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = DriverRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            driver = serializer.save()
            
            # Generar tokens JWT
            refresh = RefreshToken.for_user(driver.user)
            
            return Response({
                'message': '¡Registro exitoso! Tu solicitud está pendiente de aprobación.',
                'user': UserSerializer(driver.user).data,
                'driver': DriverSerializer(driver).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Vista para login
    POST /api/auth/login/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            
            # Preparar respuesta según tipo de usuario
            response_data = {
                'message': f'¡Bienvenido {user.get_full_name()}!',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }
            
            # Agregar datos adicionales según el tipo de usuario
            if user.user_type == 'CUSTOMER':
                try:
                    customer = Customer.objects.get(user=user)
                    response_data['customer'] = CustomerSerializer(customer).data
                except Customer.DoesNotExist:
                    pass
            
            elif user.user_type == 'DRIVER':
                try:
                    driver = Driver.objects.get(user=user)
                    response_data['driver'] = DriverSerializer(driver).data
                except Driver.DoesNotExist:
                    pass
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Vista para logout (blacklist del refresh token)
    POST /api/auth/logout/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Se requiere el refresh token.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {'message': 'Sesión cerrada exitosamente.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': 'Token inválido o expirado.'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ========================================
# USER PROFILE VIEWS
# ========================================

class UserProfileView(APIView):
    """
    Vista para obtener perfil del usuario autenticado
    GET /api/users/profile/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        response_data = {
            'user': UserSerializer(user).data
        }
        
        # Agregar datos adicionales según el tipo de usuario
        if user.user_type == 'CUSTOMER':
            try:
                customer = Customer.objects.get(user=user)
                response_data['customer'] = CustomerSerializer(customer).data
            except Customer.DoesNotExist:
                pass
        
        elif user.user_type == 'DRIVER':
            try:
                driver = Driver.objects.get(user=user)
                response_data['driver'] = DriverSerializer(driver).data
            except Driver.DoesNotExist:
                pass
        
        return Response(response_data, status=status.HTTP_200_OK)


class UpdateProfileView(APIView):
    """
    Vista para actualizar perfil del usuario
    PUT /api/users/profile/update/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Perfil actualizado exitosamente.',
                'user': UserSerializer(request.user).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    Vista para cambiar contraseña
    POST /api/users/change-password/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Contraseña actualizada exitosamente.'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ========================================
# CUSTOMER VIEWS
# ========================================

class UpdateCustomerAddressView(APIView):
    """
    Vista para actualizar dirección del cliente
    PUT /api/customers/address/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request):
        if request.user.user_type != 'CUSTOMER':
            return Response(
                {'error': 'Solo los clientes pueden actualizar direcciones.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Perfil de cliente no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UpdateCustomerAddressSerializer(
            customer,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Dirección actualizada exitosamente.',
                'customer': CustomerSerializer(customer).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ========================================
# DRIVER VIEWS
# ========================================

class DriverStatusView(APIView):
    """
    Vista para obtener el estado del conductor
    GET /api/drivers/status/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.user_type != 'DRIVER':
            return Response(
                {'error': 'Solo los conductores pueden acceder a esta información.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            driver = Driver.objects.get(user=request.user)
            return Response({
                'status': driver.status,
                'is_available': driver.is_available,
                'is_online': driver.is_online,
                'rating': float(driver.rating),
                'total_deliveries': driver.total_deliveries,
                'total_earnings': float(driver.total_earnings)
            }, status=status.HTTP_200_OK)
        except Driver.DoesNotExist:
            return Response(
                {'error': 'Perfil de conductor no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )


class UpdateDriverLocationView(APIView):
    """
    Vista para actualizar ubicación del conductor
    POST /api/drivers/location/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if request.user.user_type != 'DRIVER':
            return Response(
                {'error': 'Solo los conductores pueden actualizar su ubicación.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            driver = Driver.objects.get(user=request.user)
        except Driver.DoesNotExist:
            return Response(
                {'error': 'Perfil de conductor no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UpdateDriverLocationSerializer(
            driver,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Ubicación actualizada exitosamente.',
                'latitude': float(driver.current_latitude) if driver.current_latitude else None,
                'longitude': float(driver.current_longitude) if driver.current_longitude else None,
                'is_online': driver.is_online
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ToggleDriverAvailabilityView(APIView):
    """
    Vista para activar/desactivar disponibilidad del conductor
    POST /api/drivers/toggle-availability/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if request.user.user_type != 'DRIVER':
            return Response(
                {'error': 'Solo los conductores pueden cambiar su disponibilidad.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            driver = Driver.objects.get(user=request.user)
        except Driver.DoesNotExist:
            return Response(
                {'error': 'Perfil de conductor no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que el conductor esté aprobado
        if driver.status != 'APPROVED':
            return Response(
                {'error': f'No puedes cambiar tu disponibilidad. Estado actual: {driver.get_status_display()}'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Toggle disponibilidad
        driver.is_available = not driver.is_available
        if not driver.is_available:
            driver.is_online = False
        driver.save()
        
        return Response({
            'message': f'Disponibilidad {"activada" if driver.is_available else "desactivada"} exitosamente.',
            'is_available': driver.is_available,
            'is_online': driver.is_online
        }, status=status.HTTP_200_OK)


class UploadDriverDocumentsView(APIView):
    """
    Vista para subir documentos del conductor
    POST /api/drivers/upload-documents/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if request.user.user_type != 'DRIVER':
            return Response(
                {'error': 'Solo los conductores pueden subir documentos.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            driver = Driver.objects.get(user=request.user)
        except Driver.DoesNotExist:
            return Response(
                {'error': 'Perfil de conductor no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Actualizar documentos si se proporcionan
        if 'license_photo' in request.FILES:
            driver.license_photo = request.FILES['license_photo']
        
        if 'vehicle_photo' in request.FILES:
            driver.vehicle_photo = request.FILES['vehicle_photo']
        
        if 'id_photo' in request.FILES:
            driver.id_photo = request.FILES['id_photo']
        
        driver.save()
        
        return Response({
            'message': 'Documentos subidos exitosamente.',
            'driver': DriverSerializer(driver).data
        }, status=status.HTTP_200_OK)