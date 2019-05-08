from django import forms
from django.db import models

from .models import PrintShop, PrintShopUser


"""Printshop create/edit"""
class PrintShopForm(forms.ModelForm):
    class Meta:
        model = PrintShop
        exclude = ('slug', 'email_confirmed', 'active',)


"""PrintShop Users"""
class PrintShopUserForm(forms.ModelForm):
    class Meta:
        model = PrintShopUser
        exclude = ('creator', )
