from django.contrib import admin

from .models import ProductFigure, ProductCategory, Product, ProductImage

admin.site.register(ProductFigure)
admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(ProductImage)
