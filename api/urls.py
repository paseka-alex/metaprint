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

app_name = 'api'

# Configure API schema view
schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation MetaPrint",
        default_version="v1",
        description="API documentation for the MetaPrint DB project",
    ),
    permission_classes=(permissions.IsAuthenticated,),
    public=False,
    authentication_classes=(SessionAuthentication,),

)

# Define router
router = SimpleRouter()
router.register(r'materials', MaterialViewSet)
router.register(r'technologies', TechnologyViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='order-item')

urlpatterns = [
    path('', include(router.urls)),
    path('docs/', login_required(schema_view.with_ui('redoc', cache_timeout=None)), name='schema-redoc'),
]
