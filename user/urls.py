from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.urls import path, reverse_lazy
from .views import (ConfirmEmail, CustomPasswordResetView,
                    CustomPasswordChangeView, SignUp, UserView, UserUpdate)

from .sitemaps import StaticViewSitemap

sitemaps = {
    'User Site Map': StaticViewSitemap,
}

urlpatterns = [
    path('', UserView.as_view(), name='profile'),
    path('login/',
         auth_views.LoginView.as_view(), name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(next_page=reverse_lazy('home')),
         name='logout'),
    path('signup/', SignUp.as_view(), name='signup'),
    path('update/',
         UserUpdate.as_view(), name="update_user"),
    path('confirm/<str:uidb64>/<str:token>',
         ConfirmEmail.as_view(), name='email_confirm'),
    path('password/',
         CustomPasswordChangeView.as_view(), name='password_change'),
    path('password/change/done/',
         auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),
    path('password/reset/',
         CustomPasswordResetView.as_view(), name='password_reset'),
    path('password/reset/done/',
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('password/reset/<str:uidb64>/<str:token>',
         auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password/reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='user_sitemap')
]
