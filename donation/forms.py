from django import forms


from .models import ccPayment, PAYMENT_TYPES


class SelectPaymentForm(forms.Form):
    payment_type = forms.ChoiceField(widget=forms.RadioSelect,
                                     choices=PAYMENT_TYPES)

    def __init__(self, *args, **kwargs):
        super(SelectPaymentForm, self).__init__(*args, **kwargs)


class ccPaymentForm(forms.ModelForm):
    class Meta:
        model = ccPayment
        fields = ('first_name', 'last_name',
                  'address', 'state', 'city', 'zipcode', 'country',
                  'amount', 'card_number', 'ccv2')
