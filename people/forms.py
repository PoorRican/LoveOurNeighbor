from django import forms

from .models import User
from .utils import user_profile_img_dir


class NewUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.fields['password2'] = forms.CharField(widget=forms.PasswordInput(), label='Password (again)')

    def is_valid(self):
        # Check matching passwords
        if self.data['password'] != self.data['password2']:
            self.add_error('password', "Passwords do not match.")
            self.add_error('password2', "Passwords do not match.")

        # Check unique email and catch emails that have been used for donations
        try:
            user = User.objects.get(email=self.data['email'])
            if not user.is_verified:
                user.is_verified = True  # assume donor emails already verified
                self.instance = user
            else:
                err = forms.ValidationError('This email (%(email)s) has already been used!',
                                            code='existing_email', params={'email': user.email})
                self.add_error('email', err)
        except User.DoesNotExist:
            pass

        return super(NewUserForm, self).is_valid()

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')
        widgets = {'password': forms.PasswordInput()}


class UserLoginForm(forms.ModelForm):
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            try:
                self.user = User.authenticate_user(email, password)
            except User.DoesNotExist:
                err = forms.ValidationError('%(email)s was not found!', code='email', params={'email': email})
                self.add_error('email', err)

            # login successful
            if self.user and self.confirm_login_allowed(self.user):
                return self.cleaned_data

            # incorrect password
            else:
                err = forms.ValidationError('Incorrect password given for %(email)s',
                                            code='password', params={'email': email})
                self.add_error('password', err)

    @staticmethod
    def confirm_login_allowed(user):
        if user.is_active and (user.is_verified or user.is_staff):
            if not user.is_verified:
                # staff users will not have to verify their email
                user.is_verified = True
                user.save()
            return True
        raise forms.ValidationError('Your account needs to be verified!', code='inactive')

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
        # Process Profile Images
        # TODO: prioritize uploaded image over `selected_profile_img`
        _img = self.data.get('selected_profile_img', False)
        if _img:
            self.instance.profile_img = user_profile_img_dir(self.instance, _img)
        return super(UserEditForm, self).save(commit=commit)

    class Meta:
        model = User
        fields = ('first_name', 'last_name',
                  'profile_img')
        labels = {'profile_img': 'Profile Image'}


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name',
                  'is_staff', 'is_active', 'date_joined')

    def is_valid(self):
        return super(UserAdminForm, self).is_valid()
