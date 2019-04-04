from django import forms
from django.contrib.auth.forms import (UserCreationForm, UserChangeForm,
                PasswordResetForm, ReadOnlyPasswordHashField)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext, gettext_lazy as _

from .models import User


class CustomUserCreationForm(UserCreationForm):
    """A form to create a new normal user"""
    class Meta(UserCreationForm):
        model = User
        fields = ('email', 'name')


class CustomUserChangeForm(UserChangeForm):
    """A form for the user to change thier details"""
    class Meta:
        model = User
        fields = ('email', 'name')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email != self.instance.email: # Only check if password has changed
            qs = User.objects.filter(email=email)
            if qs.exists():
                raise forms.ValidationError("This email address is already registered.")
        return email


class CustomPasswordResetForm(PasswordResetForm):
    """A form to send a password reset key to the email provided"""
    email = forms.CharField(label=_("Email Address"),
                            widget=forms.TextInput(attrs={'autofocus': True}))

    def save(self, domain_override=None,
             subject_template_name='user/password_reset_subject.txt',
             email_template_name='user/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None,
             html_email_template_name=None, extra_email_context=None):

        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override

        email = self.cleaned_data["email"]
        for user in self.get_users(email):
            context = {
                'email': email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name, email_template_name, context, from_email,
                email, html_email_template_name=html_email_template_name,
            )


class UserAdminCreationForm(forms.ModelForm):
    """An admin form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """An admin form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', 'is_superuser')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]
