from allauth.socialaccount.models import SocialAccount
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def save_profile_pic(sender, instance, **kwargs):
    if instance:
        social_account = SocialAccount.objects.filter(user=instance).first()
        if social_account:
            profile = Profile.objects.get_or_create(user=instance)[0]
            profile.profile_pic = social_account.get_avatar_url()
            profile.save()