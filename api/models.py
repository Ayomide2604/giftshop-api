from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
# Create your models here.

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=255)
    image = CloudinaryField('image')
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Package(models.Model):
    title = models.CharField(max_length=255)
    categories = models.ManyToManyField(
        Category, related_name='packages')
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory = models.IntegerField(default=1)
    image = CloudinaryField('image')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cart_items = GenericRelation('CartItem')

    def get_content_type_id(self):
        content_type = ContentType.objects.get_for_model(self)
        return content_type.id

    def __str__(self):
        return self.title


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory = models.IntegerField(default=1)
    image = CloudinaryField('image')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cart_items = GenericRelation('CartItem')

    def get_content_type_id(self):
        content_type = ContentType.objects.get_for_model(self)
        return content_type.id

    def __str__(self):
        return self.name


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_cart(self):
        return sum(item.subtotal() for item in self.items.all()) if self.items.exists() else 0

    def __str__(self):
        return f"Cart - {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items")
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey("content_type", "object_id")
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def subtotal(self):
        return self.quantity * getattr(self.item, 'price', 0)

    def __str__(self):
        return f"{self.quantity} x {self.item} in {self.cart.user.username}'s cart"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    reference = models.CharField(
        max_length=100, unique=True, null=True, blank=True)

    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total_price(self):
        self.total_price = sum(item.subtotal() for item in self.items.all())
        self.save()

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey("content_type", "object_id")
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} x {self.item} in Order {self.order.id}"


class Shipping(models.Model):
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="shipping")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='address')
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField()
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Shipping'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"Shipping for Order {self.order.id}"
