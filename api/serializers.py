from rest_framework import serializers
from .models import Category, Package, Product, Cart, CartItem


class PackageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    categories = serializers.StringRelatedField(many=True)

    def get_image_url(self, obj):
        return obj.image.url

    class Meta:
        model = Package
        fields = ['id', 'title', 'categories',
                  'description', 'price', 'image_url']


class CategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    packages = PackageSerializer(many=True, read_only=True)

    def get_image_url(self, obj):
        return obj.image.url

    class Meta:
        model = Category
        fields = ['id', 'name', 'image_url', 'description', 'packages']


class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        return obj.image.url

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price',
                  'image_url', 'get_content_type_id']


class CartItemSerializer(serializers.ModelSerializer):
    item_data = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'content_type', 'object_id',
                  'item_data', 'quantity', 'subtotal', 'created_at', 'updated_at']

    def get_item_data(self, obj):

        if isinstance(obj.item, Product):
            return ProductSerializer(obj.item).data
        elif isinstance(obj.item, Package):
            return PackageSerializer(obj.item).data
        return None


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at',
                  'updated_at', 'total_cart']
