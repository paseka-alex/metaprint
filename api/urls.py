from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import SimpleRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth.decorators import login_required

from .views import (
    MaterialViewSet, 
    TechnologyViewSet, CategoryViewSet, 
    ProductViewSet, OrderViewSet, OrderItemViewSet
)

# Set the application namespace
app_name = 'api'

# Configure API schema view for documentation using drf-yasg
schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation MetaPrint",  # Title of the API docs
        default_version="v1.2",               # Version number
        description="API documentation for the MetaPrint DB project",  # Description
    ),
    permission_classes=(permissions.IsAuthenticated,),   # Require user to be authenticated
    public=False,                                         # Documentation is not public
    authentication_classes=(SessionAuthentication,),     # Use session authentication
)

# Initialize the router for automatically generating API routes
router = SimpleRouter()

# Register viewsets with the router to create endpoints
router.register(r'materials', MaterialViewSet)                # /materials/
router.register(r'technologies', TechnologyViewSet)           # /technologies/
router.register(r'categories', CategoryViewSet)               # /categories/
router.register(r'products', ProductViewSet)                  # /products/
router.register(r'orders', OrderViewSet, basename='order')    # /orders/
router.register(r'order-items', OrderItemViewSet, basename='order-item')  # /order-items/

# Define the URL patterns for the API
urlpatterns = [
    path('', include(router.urls)),  # Include all routes registered by the router
    path(
        'docs/',
        login_required(schema_view.with_ui('redoc', cache_timeout=None)),  # Redoc UI for docs (login required)
        name='schema-redoc'
    ),
]
