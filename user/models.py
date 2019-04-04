from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser,BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _

import datetime

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, is_staff=False,  **extra_fields):
        if not email:
            raise ValueError('The given email must be set')

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_staffuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)



class User(AbstractBaseUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(_('name known by'), max_length=128)
    is_active = models.BooleanField(_('active user'), default=True)
    is_confirmed = models.BooleanField(_('email confirmed'), default=False)
    is_staff = models.BooleanField(_('staff user'), default=False)
    is_superuser = models.BooleanField(_('super user'), default=False)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [ 'name' ]

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ('name', )

    def __str__(self):
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        """ Sends an email to this User. """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def has_perm(self, perm, obj=None):
       return self.is_superuser

    def has_module_perms(self, app_label):
       return self.is_superuser
