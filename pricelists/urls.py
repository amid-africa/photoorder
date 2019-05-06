from django.urls import path

from . import views

urlpatterns = [
    path('', views.ListPriceListView.as_view(), name='list_pricelist'),
    path('create/', views.CreatePriceListView.as_view(), name='create_pricelist'),
    path('<int:pk>/', views.DetailedPriceListView.as_view(), name='detailed_pricelist'),
    path('edit/<int:pk>/', views.EditPriceListView.as_view(), name='edit_pricelist'),
    path('delete/<int:pk>/', views.DeletePriceListView.as_view(), name='delete_pricelist'),

    path('product/<int:pk>/', views.CreatePriceListProductView.as_view(), name='create_pricelistproduct'),
    path('product/edit/<int:pk>/', views.EditPriceListProductView.as_view(), name='edit_pricelistproduct'),
    path('product/delete/<int:pk>/', views.DeletePriceListProductView.as_view(), name='delete_pricelistproduct'),

    path('currency/<int:pk>/', views.CreateCurrencyView.as_view(), name='create_currency'),
    path('currency/edit/<int:pk>/', views.EditCurrencyView.as_view(), name='edit_currency'),
    path('currency/delete/<int:pk>/', views.DeleteCurrencyView.as_view(), name='delete_currency'),

    path('rate/', views.ListRateView.as_view(), name='list_rate'),
    path('rate/create/', views.CreateRateView.as_view(), name='create_rate'),
    path('rate/<int:pk>/', views.EditRateView.as_view(), name='edit_rate'),
]
