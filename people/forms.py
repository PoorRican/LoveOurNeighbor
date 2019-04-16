from django import forms

from .models import User


class NewUserForm(forms.ModelForm):
    password2 = forms.PasswordInput()

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)

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
        fields = ('first_name', 'last_name', 'display_name',
                  '_location', '_profile_img', 'profile_img_url')
        labels = {'_location': 'Location',
                  '_profile_img': 'Profile Image'}


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'display_name',
                  'is_staff', 'is_active', 'date_joined')

    def is_valid(self):
        return super(UserAdminForm, self).is_valid()
