from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from PIL import Image

import io

User = get_user_model()

"""Images of products to use online"""
class ProductFigure(models.Model):
    image = models.ImageField(_('Product Figure'), upload_to='figures/%Y/%m/%d/')
    public = models.BooleanField(_('Avaliable to All'), default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                              on_delete=models.SET_NULL)

    def resize_figure(self, size=(256, 256)):
        try:
            image = Image.open(self.image.path)
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(self.image.path)
        except IOError:
            print("Cannot resize", self.image.name)

    # AFTER saving, resive the image and overwrite
    def save(self, *args, **kwargs):
        super().save(*args,**kwargs)
        self.resize_figure()

    def __str__(self):
        return self.image.name

    def get_absolute_url(self):
        return reverse('edit_figure', args=[self.pk])

    def is_owner(self, user):
        return self.owner == user


"""Categories for products"""
class ProductCategory(models.Model):
    title = models.CharField(_('Title'), max_length=64)
    description = models.TextField(_('Description'))
    public = models.BooleanField(_('Avaliable to All'), default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                              on_delete=models.SET_NULL)
    category_figure = models.ForeignKey(ProductFigure, blank=True, null=True,
                            on_delete=models.SET_NULL)

    class Meta:
        unique_together = ("title", "owner")
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('edit_category', args=[self.pk])

    def is_owner(self, user):
        return self.owner == user


"""The actual product"""
class Product(models.Model):
    title = models.CharField(_('Title'), max_length=64)
    description = models.TextField(_('Description'))
    product_category = models.ForeignKey(ProductCategory, null=True,
                            on_delete=models.SET_NULL, related_name='category')
    product_figure = models.ForeignKey(ProductFigure, blank=True, null=True,
                            on_delete=models.SET_NULL, related_name='figure')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                              on_delete=models.SET_NULL, related_name='owner')

    class Meta:
        unique_together = ("title", "owner")
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.title

    def save(self,*args,**kwargs):
        created = not self.pk
        super().save(*args,**kwargs)
        if created:
            ProductImage.objects.create(product=self)

    def get_absolute_url(self):
        return reverse('detailed_product', args=[self.pk])

    def is_owner(self, user):
        return self.owner == user


"""Images required for products"""
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    required = models.BooleanField(_('Required'), default=True)
    rotatable = models.BooleanField(_('Avaliable in Landscape and Portrait Format'), default=True)
    ratio = models.DecimalField(_('Ratio x/y'), max_digits=4, default=1.333,
                                        decimal_places=3)
    min_megapixels = models.DecimalField(_('Minimum Mega Pixels'), default=0.5,
                                         max_digits=4, decimal_places=1)
    warn_megapixels = models.DecimalField(_('Warning Mega Pixels'), default=2.1,
                                         max_digits=4, decimal_places=1)

    def get_absolute_url(self):
        return reverse('edit_print', args=[self.pk])
