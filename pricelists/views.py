from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
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

from decimal import Decimal

from .forms import PriceListForm, PriceListCurrencyForm, PriceListProductForm, PriceListProductEditForm
from .models import PriceList, PriceListCurrency, PriceListCurrencyRate, PriceListProduct, PriceListProductPrice

User = get_user_model()

@method_decorator(login_required, name='dispatch')
class ListCurrencyView(ListView):
    template_name = 'currency/list.html'
    model = PriceListCurrency

    # Order the list by the title
    def get_queryset(self):
        queryset = super(ListCurrencyView, self).get_queryset()
        queryset = queryset.order_by('title')
        return queryset


@method_decorator(login_required, name='dispatch')
class CreateCurrencyView(CreateView):
    template_name = 'currency/create.html'
    model = PriceListCurrency
    form_class = PriceListCurrencyForm
    success_url = reverse_lazy('list_currency')
    pricelist = None

    # Set the success url to be the current url
    def get_success_url(self):
        return self.request.path

    # Set the pricelist form field from the product pk and raise a 404 if not owner
    def get_initial(self):
        self.pricelist = get_object_or_404(PriceList, pk=self.kwargs.get('pk'))
        if not self.pricelist.is_owner(self.request.user) and not self.request.user.is_staff:
            raise Http404
        return {
            'pricelist':self.pricelist,
        }

    #Add pricelist data to the context
    def get_context_data(self, *args, **kwargs):
        context = super(CreateCurrencyView, self).get_context_data(*args, **kwargs)
        context['pricelist'] = self.pricelist
        return context

    # on save, inital rate
    def form_valid(self, form):
        currency = form.save()
        PriceListCurrencyRate.objects.create(currency=currency,
                        rate=form.cleaned_data['baserate'])
        return super(CreateCurrencyView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class EditCurrencyView(UpdateView):
    template_name = 'currency/edit.html'
    model = PriceListCurrency
    form_class = PriceListCurrencyForm
    success_url = reverse_lazy('create_currency')
    currencyrate = None

    # Set the base price to the last
    def get_initial(self):
        self.currencyrate = PriceListCurrencyRate.objects.order_by('date_effective').filter(currency=self.get_object()).last()
        return { 'baserate':self.currencyrate.rate, }

    def form_valid(self, form):
        # Save the main form
        currency = form.save()

        # Set the success_url with the pricelist pk
        print(currency)
        self.success_url = reverse_lazy('create_currency', kwargs={'pk': currency.pricelist.pk})

        # Create a new price if it has changed and not a base currency
        if self.currencyrate.rate != form.cleaned_data['baserate'] and not currency.base:
            PriceListCurrencyRate.objects.create(currency=currency,
                            rate=form.cleaned_data['baserate'])

        return super(EditCurrencyView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class DeleteCurrencyView(View):
    success_url = reverse_lazy('create_currency')

    def get(self, request, **kwargs):
        currency = get_object_or_404(PriceListCurrency, pk=self.kwargs['pk'])

        self.success_url = reverse_lazy('create_currency', kwargs={'pk': currency.pricelist.pk})

        # Check request user is the owner or a staff member
        if not currency.pricelist.is_owner(self.request.user) and not self.request.user.is_staff:
            messages.error(request, 'You do not have the authority to delete this currency.')
            return redirect(self.success_url)

        if currency.base:
            messages.error(request, 'Base currency cannot be deleted.')
            return redirect(self.success_url)

        messages.success(request, 'Currency "{}" has been successfully deleted from pricelist "{}"'.format(currency.title, currency.pricelist))
        currency.delete()
        return redirect(self.success_url)


@method_decorator(login_required, name='dispatch')
class ListPriceListView(ListView):
    template_name = 'pricelist/list.html'
    model = PriceList

    # Show users lists only if not staff
    def get_queryset(self):
        queryset = super(ListPriceListView, self).get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(creator=self.request.user)
        return queryset


@method_decorator(login_required, name='dispatch')
class CreatePriceListView(CreateView):
    template_name = 'pricelist/create.html'
    model = PriceList
    form_class = PriceListForm
    success_url = reverse_lazy('list_pricelist')

    # on save, add owner and base currency and base rate
    def form_valid(self, form):
        pricelist = form.save(commit=False)
        pricelist.owner = self.request.user
        pricelist.save()
        currency = PriceListCurrency.objects.create(pricelist=pricelist,
                        title="BASE", code='BAS', symbol='$', base=True)
        PriceListCurrencyRate.objects.create(currency=currency,
                        rate=Decimal('1.00'))
        return super(CreatePriceListView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class DetailedPriceListView(DetailView):
    template_name = 'pricelist/detail.html'
    model = PriceList


@method_decorator(login_required, name='dispatch')
class EditPriceListView(UpdateView):
    template_name = 'pricelist/edit.html'
    model = PriceList
    form_class = PriceListForm
    success_url = reverse_lazy('list_pricelist')

    # Only the owner or staff can edit
    def dispatch(self, request, *args, **kwargs):
        if not self.get_object().is_owner(self.request.user) and not self.request.user.is_staff:
            raise Http404()
        return super(EditPriceListView, self).dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class DeletePriceListView(View):
    success_url = reverse_lazy('list_pricelist')

    def get(self, request, **kwargs):
        pricelist = get_object_or_404(PriceList, pk=self.kwargs['pk'])

        # Check request user is the owner or a staff member
        if not pricelist.is_owner(self.request.user) and not self.request.user.is_staff:
            messages.error(request, 'You do not have the authority to delete this pricelist.')
            return redirect(self.success_url)

        messages.success(request, 'Pricelist "{}" has been successfully deleted.'.format(pricelist.title))
        pricelist.delete()
        return redirect(self.success_url)


@method_decorator(login_required, name='dispatch')
class CreatePriceListProductView(CreateView):
    template_name = 'pricelistproduct/create.html'
    model = PriceListProduct
    form_class = PriceListProductForm
    pricelist = None

    # Set the success url to be the current url
    def get_success_url(self):
        return self.request.path

    # Set the pricelist form field from the product pk and raise a 404 if not owner
    def get_initial(self):
        self.pricelist = get_object_or_404(PriceList, pk=self.kwargs.get('pk'))
        if not self.pricelist.is_owner(self.request.user) and not self.request.user.is_staff:
            raise Http404
        return {
            'pricelist':self.pricelist,
            'user':self.request.user,
        }

    #Add pricelist data to the context
    def get_context_data(self, *args, **kwargs):
        context = super(CreatePriceListProductView, self).get_context_data(*args, **kwargs)
        context['pricelist'] = self.pricelist
        return context

    # on save, inital base price
    def form_valid(self, form):
        product = form.save()
        PriceListProductPrice.objects.create(listproduct=product,
                        price=form.cleaned_data['baseprice'])
        return super(CreatePriceListProductView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class EditPriceListProductView(UpdateView):
    template_name = 'pricelistproduct/edit.html'
    model = PriceListProduct
    form_class = PriceListProductEditForm
    success_url = reverse_lazy('create_pricelistproduct')
    productprice = None

    # Make sure the pricelist belongs to the user
    def get_queryset(self):
        queryset = super(EditPriceListProductView, self).get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(pricelist__creator=self.request.user)
        return queryset

    # Set the base price to the last
    def get_initial(self):
        self.productprice = PriceListProductPrice.objects.order_by('date_effective').filter(listproduct=self.get_object()).last()
        return {
            'baseprice':self.productprice.price,
        }

    def form_valid(self, form):
        product = form.save()

        self.success_url = reverse_lazy('create_pricelistproduct', kwargs={'pk': product.pricelist.pk})

        # Create a new price if it has changed
        if self.productprice.price != form.cleaned_data['baseprice']:
            productprice = PriceListProductPrice.objects.create(
                            listproduct=product,
                            price=form.cleaned_data['baseprice'])

        return super(EditPriceListProductView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class DeletePriceListProductView(View):
    success_url = reverse_lazy('create_pricelistproduct')

    def get(self, request, **kwargs):
        product = get_object_or_404(PriceListProduct, pk=self.kwargs['pk'])

        self.success_url = reverse_lazy('create_pricelistproduct', kwargs={'pk': product.pricelist.pk})

        # Check request user is the owner or a staff member
        if not product.pricelist.is_owner(self.request.user) and not self.request.user.is_staff:
            messages.error(request, 'You do not have the authority to delete this product.')
            return redirect(self.success_url)

        messages.success(request, 'Product "{}" has been successfully deleted from pricelist "{}"'.format(product.product.title, product.pricelist))
        product.delete()
        return redirect(self.success_url)


@method_decorator(login_required, name='dispatch')
class ListRateView(ListView):
    pass


@method_decorator(login_required, name='dispatch')
class CreateRateView(CreateView):
    pass


@method_decorator(login_required, name='dispatch')
class EditRateView(UpdateView):
    pass
