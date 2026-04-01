from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Letter
from .models import SampleLetter
from .models import SampleNotification
#@receiver(post_save, sender=settings.AUTH_USER_MODEL)
@receiver(post_save, sender=Letter)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # trigger notification to all consumers in the 'user-notification' group
        channel_layer = get_channel_layer()
        group_name = 'user-notifications'
        event = {
            "type": "user_joined",
            #"text": instance.username
            "text": instance.sender + " created a new letter!"
        }
        async_to_sync(channel_layer.group_send)(group_name, event)
    else:
        channel_layer = get_channel_layer()
        group_name = 'user-notifications'
        event = {
            "type": "user_joined",
            #"text": instance.username
            "text": instance.letter_desc + " new update!"
        }
        async_to_sync(channel_layer.group_send)(group_name, event)



"""@receiver(post_save, sender=SampleLetter)
def create_update_notification(sender, instance, created, **kwargs):
    if not created:
        SampleNotification.objects.create(
            user=instance.user,
            message=f'Your letter with ID {instance.id} has been updated.'
        )"""