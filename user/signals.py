from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.core.mail import mail_admins
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

User = get_user_model()
current_site = Site.objects.get_current()

# Check if email change
@receiver(pre_save,sender=User)
def pre_check_email(sender, instance, **kwargs):
    if instance.id:
        _old_email = instance._old_email = sender.objects.get(id=instance.id).email
        if _old_email != instance.email:
            instance.is_confirmed = False

@receiver(post_save,sender=User)
def post_check_email(sender, instance, created, **kwargs):
    if not instance.is_confirmed:
        subject = 'Activate Your MySite Account'
        message = render_to_string('user/user_confirm_email.html', {
            'user': instance,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(instance.pk)),
            'token': default_token_generator.make_token(instance),
        })
        instance.email_user(subject, message)
