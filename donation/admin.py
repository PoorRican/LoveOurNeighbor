from django.contrib.admin import ModelAdmin, StackedInline

from .models import ccPayment


class CCPaymentInline(StackedInline):
    model = ccPayment
    readonly_fields = ('payment_date', 'confirmation', 'amount', 'card_number', 'name', 'zipcode', 'auth_num', 'tx_id')
    fields = ('payment_date', 'confirmation', 'amount', 'card_number', 'name', 'zipcode', 'auth_num', 'tx_id')


class DonationAdmin(ModelAdmin):
    list_display = ('campaign', 'date', 'amount')
    search_fields = ('campaign__title', 'payment__payment_date', 'user__email', 'campaign__ministry')
    readonly_fields = ('campaign', 'amount', 'user')
    fields = ('campaign', 'amount', 'user')
    inlines = [CCPaymentInline]
