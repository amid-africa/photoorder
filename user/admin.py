from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


from .forms import UserAdminCreationForm, UserAdminChangeForm
from .models import User

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'name', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'date_joined', 'last_login')}),
        ('Personal info', {'fields': ('name', )}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser',)}),
    )
    readonly_fields = ['date_joined', 'last_login',]

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'is_staff')}
        ),
    )
    search_fields = ('email', 'name', )
    ordering = ('email',)
    filter_horizontal = ()



admin.site.register(User, UserAdmin)

# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)
