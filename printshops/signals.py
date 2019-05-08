from django.contrib.sites.models import Site
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import PrintShop
from .token import confirmation_token

current_site = Site.objects.get_current()


# Check if print shop email change
@receiver(pre_save,sender=PrintShop)
def pre_check_email(sender, instance, **kwargs):
    if instance.id:
        _old_email = instance._old_email = sender.objects.get(id=instance.id).email
        if _old_email != instance.email:
            instance.email_confirmed = False

# Send an email confirm if email changed
@receiver(post_save,sender=PrintShop)
def post_check_email(sender, instance, created, **kwargs):
    if not instance.email_confirmed:
        subject = 'Confirm Your Shop Email'
        message = render_to_string('printshop/shop_confirm_email.html', {
            'shop': instance,
            'domain': current_site.domain,
            'sid': urlsafe_base64_encode(force_bytes(instance.pk)),
            'token': confirmation_token(instance.email),
        })
        instance.email_shop(subject, message)
