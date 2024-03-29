from django import forms

from tag.models import Tag

from .models import BaseProfile
from .utils import sanitize_wysiwyg_input, generic_banner_img_dir, generic_profile_img_dir


class NewProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'] = forms.CharField(max_length=256, required=False)

    def save(self, commit=True) -> BaseProfile:
        """ Handles related data such as ForeignKey relationships and media directories.

        Notes
        -----
            The admin attribute is blind to malicious actions; the admin attribute MUST be verified
        before the model can be saved.
        """
        if 'admin' in self.initial.keys():
            self.instance.admin = self.initial.get('admin')
        elif 'admin' in self.data.keys():
            self.instance.admin = self.data.get('admin')
        else:
            raise KeyError("No value for 'admin' found")

        # object must 'exist' before ForeignKey relationships
        super().save(commit=False)
        self.instance.save()

        # Handle object relationships
        Tag.process_tags(self.instance, self.data.get('tags', ''))

        # Cleaned Data
        # for some reason the `clean_description` overwritten method nullified the value
        self.instance.description = sanitize_wysiwyg_input(self.data.get('description', ''))

        return super().save(commit=commit)

    class Meta:
        abstract = True
        fields = ('profile_img', 'banner_img',
                  'name', 'address', 'phone_number', 'website', 'founded',
                  'facebook', 'instagram', 'youtube', 'twitter',
                  'admin', 'description', 'staff',)
        exclude = ('admin',)
        widgets = {'description': forms.Textarea(attrs={'id': 'tinyEditor'}),
                   'address': forms.Textarea(attrs={'rows': 3,
                                                    'cols': 30,
                                                    'class': 'materialize-textarea'}),
                   'founded': forms.TextInput(attrs={'class': 'pickadate', 'required': True})}
        labels = {'img_path': 'Banner Image',
                  'founded': 'Date Founded',
                  'phone_number': 'Phone'}


class ProfileEditForm(NewProfileForm):
    """Form for viewing and editing fields in a Profile object.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['selected_banner_img'] = forms.CharField(max_length=64, required=False)
        self.fields['selected_profile_img'] = forms.CharField(max_length=64, required=False)

    def save(self, commit=True) -> BaseProfile:
        """ Handles related data such as ForeignKey relationships and media directories.

        Notes
        -----
            The admin attribute is blind to malicious actions; the admin attribute MUST be verified
        before the model can be saved.
        """
        # move to a new directory if name change
        # TODO: make `Ministry.rename` work w/ S3 storage
        # if self.instance.name != self.data.get('name'):
        #     self.instance.rename(self.data.get('name'))

        # handle selection of previously uploaded media
        _img = self.data.get('selected_banner_img', False)
        if _img:
            self.instance.banner_img = generic_banner_img_dir(self.instance, _img)

        _img = self.data.get('selected_profile_img', False)
        if _img:
            self.instance.profile_img = generic_profile_img_dir(self.instance, _img)

        # Handle object relationships
        Tag.process_tags(self.instance, self.data.get('tags', ''))

        # Cleaned Data
        # for some reason the `clean_description` overwritten method nullified the value
        self.instance.description = sanitize_wysiwyg_input(self.data.get('description', ''))

        return super(forms.ModelForm, self).save(commit=commit)

    class Meta(NewProfileForm.Meta):
        widgets = {'name': forms.TextInput(attrs={'required': True, 'readonly': True}),
                   'description': forms.Textarea(attrs={'id': 'tinyEditor'}),
                   'address': forms.Textarea(attrs={'rows': 3,
                                                    'cols': 30,
                                                    'class': 'materialize-textarea'}),
                   'founded': forms.TextInput(attrs={'class': 'pickadate', 'required': True})}


class BaseRepManagementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reps'] = forms.CharField(max_length=512, required=False)
        self.fields['requests'] = forms.CharField(max_length=512, required=False)

    def save(self, commit=True) -> BaseProfile:
        reps = self.data.get('reps', '').split(', ')
        reqs = self.data.get('requests', '').split(', ')

        # promote reps
        for email in reps:
            if email in [i.email for i in self.instance.requests.all()]:
                self.instance.add_representative(email)
        # demote reps
        for email in [i.email for i in self.instance.reps.all()]:
            if email not in reps:
                self.instance.remove_representative(email)

        # delete requests
        for user in self.instance.requests.all():
            if user.email not in reqs:
                self.instance.delete_request(user.email)

        return super().save(commit=commit)

    class Meta:
        abstract = True
        exclude = ('profile_img', 'banner_img',
                   'name', 'address', 'phone_number', 'website', 'founded',
                   'facebook', 'instagram', 'youtube', 'twitter',
                   'admin', 'description', 'staff',
                   'reps', 'requests')
