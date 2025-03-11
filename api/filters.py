import django_filters
from .models import Package, Category


class PackageFilter(django_filters.FilterSet):
    categories = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all())
    price_min = django_filters.NumberFilter(
        field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(
        field_name="price", lookup_expr="lte")

    class Meta:
        model = Package
        fields = ['categories', 'price_min', 'price_max']
