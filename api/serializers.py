from rest_framework import serializers
from catalog.models import (
    Material, Technology, 
    Category, Product, ProductImage
)
from orders.models import Order, OrderItem
from djmoney.money import Money

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'name', 'description', 'colors']

class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ['id', 'name', 'description']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ProductListSerializer(serializers.ModelSerializer):
    """Simplified serializer for product listings"""
    category = CategorySerializer()
    main_image = ProductImageSerializer()

    # Custom method to serialize Money fields
    def get_money_field(self, obj, field_name):
        money_obj = getattr(obj, field_name)
        if isinstance(money_obj, Money):
            return {'amount': str(money_obj.amount), 'currency': str(money_obj.currency)}
        return None

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

    def get_base_price(self, obj):
        return self.get_money_field(obj, 'base_price')

    def get_discount_price(self, obj):
        return self.get_money_field(obj, 'discount_price')

    def get_current_price(self, obj):
        return self.get_money_field(obj, 'current_price')

class ProductDetailSerializer(ProductListSerializer):
    """Comprehensive serializer for product details"""
    all_images = ProductImageSerializer(many=True)
    related_products = serializers.SerializerMethodField()

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + [
            'description', 'stl_file', 
            'all_images', 'related_products'
        ]

    def get_related_products(self, obj):
        related = Product.get_related_products(obj)
        return ProductListSerializer(related, many=True).data

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False, allow_null=True)
    material = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all(), required=False, allow_null=True)
    technology = serializers.PrimaryKeyRelatedField(queryset=Technology.objects.all(), required=False, allow_null=True)

    class Meta:
        model = OrderItem
        exclude = ['order']  # We set 'order' manually in OrderSerializer.create



class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])  # Get the items data from validated data

        # Create the order object
        order = Order.objects.create(**validated_data)

        # Create order items and associate them with the order
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        # After creating the items, calculate the total cost
        order.calculate_total_cost()

        return order
    def update(self, instance, validated_data):
        # First update the fields that are not nested
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.telegram_nick = validated_data.get('telegram_nick', instance.telegram_nick)
        instance.address = validated_data.get('address', instance.address)
        instance.postal_code = validated_data.get('postal_code', instance.postal_code)
        instance.city = validated_data.get('city', instance.city)

        # Save the instance after updating top-level fields
        instance.save()

        # Now update the nested `items` (OrderItem)
        items_data = validated_data.get('items', [])
        for item_data in items_data:
            # Try to get the corresponding OrderItem instance
            item_id = item_data.get('id')
            if item_id:
                item_instance = OrderItem.objects.get(id=item_id, order=instance)
                item_instance.price = item_data.get('price', item_instance.price)
                item_instance.quantity = item_data.get('quantity', item_instance.quantity)
                item_instance.postprocessing = item_data.get('postprocessing', item_instance.postprocessing)
                item_instance.order_name = item_data.get('order_name', item_instance.order_name)
                item_instance.save()
            else:
                # If no item_id is provided, create new OrderItem (optional)
                OrderItem.objects.create(order=instance, **item_data)

        return instance