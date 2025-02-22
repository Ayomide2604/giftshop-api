from django.contrib import admin
from .models import Category, Package, Product
# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'image')
    search_fields = ('title', )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price', 'image')
    search_fields = ('name',)
    list_filter = ('name',)
