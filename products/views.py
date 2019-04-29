from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.views.generic import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View

from .forms import ProductForm, ProductCategoryForm, ProductFigureForm, ProductImageForm
from .models import ProductFigure, ProductCategory, Product, ProductImage

User = get_user_model()

@method_decorator(login_required, name='dispatch')
class ListProductView(ListView):
    template_name = 'product/list.html'
    model = Product

    # Only show the items that the user 'owns'
    def get_queryset(self):
        queryset = self.model.objects.filter(owner=self.request.user)
        return queryset


@method_decorator(login_required, name='dispatch')
class CreateProductView(CreateView):
    template_name = 'product/create.html'
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy('detailed_product')

    # on save, add owner
    def form_valid(self, form):
        product = form.save(commit=False)
        product.owner = self.request.user
        product.save()
        self.success_url = reverse_lazy('detailed_product', kwargs={'pk': product.pk})
        return super(CreateProductView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class DetailedProductView(DetailView):
    template_name = 'product/detail.html'
    model = Product


@method_decorator(login_required, name='dispatch')
class EditProductView(UpdateView):
    template_name = 'product/edit.html'
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy('detailed_product')

    # Only allow ordinary user to update their own, but staff all.
    def get_queryset(self):
        queryset = super(EditProductView, self).get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(creator=self.request.user)
        return queryset

    def form_valid(self, form):
        product = form.save()
        self.success_url = reverse_lazy('detailed_product', kwargs={'pk': product.pk})
        return super(EditProductView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class DeleteProductView(View):
    success_url = reverse_lazy('list_product')

    def get(self, request, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs['pk'])

        # Check request user is the owner or a staff member
        if not product.is_owner(self.request.user) and not self.request.user.is_staff:
            messages.error(request, 'You do not have the authority to delete this product.')
            return redirect(self.success_url)

        messages.success(request, 'Product "{}" has been successfully deleted'.format(product.title))
        product.delete()
        return redirect(self.success_url)


@method_decorator(login_required, name='dispatch')
class CreatePrintView(CreateView):
    template_name = 'print/create.html'
    model = ProductImage
    form_class = ProductImageForm
    success_url = reverse_lazy('create_print')
    product = None

    #Add product data to the context
    def get_context_data(self, *args, **kwargs):
        context = super(CreatePrintView, self).get_context_data(*args, **kwargs)
        context['product'] = self.product
        return context

    # Set the product form field from the product pk and raise a 404 if not owner
    def get_initial(self):
        self.product = get_object_or_404(Product, pk=self.kwargs.get('pk'))
        if not self.product.is_owner(self.request.user) and not self.request.user.is_staff:
            raise Http404
        return {
            'product':self.product,
        }

    def form_valid(self, form):
        print = form.save()
        self.success_url = reverse_lazy('create_print', kwargs={'pk': self.kwargs.get('pk')})
        return super(CreatePrintView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class EditPrintView(UpdateView):
    template_name = 'print/edit.html'
    model = ProductImage
    form_class = ProductImageForm
    success_url = reverse_lazy('create_print')

    # Only allow ordinary user to update their own, but staff all.
    def get_queryset(self):
        queryset = super(EditPrintView, self).get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(product__owner=self.request.user)
        return queryset

    def form_valid(self, form):
        print = form.save()
        self.success_url = reverse_lazy('create_print', kwargs={'pk': print.product.pk})
        return super(EditPrintView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class DeletePrintView(View):
    success_url = reverse_lazy('create_print')

    def get(self, request, **kwargs):
        image = get_object_or_404(ProductImage, pk=self.kwargs['pk'])

        self.success_url = reverse_lazy('create_print', kwargs={'pk': image.product.pk})

        # Check not deleting the last image
        set = ProductImage.objects.filter(product=image.product)
        if len(set) == 1:
            messages.error(request, 'A product must have at least one image.')
            return redirect(self.success_url)

        # Check request user is the owner or a staff member
        if not image.product.is_owner(self.request.user) and not self.request.user.is_staff:
            messages.error(request, 'You do not have the authority to delete this image.')
            return redirect(self.success_url)

        messages.success(request, 'Image has been successfully deleted from product "{}"'.format(image.product))
        image.delete()
        return redirect(self.success_url)


@method_decorator(login_required, name='dispatch')
class ListCategoryView(ListView):
    template_name = 'category/list.html'
    model = ProductCategory

    # Only show the items that the user 'owns'
    def get_queryset(self):
        queryset = self.model.objects.filter(owner=self.request.user)
        return queryset


@method_decorator(login_required, name='dispatch')
class CreateCategoryView(CreateView):
    template_name = 'category/create.html'
    model = ProductCategory
    form_class = ProductCategoryForm
    success_url = reverse_lazy('list_category')

    # on save, add owner
    def form_valid(self, form):
        category = form.save(commit=False)
        category.owner = self.request.user
        category.save()
        return super(CreateCategoryView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class DetailedCategoryView(DetailView):
    template_name = 'category/detail.html'
    model = ProductCategory


@method_decorator(login_required, name='dispatch')
class EditCategoryView(UpdateView):
    template_name = 'category/edit.html'
    model = ProductCategory
    form_class = ProductCategoryForm
    success_url = reverse_lazy('list_category')

    # Only allow ordinary user to update their own, but staff all.
    def get_queryset(self):
        queryset = super(EditCategoryView, self).get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(creator=self.request.user)
        return queryset


@method_decorator(login_required, name='dispatch')
class DeleteCategoryView(View):
    success_url = reverse_lazy('list_category')

    def get(self, request, **kwargs):
        category = get_object_or_404(ProductCategory, pk=self.kwargs['pk'])

        # Check request user is the owner or a staff member
        if not category.is_owner(self.request.user) and not self.request.user.is_staff:
            messages.error(request, 'You do not have the authority to delete this category.')
            return redirect(self.success_url)

        # Check the category is not in use with any products
        if Product.objects.filter(product_category=category):
            messages.warning(request, 'Category "{}" cannot be deleted as it is still in use.'.format(category.title))
            return redirect(self.success_url)

        messages.success(request, 'Category "{}" has been successfully deleted'.format(category.title))
        category.delete()
        return redirect(self.success_url)



@method_decorator(login_required, name='dispatch')
class ListFigureView(ListView):
    template_name = 'figure/list.html'
    model = ProductFigure

    # Only show the items that the user 'owns'
    def get_queryset(self):
        queryset = self.model.objects.filter(owner=self.request.user)
        return queryset


@method_decorator(login_required, name='dispatch')
class CreateFigureView(CreateView):
    template_name = 'figure/create.html'
    model = ProductFigure
    form_class = ProductFigureForm
    success_url = reverse_lazy('list_figure')

    # on save, add owner
    def form_valid(self, form):
        figure = form.save(commit=False)
        figure.owner = self.request.user
        figure.save()
        return super(CreateFigureView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class DetailedFigureView(DetailView):
    template_name = 'figure/detail.html'
    model = ProductFigure


@method_decorator(login_required, name='dispatch')
class EditFigureView(UpdateView):
    template_name = 'figure/edit.html'
    model = ProductFigure
    form_class = ProductFigureForm
    success_url = reverse_lazy('list_figure')

    # Only allow ordinary user to update their own, but staff all.
    def get_queryset(self):
        queryset = super(EditFigureView, self).get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(creator=self.request.user)
        return queryset


@method_decorator(login_required, name='dispatch')
class DeleteFigureView(View):
    success_url = reverse_lazy('list_figure')

    def get(self, request, **kwargs):
        figure = get_object_or_404(ProductFigure, pk=self.kwargs['pk'])

        # Check request user is the owner or a staff member
        if not figure.is_owner(self.request.user) and not self.request.user.is_staff:
            messages.error(request, 'You do not have the authority to delete this figure.')
            return redirect(self.success_url)

        # Check the category is not in use with any products
        if Product.objects.filter(product_figure=figure) or ProductCategory.objects.filter(category_figure=figure):
            messages.warning(request, 'Figure "{}" cannot be deleted as it is still in use.'.format(figure.image.name))
            return redirect(self.success_url)

        messages.success(request, 'Figure "{}" has been successfully deleted'.format(figure.image.name))
        figure.delete()
        return redirect(self.success_url)
