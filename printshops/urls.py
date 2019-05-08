from django.urls import path

from . import views

urlpatterns = [
    path('', views.ListPrintShopView.as_view(), name='list_print_shop'),
    path('register', views.CreatePrintShopView.as_view(), name='create_print_shop'),
    path('<slug:slug>/', views.DetailedPrintShopView.as_view(), name='details_print_shop'),
    path('<slug:slug>/edit/', views.EditPrintShopView.as_view(), name='edit_print_shop'),
    path('<slug:slug>/user/', views.PrintShopUserView.as_view(), name='print_shop_user'),
    path('<slug:slug>/confirm/', views.PrintShopEmailConfirmationView.as_view(), name='print_shop_email_confirm'),
    path('<slug:slug>/pricelist/', views.CreatePrintShopPriceListView.as_view(), name='create_printshop_pricelist'),
    path('<slug:slug>/pricelist/delete/', views.DeletePrintShopPriceListView.as_view(), name='delete_printshop_pricelist'),
    path('verify/<str:uidb64>/<str:token>', views.PrintShopEmailVerifyView.as_view(), name='print_shop_email_verify'),
]
