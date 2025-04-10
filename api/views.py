from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from catalog.models import (
    Material, Technology, 
    Category, Product
)
from orders.models import Order, OrderItem
from .serializers import (
    MaterialSerializer, 
    TechnologySerializer, CategorySerializer, 
    ProductListSerializer, ProductDetailSerializer,
    OrderSerializer, OrderItemSerializer
)
from django.core.cache import cache

class MaterialViewSet(viewsets.ModelViewSet):
    """
    API endpoint for materials
    """
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [permissions.IsAuthenticated]

class TechnologyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for technologies
    """
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    permission_classes = [permissions.IsAuthenticated]

class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for product categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """
        List products for a specific category
        """
        category = self.get_object()
        products = Product.objects.filter(category=category)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for products
    """
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """
        Different serializers for list and retrieve actions
        """
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Filter products by category slug
        """
        category_slug = request.query_params.get('category', None)
        if category_slug:
            products = Product.objects.filter(category__slug=category_slug)
            serializer = ProductListSerializer(products, many=True)
            return Response(serializer.data)
        return Response({'error': 'Category slug is required'}, status=400)

    def list(self, request, *args, **kwargs):
        cache_key = 'products_list'
        products = cache.get(cache_key)
        if not products:
            print("Cache is empty, retrieving data from the database.")
            response = super().list(request, *args, **kwargs)
            products = response.data 
            cache.set(cache_key, products, timeout=60*15) 
        else:
            print("Data retrived from cache.")
        return Response(products)  

class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for orders
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        cache_key = 'orders_list'
        orders = cache.get(cache_key)
        if not orders:
            print("Cache is empty, retrieving data from the database.")
            response = super().list(request, *args, **kwargs)
            orders = response.data  # Get the data from the response
            cache.set(cache_key, orders, timeout=60*15)  # Cache only the data
        else:
            print("Data retrieved from cache.")
        return Response(orders)  # Return a new Response object with cached data

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """
        Get all items for a specific order
        """
        order = self.get_object()
        items = order.items.all()
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """
        Mark an order as paid
        """
        order = self.get_object()
        order.paid = True
        order.save()
        return Response({'status': 'order marked as paid'})

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update order status
        """
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status:
            order.status = new_status
            order.save()
            return Response({'status': 'order status updated'})
        return Response({'error': 'status is required'}, status=400)

    @action(detail=True, methods=['post'])
    def update_tracking(self, request, pk=None):
        """
        Update order tracking number
        """
        order = self.get_object()
        tracking_number = request.data.get('tracking_number')
        if tracking_number:
            order.tracking_number = tracking_number
            order.save()
            return Response({'status': 'tracking number updated'})
        return Response({'error': 'tracking number is required'}, status=400)

class OrderItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for order items
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Create order item and update order total cost
        """
        order_item = serializer.save()
        order_item.order.calculate_total_cost()

    def perform_update(self, serializer):
        """
        Update order item and update order total cost
        """
        order_item = serializer.save()
        order_item.order.calculate_total_cost()

    def perform_destroy(self, instance):
        """
        Delete order item and update order total cost
        """
        order = instance.order
        instance.delete()
        order.calculate_total_cost()