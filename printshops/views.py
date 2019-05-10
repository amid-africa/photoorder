from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.models import Site
from django.core import serializers
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from .forms import PrintShopForm, PrintShopUserForm, PrintShopPriceListForm
from .models import PrintShop, PrintShopGroup, PrintShopUser, PrintShopPriceList
from .token import validate_confirmation_token, confirmation_token

User = get_user_model()
current_site = Site.objects.get_current()

"""Send a 'shop email' verification email"""
class PrintShopEmailConfirmationView(View):
    def get(self, request, **kwargs):
        slug = self.kwargs['slug']
        printshop = get_object_or_404(PrintShop, slug=slug)

        if not printshop.email_confirmed:
            messages.success(self.request, 'A new confirmation email has been sent to {}'.format(printshop.email))
            subject = 'Confirm Your Shop Email'
            message = render_to_string('printshop/shop_confirm_email.html', {
                'shop': printshop,
                'domain': current_site.domain,
                'sid': urlsafe_base64_encode(force_bytes(printshop.pk)),
                'token': confirmation_token(printshop.email),
            })
            printshop.email_shop(subject, message)

        return HttpResponseRedirect(reverse('details_print_shop',
                                            kwargs={'slug': printshop.slug}))


"""Verify the 'shop email' address"""
class PrintShopEmailVerifyView(View):
    success_url = reverse_lazy('details_print_shop')

    def __init__(self, **kwargs):
        if 'success_url' in kwargs:
            self.success_url = kwargs['success_url']

    def get(self, request, uidb64, token):
        try:
            # Get the print shop
            sid = urlsafe_base64_decode(uidb64).decode()
            printshop = PrintShop.objects.get(pk=sid)
            self.success_url = reverse_lazy('details_print_shop', kwargs={'slug': printshop.slug})
        except (TypeError, ValueError, OverflowError, PrintShop.DoesNotExist):
            printshop = None

        if printshop is not None and validate_confirmation_token(token, printshop.email):
            # Check the token is valid
            messages.success(self.request, '{} has been successfully confirmed.'.format(printshop.email))
            if not printshop.email_confirmed:
                printshop.email_confirmed = True
                printshop.save()
            return redirect(self.success_url)

        # If error, display it.
        return render(request, 'printshop/shop_confirm_email_failed.html', {'printshop': printshop})


@method_decorator(login_required, name='dispatch')
class EditPrintShopView(UpdateView):
    template_name = 'printshop/edit.html'
    form_class = PrintShopForm
    model = PrintShop

    """Save and get the slug to redirect"""
    def form_valid(self, form):
        printshop = form.save()
        messages.success(self.request, '\'{}\' details have been updated.'.format(printshop))
        return HttpResponseRedirect(reverse('details_print_shop',
                                            kwargs={'slug': printshop.slug}))


"""Create a new print shop"""
@method_decorator(login_required, name='dispatch')
class CreatePrintShopView(SuccessMessageMixin, CreateView):
    template_name = 'printshop/create.html'
    model = PrintShop
    form_class = PrintShopForm
    success_url = reverse_lazy('details_print_shop')
    success_message = "Print shop '%(name)s' was created successfully. Confirm the email address '%(email)s' by clicking on the link emailed to that address."
    slug = None

    def form_invalid(self, form):
        return super(CreatePrintShopView, self).form_invalid(form)

    """Get the slug for the success_url and create the user group and user"""
    def form_valid(self, form):
        printshop = form.save()
        self.slug = printshop.slug

        # Create the user Group
        group, create = PrintShopGroup.objects.get_or_create(printshop=printshop,
                    defaults={'title':'{} - User Group'.format(printshop.name)})

        # Add the current user to the group
        user, create = PrintShopUser.objects.get_or_create(group=group,
                    user=self.request.user,
                    defaults={'admin': True, 'creator': True})

        return super(CreatePrintShopView, self).form_valid(form)

    def get_success_url(self):
         return reverse('details_print_shop', kwargs={'slug': self.slug})


