"""
URL configuration for auth_service project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Home
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # OAuth2
    path('oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    
    # Apps
    path('api/accounts/', include('accounts.urls')),
    path('api/permissions/', include('permissions_system.urls')),
]
