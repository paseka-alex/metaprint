from django_filters import rest_framework as filters
from catalog.models import Product

class ProductFilter(filters.FilterSet):
    """
    Advanced filtering for products
    """
    name = filters.CharFilter(lookup_expr='icontains')
    min_price = filters.NumberFilter(field_name='base_price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='base_price', lookup_expr='lte')
    category = filters.CharFilter(field_name='category__slug')
    has_discount = filters.BooleanFilter(method='filter_has_discount')

    class Meta:
        model = Product
        fields = ['name', 'min_price', 'max_price', 'category', 'has_discount']

    def filter_has_discount(self, queryset, name, value):
        if value:
            return queryset.filter(discount_price__isnull=False)
        return queryset