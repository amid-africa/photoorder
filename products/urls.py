from django.urls import path

from . import views

urlpatterns = [
    path('', views.ListProductView.as_view(), name='list_product'),
    path('create/', views.CreateProductView.as_view(), name='create_product'),
    path('<int:pk>/', views.DetailedProductView.as_view(), name='detailed_product'),
    path('edit/<int:pk>/', views.EditProductView.as_view(), name='edit_product'),
    path('delete/<int:pk>/', views.DeleteProductView.as_view(), name='delete_product'),

    path('print/create/<int:pk>/', views.CreatePrintView.as_view(), name='create_print'),
    path('print/edit/<int:pk>/', views.EditPrintView.as_view(), name='edit_print'),
    path('print/delete/<int:pk>/', views.DeletePrintView.as_view(), name='delete_print'),

    path('category/', views.ListCategoryView.as_view(), name='list_category'),
    path('category/create/', views.CreateCategoryView.as_view(), name='create_category'),
    path('category/<int:pk>/', views.DetailedCategoryView.as_view(), name='detailed_category'),
    path('category/edit/<int:pk>/', views.EditCategoryView.as_view(), name='edit_category'),
    path('category/delete/<int:pk>/', views.DeleteCategoryView.as_view(), name='delete_category'),

    path('figure/', views.ListFigureView.as_view(), name='list_figure'),
    path('figure/create/', views.CreateFigureView.as_view(), name='create_figure'),
    path('figure/<int:pk>/', views.DetailedFigureView.as_view(), name='detailed_figure'),
    path('figure/edit/<int:pk>/', views.EditFigureView.as_view(), name='edit_figure'),
    path('figure/delete/<int:pk>/', views.DeleteFigureView.as_view(), name='delete_figure'),
]
