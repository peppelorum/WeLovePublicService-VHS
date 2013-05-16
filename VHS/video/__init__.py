from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import User
from models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a matching profile whenever a user object is created."""
    if created:
        profile, new = Profile.objects.get_or_create(user=instance)