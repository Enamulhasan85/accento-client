from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
import logging

logger = logging.getLogger(__name__)

from bold_voice.identity.services import EmailConfirmationService

User = settings.AUTH_USER_MODEL

# Custom signal to handle user registration
user_registered = Signal()


@receiver(user_registered)
def user_registered_receiver(sender, user: User, request, **kwargs):
    if not user.email_verified:
        EmailConfirmationService(user=user, request=request).send()


@receiver(post_save, sender=User)
def user_register_post_save(sender, instance: User, created, **kwargs):
    if created:
        user_group = Group.objects.filter(name='Member').first()
        if user_group == None:
            logger.info(f"Creating 'Member' group for new user: {instance.username}")
            user_group = Group.objects.create(name='Member')

        instance.groups.add(user_group)


@receiver(post_save, sender=SocialAccount)
def social_account_post_save(sender, instance: SocialAccount, created, **kwargs):
    if created:
        user = instance.user
        user.email_verified = True
        user.avatar = instance.get_avatar_url()
        user.save(update_fields=['email_verified', 'avatar'])
