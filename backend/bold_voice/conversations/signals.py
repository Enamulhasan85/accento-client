from django.db.models.signals import post_delete
from django.dispatch import receiver

from bold_voice.conversations.models import VoiceMessage


@receiver(post_delete, sender=VoiceMessage)
def delete_audio_file(sender, instance, **kwargs):
    if instance.audio_file:
        instance.audio_file.delete(save=False)
