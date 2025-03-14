from django.contrib import admin
from .models import Category, Package, Product, Cart, CartItem, Order, OrderItem, Shipping
from django.contrib.contenttypes.admin import GenericTabularInline

# Register your models here.


class CartItemInline(GenericTabularInline):
    model = CartItem
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('id',)


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'price')
    search_fields = ('title',)
    list_filter = ('title',)
    ordering = ('title',)
    inlines = [CartItemInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('name',)
    inlines = [CartItemInline]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user__email', 'total_cart')
    search_fields = ('user__email',)
    list_filter = ('user__email',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'quantity', 'created_at', 'updated_at')
    search_fields = ('cart__user__email',)
    list_filter = ('cart',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user__email', 'total_price', 'status',
                    'created_at', 'updated_at')
    search_fields = ('user__email',)
    list_filter = ('status',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'item', 'quantity', 'price')
    search_fields = ('order__user__email',)
    list_filter = ('order',)


@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'address', 'city',
                    'state', 'postal_code', 'country', 'phone')
    search_fields = ('order__user__username',)
    list_filter = ('order',)
