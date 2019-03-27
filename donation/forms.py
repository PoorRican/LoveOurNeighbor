from django import forms

from .models import PAYMENT_TYPES


class SelectPaymentForm(forms.Form):
    payment_type = forms.ChoiceField(choices=PAYMENT_TYPES)

    def __init__(self, *args, **kwargs):
        super(SelectPaymentForm, self).__init__(*args, **kwargs)
