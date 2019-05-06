from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ProductFigure, ProductCategory, Product, ProductImage

"""Product create/edit"""
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ('owner',)


"""Product Image create/edit"""
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = '__all__'
        widgets = {
            'product': forms.HiddenInput,
        }


"""Product Category create/edit"""
class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        exclude = ('owner',)


"""Product Figure create/edit"""
class ProductFigureForm(forms.ModelForm):
    class Meta:
        model = ProductFigure
        exclude = ('owner',)
