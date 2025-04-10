from rest_framework import serializers
from catalog.models import (
    Material, Technology, 
    Category, Product, ProductImage
)
from orders.models import Order, OrderItem
from djmoney.money import Money

# Serializer for Material model
class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'name', 'description', 'colors']

# Serializer for Technology model
class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ['id', 'name', 'description']

# Serializer for ProductImage model
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text']

# Serializer for Category model
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

# Serializer for listing products in a simplified way
class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer()               # Nested category serializer
    main_image = ProductImageSerializer()         # Main image for quick display

    # Custom money serialization
    def get_money_field(self, obj, field_name):
        money_obj = getattr(obj, field_name)
        if isinstance(money_obj, Money):
            return {
                'amount': str(money_obj.amount),
                'currency': str(money_obj.currency)
            }
        return None

    # Method fields for price values
    base_price = serializers.SerializerMethodField()
    discount_price = serializers.SerializerMethodField()
    current_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category',
            'base_price', 'base_price_currency', 'discount_price', 'discount_price_currency',
            'current_price', 'discount_percentage',
            'main_image'
        ]

    # Serialize money fields using helper method
    def get_base_price(self, obj):
        return self.get_money_field(obj, 'base_price')

    def get_discount_price(self, obj):
        return self.get_money_field(obj, 'discount_price')

    def get_current_price(self, obj):
        return self.get_money_field(obj, 'current_price')

# Serializer for detailed product view (extends ProductListSerializer)
class ProductDetailSerializer(ProductListSerializer):
    all_images = ProductImageSerializer(many=True)                  # All product images
    related_products = serializers.SerializerMethodField()          # Dynamically get related products

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + [
            'description', 'stl_file', 
            'all_images', 'related_products'
        ]

    # Get related products using model method
    def get_related_products(self, obj):
        related = Product.get_related_products(obj)
        return ProductListSerializer(related, many=True).data

# Serializer for individual order items
class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False, allow_null=True)
    material = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all(), required=False, allow_null=True)
    technology = serializers.PrimaryKeyRelatedField(queryset=Technology.objects.all(), required=False, allow_null=True)

    class Meta:
        model = OrderItem
        exclude = ['order']  # 'order' will be manually assigned in OrderSerializer.create

# Serializer for complete Order object with nested items
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)  # Nested serializer for order items

    class Meta:
        model = Order
        fields = '__all__'

    # Custom create method to handle nested order items
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])  # Extract items from data

        # Create the order
        order = Order.objects.create(**validated_data)

        # Create each order item and associate with the order
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        # Calculate total cost after adding items
        order.calculate_total_cost()

        return order

    # Custom update method to handle both order fields and nested items
    def update(self, instance, validated_data):
        # Update basic order fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.telegram_nick = validated_data.get('telegram_nick', instance.telegram_nick)
        instance.address = validated_data.get('address', instance.address)
        instance.postal_code = validated_data.get('postal_code', instance.postal_code)
        instance.city = validated_data.get('city', instance.city)
        instance.save()

        # Handle order items
        items_data = validated_data.get('items', [])
        for item_data in items_data:
            item_id = item_data.get('id')
            if item_id:
                # Update existing item
                item_instance = OrderItem.objects.get(id=item_id, order=instance)
                item_instance.price = item_data.get('price', item_instance.price)
                item_instance.quantity = item_data.get('quantity', item_instance.quantity)
                item_instance.postprocessing = item_data.get('postprocessing', item_instance.postprocessing)
                item_instance.order_name = item_data.get('order_name', item_instance.order_name)
                item_instance.save()
            else:
                # Optionally create a new item if ID not provided
                OrderItem.objects.create(order=instance, **item_data)

        return instance
