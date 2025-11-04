from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from sphinx.email_utils import send_email

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=150)
    body = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.title


@receiver(post_save, sender=Notification)
def email_on_new_notification(sender, instance: Notification, created: bool, **kwargs):
    if created and instance.user and instance.user.email:
        try:
            send_email(
                subject=instance.title,
                message=instance.body,
                to=[instance.user.email],
                fail_silently=True,
                html_template='emails/notification.html',
                context={'title': instance.title, 'body': instance.body},
            )
        except Exception:
            pass
