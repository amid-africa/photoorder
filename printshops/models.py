from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()

from pricelists.models import PriceList
from user.models import Group, GroupUser

class PrintShop(models.Model):
    name = models.CharField(_('Shop Name'), max_length=128, unique=True)
    slug = models.CharField(unique=True, max_length=128, blank=True, null=True)
    about = models.TextField(_('About Us'))
    email = models.EmailField(_('Email Address'), blank=False)
    email_confirmed = models.BooleanField(default=False)
    phone = PhoneNumberField(_('Phone Number'), help_text = "E.164 Format, i.e. +263242123456")
    address_line1 = models.CharField(_("Address Line 1"), max_length = 45, blank = True)
    address_line2 = models.CharField(_("Address Line 2"), max_length = 45, blank = True, help_text = "Optional")
    postal_code = models.CharField(_("Postal Code"), max_length = 10, blank = True, help_text = "Optional")
    city = models.CharField(_("City / Town"), max_length = 50)
    state_province = models.CharField(_("State / Province"), max_length = 40, blank = True, help_text = "Optional")
    country = models.CharField(_("Country"), max_length = 40, blank = True)
    latitude = models.DecimalField(_("Latitude"), max_digits=10, decimal_places=7, default=0)
    longitude = models.DecimalField(_("Longitude"), max_digits=10, decimal_places=7, default=0)
    logo = models.ImageField(_('Shop Logo'), upload_to='logos/%Y/%m/%d/')
    active = models.BooleanField(default=False)
    date_added = models.DateTimeField(_('Created'), auto_now_add=True)
    date_updated = models.DateTimeField(_('Last Updated'), auto_now=True)


    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(PrintShop, self).save(*args, **kwargs)

    def __str__(self):
        return '{}, {}, {}'.format(self.name, self.city, self.country)

    def get_absolute_url(self):
        return reverse('details_print_shop', args=[self.slug])

    def email_shop(self, subject, message, from_email=None, **kwargs):
        """ Sends an email to the shop email address. """
        res = send_mail(subject, message, from_email, [self.email], **kwargs)

    """Check if user is staff for the shop"""
    def is_shop_staff(self, user):
        if PrintShopUser.objects.filter(
                        group=PrintShopGroup.objects.get(printshop=self),
                        user=user, user__is_active=True):
            return True

        else:
            return False

    """Check if user is admin for the shop"""
    def is_shop_admin(self, user):
        if PrintShopUser.objects.filter(
                        group=PrintShopGroup.objects.get(printshop=self),
                        user=user, admin=True, user__is_active=True):
            return True

        else:
            return False

    class Meta:
        ordering = ["name"]
        verbose_name = "Print Shop"
        verbose_name_plural = "Print Shops"


class PrintShopGroup(Group):
    printshop = models.ForeignKey(PrintShop, on_delete=models.CASCADE)

    def member_set(self):
        return PrintShopUser.objects.filter(group=self).order_by('user')


"""Users of print shops:
Admin can admistor shop details, users, prices and services and get all admin emails
Users can download orders only
"""
class PrintShopUser(GroupUser):
    creator = models.BooleanField(_('Shop Creator'), default=False)
    order_notifications = models.BooleanField(_('Recieve Order Emails'), default=True)
    customer_notifications = models.BooleanField(_('Recieve Emails From Customers'), default=True)
    service_notifications = models.BooleanField(_('Recieve Service Emails'), default=True)

    class Meta:
        verbose_name = "Print Shop Group User"
        verbose_name_plural = "Print Shop Group Users"

    def __str__(self):
        return '{} - {}'.format(self.group, self.user)



"""Assign pricelist to said printshop"""
class PrintShopPriceList(models.Model):
    printshop = models.ForeignKey(PrintShop, on_delete=models.CASCADE)
    pricelist = models.ForeignKey(PriceList, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("printshop", "pricelist")
        verbose_name = "Print Shop Price List"
        verbose_name_plural = "Print Shop Price Lists"

    def __str__(self):
        return '{} - {}'.format(self.printshop, self.pricelist)

    def get_absolute_url(self):
        return reverse('create_printshop_pricelist', args=[self.printshop.slug])
