from django import forms

from frontend.utils import sanitize_wysiwyg_input
from tag.models import Tag

from .utils import (
    ministry_banner_dir,
    ministry_profile_image_dir,
    create_ministry_dirs,
)

from .models import MinistryProfile


class NewMinistryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewMinistryForm, self).__init__(*args, **kwargs)
        self.fields['tags'] = forms.CharField(max_length=256, required=False)

    def save(self, commit=True) -> MinistryProfile:
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
        super(NewMinistryForm, self).save(commit=False)
        self.instance.save()

        create_ministry_dirs(self.instance)
        # Handle object relationships
        if self.data.get('address', False):
            self.instance.location = self.data['address']

        Tag.process_tags(self.instance, self.data.get('tags', ''))

        # Cleaned Data
        # for some reason the `clean_description` overwritten method nullified the value
        self.instance.description = sanitize_wysiwyg_input(self.data.get('description', ''))

        return super(NewMinistryForm, self).save(commit=commit)

    class Meta:
        model = MinistryProfile
        fields = ('profile_img', 'banner_img',
                  'name', 'address', 'phone_number', 'website', 'founded',
                  'facebook', 'instagram', 'youtube', 'twitter',
                  'admin', 'description', 'staff',)
        exclude = ('admin',)
        widgets = {'description': forms.Textarea(attrs={'rows': 20,
                                                        'cols': 80}),
                   'address': forms.Textarea(attrs={'rows': 3,
                                                    'cols': 30,
                                                    'class': 'materialize-textarea'}),
                   'founded': forms.TextInput(attrs={'class': 'pickadate'})}
        labels = {'img_path': 'Banner Image',
                  'founded': 'Date Founded',
                  'phone_number': 'Phone'}


class MinistryEditForm(NewMinistryForm):
    """Form for viewing and editing fields in a MinistryProfile object.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """

    def __init__(self, *args, **kwargs):
        super(MinistryEditForm, self).__init__(*args, **kwargs)
        self.fields['selected_banner_img'] = forms.CharField(max_length=64, required=False)
        self.fields['selected_profile_img'] = forms.CharField(max_length=64, required=False)

    def save(self, commit=True) -> MinistryProfile:
        """ Handles related data such as ForeignKey relationships and media directories.

        Notes
        -----
            The admin attribute is blind to malicious actions; the admin attribute MUST be verified
        before the model can be saved.
        """
        # move to a new directory if name change
        if self.instance.name != self.data.get('name'):
            self.instance.rename(self.data.get('name'))

        # handle selection of previously uploaded media
        _img = self.data.get('selected_banner_img', False)
        if _img:
            self.instance.banner_img = ministry_banner_dir(self.instance, _img)

        _img = self.data.get('selected_profile_img', False)
        if _img:
            self.instance.profile_img = ministry_profile_image_dir(self.instance, _img)

        # Handle object relationships
        if self.data.get('address', False):
            self.instance.location = self.data['address']

        Tag.process_tags(self.instance, self.data.get('tags', ''))

        # Cleaned Data
        # for some reason the `clean_description` overwritten method nullified the value
        self.instance.description = sanitize_wysiwyg_input(self.data.get('description', ''))

        return super(forms.ModelForm, self).save(commit=commit)
