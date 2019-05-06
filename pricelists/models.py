from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from datetime import datetime
import pytz

User = get_user_model()

from products.models import Product


"""The PriceList Header"""
class PriceList(models.Model):
    title = models.CharField(_('Title'), max_length=64, unique=True)
    description = models.TextField(_('Description'))
    active = models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                              on_delete=models.SET_NULL)
    date_created = models.DateTimeField(_('Created'), auto_now_add=True)

    def __str__(self):
        return self.title

    def is_owner(self, user):
        return self.owner == user

    def get_absolute_url(self):
        return reverse('detailed_pricelist', args=[self.pk])


"""Multi Currency Pricelist"""
class PriceListCurrency(models.Model):
    pricelist = models.ForeignKey(PriceList, on_delete=models.CASCADE)
    title = models.CharField(_('Title'), max_length=32)
    code = models.CharField(_('Currency Code'), max_length=3)
    symbol = models.CharField(_('Currency symbol'), max_length=3)
    base = models.BooleanField(default=False)

    class Meta:
        unique_together = ("pricelist", "code")
        ordering = ["code"]

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        super(PriceListCurrency, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('edit_currency', args=[self.pk])

    # Return the current currency rate
    def current_rate(self):
        current = PriceListCurrencyRate.objects.filter(currency=self, date_effective__lt=datetime.now(pytz.utc)).order_by('date_effective').last()
        return current.rate


"""Multi Currency Pricelist Rates"""
class PriceListCurrencyRate(models.Model):
    currency = models.ForeignKey(PriceListCurrency, on_delete=models.CASCADE)
    rate = models.DecimalField(_('Rate to Base'), max_digits=16, decimal_places=8)
    date_effective = models.DateTimeField(_('Effective'), auto_now_add=True)



"""Assign products to said pricelist"""
class PriceListProduct(models.Model):
    pricelist = models.ForeignKey(PriceList, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("pricelist", "product")
        verbose_name = "Pricelist Product"
        verbose_name_plural = "Pricelist Products"

    def __str__(self):
        return '{} - {}'.format(self.pricelist, self.product)

    def get_absolute_url(self):
        return reverse('edit_pricelistproduct', args=[self.pk])

    # Return the current product base price
    def current_price(self):
        currency = PriceListCurrency.objects.filter(pricelist=self.pricelist, base=True).first()
        current = PriceListProductPrice.objects.filter(listproduct=self, date_effective__lt=datetime.now(pytz.utc)).order_by('date_effective').last()
        return '{}{}'.format(currency.symbol, current.price)


"""Assign prices to products of list"""
class PriceListProductPrice(models.Model):
    listproduct = models.ForeignKey(PriceListProduct, on_delete=models.CASCADE)
    price = models.DecimalField(_('Price'), max_digits=8, decimal_places=2)
    date_effective = models.DateTimeField(_('Effective'), auto_now_add=True)

    def __str__(self):
        return '{}: {}'.format(self.listproduct, self.price)
