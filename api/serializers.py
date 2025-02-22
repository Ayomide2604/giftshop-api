from rest_framework import serializers
from .models import Category, Package, Product


class CategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        return obj.image.url

    class Meta:
        model = Category
        fields = ['id', 'name', 'image_url', 'description']


class PackageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        return obj.image.url

    class Meta:
        model = Package
        fields = ['id', 'title', 'category',
                  'description', 'price', 'image_url']


class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        return obj.image.url

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image_url']
