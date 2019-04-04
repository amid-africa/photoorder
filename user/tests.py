from django.contrib.auth import get_user_model, views as auth_views
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sites.models import Site
from django.core import mail
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from rest_framework import status

from . import forms
from . import views

import random, re, string

User = get_user_model()
current_site = Site.objects.get_current()

class SimpleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.loginName = 'Test User'
        self.loginPassword = ''.join(random.choices(
                                string.ascii_uppercase + string.digits, k=12))
        self.loginEmail = 'fred@frog.com'
        self.loginEmail2 = 'anonther@frog.com'
        self.factory = RequestFactory()
        self.randomPassword = ''.join(random.choices(
                                string.ascii_uppercase + string.digits, k=12))
        self.credentials = {
            'name': self.loginName,
            'password': self.loginPassword,
            'email': self.loginEmail
        }
        self.user = User.objects.create_user(**self.credentials)

        self.credentials2 = {
            'name': 'Another User',
            'password': ''.join(random.choices(
                                string.ascii_uppercase + string.digits, k=12)),
            'email': self.loginEmail2
        }
        User.objects.create_user(**self.credentials2)


    def setup_request(self, request):
        request.user = self.user

        """Annotate a request object with a session"""
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        """Annotate a request object with a messages"""
        middleware = MessageMiddleware()
        middleware.process_request(request)
        request.session.save()

        request.session['some'] = 'some'
        request.session.save()


    def testUserView(self):
        """Get User Profile View"""
        url = reverse('profile')
        # Logout incase a user is logged in, must redirect to login
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, '{}?next={}'.format(reverse('login'), url))

        # Login User, this time form wont redirect
        self.client.login(email=self.loginEmail, password=self.loginPassword)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'user/user_profile.html')
        self.assertEqual(self.loginEmail, response.context['user'].email)
        

    def testLogin(self):
        """Get login form"""
        url = reverse('login')
        request = self.factory.get(url)
        self.setup_request(request)
        view = auth_views.LoginView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.template_name[0], 'registration/login.html')

        """Post Login form"""
        # InCorrect Data - Not logged in, stay at loggin in form
        form_data = {
            'username': 'msdahfmbfsakHEFWJkjdhaj,HFDBjahjeewjhf',
            'password': 'amsndfbkq4tiq4 gkrEYTR I2Gewhwae'
        }
        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.template_name[0], 'registration/login.html')

        # Correct Data - Login and redirct to profile
        form_data = {
            'username': self.loginEmail,
            'password': self.loginPassword
        }
        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, reverse('profile'))
        self.assertEqual(response.context["user"].name, self.loginName)

        """Logout, redirect to home"""
        url = reverse('logout')
        request = self.factory.get(url)
        self.setup_request(request)
        view = auth_views.LogoutView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, reverse('home'))
        self.assertFalse(request.user.is_authenticated)


    def testSignup(self):
        """Get signup view"""
        url = reverse('signup')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'registration/signup.html')

        # Sign up existing email
        form_data = {
            'email': self.loginEmail,
            'name': self.loginName,
            'password1': self.loginPassword,
            'password2': self.loginPassword,
        }
        form = forms.CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        response = self.client.post(url, form_data)
        self.assertFormError(response, 'form', 'email', 'User with this Email address already exists.')

        # Sign up with no details
        form_data = {
            'email': '',
            'name': '',
            'password1': '',
            'password2': '',
        }
        form = forms.CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        response = self.client.post(url, form_data)
        self.assertFormError(response, 'form', 'email', 'This field is required.')
        self.assertFormError(response, 'form', 'name', 'This field is required.')
        self.assertFormError(response, 'form', 'password1', 'This field is required.')

        # Sign up invalid email and mismatching passwords
        form_data = {
            'email': 'notanemail',
            'name': self.loginName,
            'password1': self.loginPassword,
            'password2': self.loginPassword[::-1],
        }
        form = forms.CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        response = self.client.post(url, form_data)
        self.assertFormError(response, 'form', 'email', 'Enter a valid email address.')
        self.assertFormError(response, 'form', 'password2', "The two password fields didn't match.")

        # Sign up valid
        form_data = {
            'email': 'agood@email.com',
            'name': 'A good Name',
            'password1': self.randomPassword,
            'password2': self.randomPassword,
        }
        form = forms.CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        response = self.client.post(url, form_data)
        self.assertEqual(response.context['user'].name, 'A good Name')

        # Get the sent email and extrat the confirmation link
        messageBody = mail.outbox[len(mail.outbox)-1].body
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', messageBody)
        url = urls[0]
        path = url[url.index(current_site.domain)+len(current_site.domain):] # Get path only from the url

        # Place invalid user and token
        fake_uid = reverse('email_confirm', kwargs={'uidb64':'!*%$£@#', 'token': '111-111111111111'})
        response = self.client.get(fake_uid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'user/confirm_email_failed.html')

        # confirm the email address with correct token
        response = self.client.get(path)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, reverse('profile'))


    def testUserUpdate(self):
        """Test Change the user
        Only edit own
        Email can be the same as current
        Name and email are required
        Email must not be used by another user
        If email is changed, is_confirmed must set to false
        """
        url = reverse('update_user')
        self.client.login(email=self.loginEmail, password=self.loginPassword)
        response = self.client.get(url)
        self.assertEqual(self.loginEmail, response.context['user'].email)
        self.assertIn(self.loginEmail, str(response.context['form']))

        # Name and email blank
        form_data = {
            'email': '',
            'name': '',
        }
        response = self.client.post(url, form_data)
        self.assertFormError(response, 'form', 'email', 'This field is required.')
        self.assertFormError(response, 'form', 'name', 'This field is required.')

        # Email in use by another user
        form_data = {
            'email': self.loginEmail2,
            'name': self.loginName,
        }
        response = self.client.post(url, form_data)
        self.assertFormError(response, 'form', 'email', 'This email address is already registered.')

        # Same Email address
        form_data = {
            'email': self.loginEmail,
            'name': self.loginName,
        }
        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, reverse('profile'))


    def testPasswordChange(self):
        """Get password change view"""
        url = reverse('password_change')

        # Logout incase a user is logged in, must redirect to login
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, '{}?next={}'.format(reverse('login'), url))

        # Login User, this time form wont redirect
        self.client.login(email=self.loginEmail, password=self.loginPassword)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'user/password_change_form.html')

        # Submit with all fields empty
        form_data = {
            'old_password': '',
            'new_password1': '',
            'new_password2': '',
        }
        response = self.client.post(url, form_data)
        self.assertFormError(response, 'form', 'old_password', 'This field is required.')
        self.assertFormError(response, 'form', 'new_password1', 'This field is required.')
        self.assertFormError(response, 'form', 'new_password2', 'This field is required.')

        # Submit with incorrect old password and mismatching new passwords
        form_data = {
            'old_password': self.randomPassword,
            'new_password1': self.randomPassword,
            'new_password2': self.randomPassword[::-1],
        }
        response = self.client.post(url, form_data)
        self.assertFormError(response, 'form', 'old_password', 'Your old password was entered incorrectly. Please enter it again.')
        self.assertFormError(response, 'form', 'new_password2', "The two password fields didn't match.")

        # Submit correctly
        form_data = {
            'old_password': self.loginPassword,
            'new_password1': self.randomPassword,
            'new_password2': self.randomPassword,
        }
        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, reverse('password_change_done'))


    def testPasswordReset(self):
        """Get password reset view"""
        url = reverse('password_reset')

        # Logout incase a user is logged in
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'user/password_reset_form.html')

        # Submit with all fields empty
        form_data = {
            'email': self.loginEmail,
        }
        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, reverse('password_reset_done'))


    def testSitemaps(self):
        url = reverse('user_sitemap')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual("application/xml", response['Content-Type'])
        self.assertNotEqual(len(response.context['urlset']), 0)
