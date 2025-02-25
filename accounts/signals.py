from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile, CustomUser


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    """Create a profile when a new user is created and copy user details."""
    if created:
        Profile.objects.create(
            user=instance,
            first_name=instance.first_name,
            last_name=instance.last_name,
            username=instance.username,
            email=instance.email
        )
