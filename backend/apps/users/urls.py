from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    # Authentication
    CustomerRegistrationView,
    DriverRegistrationView,
    LoginView,
    LogoutView,
    
    # User Profile
    UserProfileView,
    UpdateProfileView,
    ChangePasswordView,
    
    # Customer
    UpdateCustomerAddressView,
    
    # Driver
    DriverStatusView,
    UpdateDriverLocationView,
    ToggleDriverAvailabilityView,
    UploadDriverDocumentsView,
)

app_name = 'users'

urlpatterns = [
    # ========================================
    # AUTHENTICATION ENDPOINTS
    # ========================================
    path('register/customer/', CustomerRegistrationView.as_view(), name='register-customer'),
    path('register/driver/', DriverRegistrationView.as_view(), name='register-driver'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # ========================================
    # USER PROFILE ENDPOINTS
    # ========================================
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # ========================================
    # CUSTOMER ENDPOINTS
    # ========================================
    path('customers/address/', UpdateCustomerAddressView.as_view(), name='update-customer-address'),
    
    # ========================================
    # DRIVER ENDPOINTS
    # ========================================
    path('drivers/status/', DriverStatusView.as_view(), name='driver-status'),
    path('drivers/location/', UpdateDriverLocationView.as_view(), name='update-driver-location'),
    path('drivers/toggle-availability/', ToggleDriverAvailabilityView.as_view(), name='toggle-driver-availability'),
    path('drivers/upload-documents/', UploadDriverDocumentsView.as_view(), name='upload-driver-documents'),
]