from django import forms

from .models import User
from .utils import user_profile_img_dir


class NewUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.fields['password2'] = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':
                                                                                         'Password (again)'}))

    def is_valid(self):
        # Check matching passwords (this is redundant of client-side validation)
        if self.data['password'] != self.data['password2']:
            self.add_error('password', "Passwords do not match.")

        # Check unique email and catch emails that have been used for donations
        try:
            user = User.objects.get(email=self.data['email'])
            if not user.is_verified:
                user.is_verified = True  # assume donor emails already verified
                self.instance = user
        except User.DoesNotExist:
            pass

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
        self.fields['selected_profile_img'] = forms.CharField(required=False)

    def save(self, commit=True):
        """
        Processes special data used for updating profile:
            - Calls the setter `User.location`
            - Processes selection of previous profile images.
                Any uploaded file takes precedence over any 'selected' value.

        Parameters
        ----------
        commit:
            Passed to `forms.ModelForm.save`

        Returns
        -------
        Value returned by `forms.ModelForm.save`
        """
        # Process Location
        _location = self.data.get('_location', False)
        if _location:
            self.instance.location = _location

        # Process Profile Images
        _img = self.data.get('selected_profile_img', False)
        if _img:
            self.instance.profile_img = user_profile_img_dir(self.instance, _img)
        return super(UserEditForm, self).save(commit=commit)

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
