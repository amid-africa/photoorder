from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from .forms import (CustomUserCreationForm, CustomPasswordResetForm,
                    CustomUserChangeForm)

User = get_user_model()

@method_decorator(login_required, name='dispatch')
class UserView(TemplateView):
    template_name = "user/user_profile.html"

    def get_context_data(self, *args, **kwargs):
        # The current user is already in the context
        context = super(UserView, self).get_context_data(*args, **kwargs)
        context['data'] = 'somedata'
        return context


@method_decorator(login_required, name='dispatch')
class UserUpdate(UpdateView):
    model = User
    template_name = 'user/user_update_form.html'
    form_class = CustomUserChangeForm
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user


class SignUp(View):
    """Create a new user"""
    success_url = reverse_lazy('profile')
    template_name = 'registration/signup.html'

    def __init__(self, **kwargs):
        if 'success_url' in kwargs:
            self.success_url = kwargs['success_url']

    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(self.success_url)

        return render(request, self.template_name, {'form': form})


class ConfirmEmail(View):
    """Confirm the users email address"""
    success_url = reverse_lazy('profile')

    def __init__(self, **kwargs):
        if 'success_url' in kwargs:
            self.success_url = kwargs['success_url']

    def get(self, request, uidb64, token):
        try:
            # Get the user
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            # Check the token is valid
            messages.success(request, 'Your email address has been confirmed successfully.')
            if not user.is_confirmed:
                user.is_confirmed = True
                user.save()
            return redirect(self.success_url)

        # If error, display it.
        messages.error(request, 'Your email could not be confirmed. Please generate a new code to try again.')
        return render(request, 'user/confirm_email_failed.html', {'user': user})


class CustomPasswordResetView(PasswordResetView):
    """Extend builtin PasswordResetView to use our custom form and template"""
    form_class = CustomPasswordResetForm
    template_name = 'user/password_reset_form.html'


class CustomPasswordChangeView(PasswordChangeView):
    """Extend builtin PasswordChangeView to use our template"""
    template_name = 'user/password_change_form.html'
