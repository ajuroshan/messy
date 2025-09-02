from allauth.socialaccount.models import SocialAccount
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Application


@receiver(post_save, sender=Application)
def save_profile_pic(sender, instance, **kwargs):
    if instance:
        # Set the first name and last name of the user
        instance.applicant.first_name = instance.first_name
        instance.applicant.last_name = instance.last_name if instance.last_name else ""
        instance.applicant.save()

        # Check if the application has a profile picture
        if instance.profile_pic:
            # Set the profile picture to the profile
            profile = Profile.objects.get_or_create(user=instance.applicant)[0]
            profile.profile_pic = instance.profile_pic.url
            profile.save()
