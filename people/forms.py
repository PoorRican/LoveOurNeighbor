from django import forms

from .models import User


class NewUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.fields['password2'] = forms.PasswordInput(attrs={'placeholder':
                                                                  'Password (again)'})

    def is_valid(self):
        if self.cleaned_data['password'] != self.data['password2']:
            self.add_error(None, "Passwords do not match!")
        return super(NewUserForm, self).is_valid()

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')


class UserLoginForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ('email', 'password')


class UserEditForm(forms.ModelForm):
    """Form for viewing and editing name fields in a User object.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ('first_name', 'last_name',
                  '_location', 'profile_img')
        labels = {'_location': 'Location',
                  'profile_img': 'Profile Image'}


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name',
                  'is_staff', 'is_active', 'date_joined')

    def is_valid(self):
        return super(UserAdminForm, self).is_valid()