"""List all print shops"""
class ListPrintShopView(ListView):
    template_name = 'printshop/list.html'
    model = PrintShop


"""View print shop in detail"""
class DetailedPrintShopView(DetailView):
    template_name = 'printshop/detail.html'
    model = PrintShop

    def get_context_data(self, **kwargs):
        context = super(DetailedPrintShopView, self).get_context_data(**kwargs)

        # Only display email confirmation message if there are no other messages and user is owner or staff
        if not context['printshop'].email_confirmed:
            storage = messages.get_messages(self.request)
            if not storage and context['printshop'].is_shop_staff(self.request.user):
                messages.error(self.request, mark_safe('Shop Email address must be confirmed to prevent automatic deactivation. Check your email urgently! <a href="{}" class="btn btn-danger">Resend Confirmation Email</a>'.format(reverse('print_shop_email_confirm', kwargs={'slug': self.object.slug}))))

        # Add to context if current user is active admin or active staff.
        user_group = PrintShopGroup.objects.get(printshop=context['printshop'])
        context['admin_user'] = user_group.is_admin(self.request.user)
        context['staff_user'] = user_group.is_member(self.request.user)

        # Add to context all staff, only if current user is group member or staff user
        context['staff'] = None
        if user_group.is_member(self.request.user) or self.request.user.is_staff:
            context['staff'] = user_group.member_set()

        return context


"""Users for shops"""
@method_decorator(login_required, name='dispatch')
class PrintShopUserView(View):
    template_name = 'printshop/user.html'

    def get(self, request, **kwargs):
        slug = self.kwargs['slug']
        printshop = get_object_or_404(PrintShop, slug=slug)

        # Render a 404 page if request.user is not a shop admin
        if not printshop.is_shop_admin(self.request.user):
            raise Http404

        # Get all the staff
        staff_group = PrintShopGroup.objects.get(printshop=printshop)
        staff_users = staff_group.member_set()

        return render(self.request, self.template_name, {
            'form': PrintShopUserForm(initial={'group': staff_group}),
            'printshop': printshop,
            'staff_users': staff_users,
            'slug': slug })


    def post(self, request, **kwargs):
        data = {'is_valid': False}

        """Submitting Form"""
        if 'action' in self.request.POST:
            slug = self.kwargs['slug']
            printshop = get_object_or_404(PrintShop, slug=slug)
            printshopusers =  PrintShopGroup.objects.get(printshop=printshop).member_set()

            # Render a 404 page if request.user is not a shop admin
            if not printshop.is_shop_admin(self.request.user):
                raise Http404

            """List print shop users"""
            if self.request.POST['action'] == 'LIST':
                list = ''
                for staff in printshopusers:
                    listrow = '<tr class="row-edit {}" data-id="{}"><td>{}</td><td>{}</td>'.format(
                            'table-success' if staff.admin else '' if staff.user.is_active else 'table-danger',
                            staff.id, staff.user.name, staff.user.email)

                    listrow += '<td>{}{}</td><td>{}{}{}</td><td>{}</td>'.format(
                            staff.admin,
                            '<br/>Creator' if staff.creator else '',
                            'Customer Orders<br/>' if staff.order_notifications else '',
                            'Customer Queries<br/>' if staff.customer_notifications else '',
                            'Service Notices' if staff.service_notifications else '',
                            'Active' if staff.user.is_active else 'Disabled')

                    list += listrow
                return HttpResponse(list)


            """Get details for new user"""
            if self.request.POST['action'] == 'NEW':
                # Get the unselected users for the user select field
                existing = PrintShopGroup.objects.get(printshop=printshop).member_set().values_list('user')
                users = User.objects.filter(is_active=True).exclude(id__in=existing)

                data = {
                    'userlist': serializers.serialize('json', users, fields=["email"]),
                }


            """Get user shop user details for editing"""
            if self.request.POST['action'] == 'EDIT':
                printshopuser = get_object_or_404(PrintShopUser, id=self.request.POST['id'])

                # Get the unselected users for the user select field
                existing = PrintShopGroup.objects.get(printshop=printshop).member_set().exclude(user=printshopuser.user).values_list('user')
                #existing = PrintShopUser.objects.filter(printshop=printshop).exclude(user=printshopuser.user).values_list('user')
                users = User.objects.filter(is_active=True).exclude(id__in=existing)

                data = {
                    'id': printshopuser.id,
                    'user': printshopuser.user.id,
                    'admin': printshopuser.admin,
                    'creator': printshopuser.creator,
                    'active': printshopuser.user.is_active,
                    'order_notifications': printshopuser.order_notifications,
                    'customer_notifications': printshopuser.customer_notifications,
                    'service_notifications': printshopuser.service_notifications,
                    'userlist': serializers.serialize('json', users, fields=["email"]),
                }


            """Deactivate / reactivate current user"""
            if self.request.POST['action'] == 'DEACTIVATE':
                printshopuser = get_object_or_404(PrintShopUser, id=self.request.POST['id'], printshop=printshop)
                if printshopuser.user == self.request.user:
                    data = {'is_valid': False, 'error':'User cannot deactivate own account.'}

                else:
                    printshopuser.active = not printshopuser.active
                    printshopuser.save()
                    data = {'action': self.request.POST['action'], 'id': self.request.POST['id'], 'is_valid': True}


            """Delete current user"""
            if self.request.POST['action'] == 'Delete':
                printshopuser = get_object_or_404(PrintShopUser, id=self.request.POST['id'], printshop=printshop)
                if printshopuser.creator == False:
                    printshopuser.delete()
                    data = {'action': self.request.POST['action'], 'id': self.request.POST['id'], 'is_valid': True}


        else:
            form = PrintShopUserForm(self.request.POST)

            """Update Existing"""
            if self.request.POST['id']:
                printshopuser = get_object_or_404(PrintShopUser, id=self.request.POST['id'])
                form = PrintShopUserForm(self.request.POST, instance=printshopuser)
                if form.is_valid():
                    form.save()
                    data = {'is_valid': True}

                else:
                    data = {'is_valid': False, 'error': form.errors}


            else:
                """Create New"""
                if form.is_valid():
                    form.save()
                    data = {'is_valid': True}

                else:
                    data = {'is_valid': False, 'error': form.errors}


        # Return Response
        return JsonResponse(data)


