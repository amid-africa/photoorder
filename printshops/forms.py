from django import forms
from django.db import models

from .models import PrintShop, PrintShopUser, PrintShopPriceList
from pricelists.models import PriceList


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


"""Printshop Pricelists"""
class PrintShopPriceListForm(forms.ModelForm):
    class Meta:
        model = PrintShopPriceList
        fields = '__all__'
        widgets = {
            'printshop': forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        super(PrintShopPriceListForm, self).__init__(*args, **kwargs)
        inital = kwargs.get('initial')
        printshop = inital.get('printshop')
        existing = PrintShopPriceList.objects.filter(printshop=printshop).values_list('pricelist')
        self.fields['pricelist'].queryset = PriceList.objects.exclude(id__in=existing)
