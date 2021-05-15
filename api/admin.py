from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import AkvelonUser, Transaction


@admin.register(AkvelonUser)
class AkvelonUserAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'first_name',
        'last_name',
        'is_admin'
    ]

    readonly_fields = [
        'password'
    ]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'user_link',
        'date',
        'amount'
    ]

    """
        Method for displaying the link to user model instead of user id
        (example 9.1 in "Django Admin Cookbook")
    """
    def user_link(self, obj):
        display_text = ", ".join([
            "<a href={}>{}</a>".format(
                reverse('admin:{}_{}_change'.format(obj._meta.app_label, obj.user._meta.model_name),
                        args=(obj.user.pk,)),
                obj.user.first_name + ' ' + obj.user.last_name)
        ])
        if display_text:
            return mark_safe(display_text)
        return "-"
