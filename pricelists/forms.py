from django import forms
from django.utils.translation import gettext_lazy as _

from decimal import Decimal

from products.models import Product

from .models import PriceList, PriceListCurrency, PriceListCurrencyRate, PriceListProduct, PriceListProductPrice

"""Pricelist Currency create/edit"""
class PriceListCurrencyForm(forms.ModelForm):
    baserate = forms.DecimalField(max_digits=16, decimal_places=8,
                              initial=Decimal('1.00'), required=True,
                              label=_('Rate to Base Currency'))

    # Disable the base rate if base currency
    def __init__(self, *args, **kwargs):
        super(PriceListCurrencyForm, self).__init__(*args, **kwargs)
        if self.instance.base:
            self.fields['baserate'].disabled = True

    class Meta:
        model = PriceListCurrency
        exclude = ('base',)
        widgets = {
            'pricelist': forms.HiddenInput,
        }


"""PriceList create/edit"""
class PriceListForm(forms.ModelForm):
    class Meta:
        model = PriceList
        exclude = ('owner',)


"""Pricelist Product create"""
class PriceListProductForm(forms.ModelForm):
    baseprice = forms.DecimalField(max_digits=8, decimal_places=2,
                              initial=Decimal('0.00'), required=True,
                              label=_('Base Price'))

    class Meta:
        model = PriceListProduct
        fields = '__all__'
        widgets = {
            'pricelist': forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        super(PriceListProductForm, self).__init__(*args, **kwargs)
        inital = kwargs.get('initial')
        pricelist = inital.get('pricelist')
        user = inital.get('user')
        existing = PriceListProduct.objects.filter(pricelist=pricelist).values_list('product')
        self.fields['product'].queryset = Product.objects.filter(owner=user).exclude(id__in=existing)



"""Pricelist Product edit"""
class PriceListProductEditForm(forms.ModelForm):
    baseprice = forms.DecimalField(max_digits=8, decimal_places=2,
                              initial=Decimal('0.00'), required=True,
                              label=_('Base Price'))

    class Meta:
        model = PriceListProduct
        fields = '__all__'
        widgets = {
            'pricelist': forms.HiddenInput,
            'product': forms.HiddenInput,
        }