"""Assign priceslists to the printshop"""
class CreatePrintShopPriceListView(CreateView):
    template_name = 'printshop/pricelist.html'
    model = PrintShopPriceList
    form_class = PrintShopPriceListForm
    printshop = None

    # Set the success url to be the current url
    def get_success_url(self):
        return self.request.path

    # Set the printshop form field from the printshop slug and raise a 404 if not shop admin
    def get_initial(self):
        self.printshop = get_object_or_404(PrintShop, slug=self.kwargs.get('slug'))
        if not self.printshop.is_shop_admin(self.request.user) and not self.request.user.is_staff:
            raise Http404
        return {
            'printshop':self.printshop,
        }

    #Add printshop data to the context
    def get_context_data(self, *args, **kwargs):
        context = super(CreatePrintShopPriceListView, self).get_context_data(*args, **kwargs)
        context['printshop'] = self.printshop
        return context


"""Delete a pricelist from a printshop"""
class DeletePrintShopPriceListView(View):
    def post(self, request, **kwargs):

        # Get the printshop
        slug = self.kwargs['slug']
        printshop = get_object_or_404(PrintShop, slug=slug)

        # Render a 404 page if request.user is not a shop admin
        if not printshop.is_shop_admin(self.request.user):
            raise Http404

        # Get the printshoppricelist instance
        printshoppricelist = get_object_or_404(PrintShopPriceList, pk=self.request.POST['id'], printshop=printshop)

        # Delete the instance
        messages.success(request, "Price list '{}' has been removed from print shop '{}'.".format(printshoppricelist.pricelist, printshoppricelist.printshop))
        printshoppricelist.delete()

        return JsonResponse({'is_valid': True})
