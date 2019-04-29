from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver

from .models import ProductFigure

"""Automatically delete images on delete of record to prevent orphaned files"""
@receiver(post_delete, sender=ProductFigure)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)
