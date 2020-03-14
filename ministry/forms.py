from os import path, rename

from django import forms
from django.conf import settings

from frontend.utils import sanitize_wysiwyg_input
from people.models import User
from tag.models import Tag

from .models import DEFAULT_PROFILE_IMG
from .utils import (
    dedicated_ministry_dir,
    ministry_banner_dir,
    ministry_profile_image_dir,
    create_ministry_dir,
)

from .models import MinistryProfile


class MinistryEditForm(forms.ModelForm):
    """Form for viewing and editing fields in a MinistryProfile object.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """

    def __init__(self, *args, **kwargs):
        super(MinistryEditForm, self).__init__(*args, **kwargs)
        self.fields['tags'] = forms.CharField(max_length=256, required=False)
        self.fields['selected_banner_img'] = forms.CharField(max_length=64, required=False)
        self.fields['selected_profile_img'] = forms.CharField(max_length=64, required=False)

    def save(self, commit=True) -> MinistryProfile:
        """ Handles related data such as ForeignKey relationships and media directories.

        Notes
        -----
            The admin attribute is blind to malicious actions; the admin attribute MUST be verified
        before the model can be saved.
        """
        # Check if `self.instance` is a new object
        new_object = False
        try:
            self.instance.admin
        except User.DoesNotExist:
            new_object = True

        # called during `views.create_ministry`
        if new_object:
            if 'admin' in self.initial.keys():
                self.instance.admin = self.initial.get('admin')
            elif 'admin' in self.data.keys():
                self.instance.admin = self.data.get('admin')
            else:
                raise KeyError("No value for 'admin' found")

            # object must 'exist' before ForeignKey relationships
            super(MinistryEditForm, self).save(commit=False)

            create_ministry_dir(self.instance)

        # Called from admin_panel view
        else:
            # move to a new directory if name change
            if self.instance.name != self.data.get('name'):
                _old_dir = dedicated_ministry_dir(self.instance)
                _old_dir = path.join(settings.MEDIA_ROOT, _old_dir)
                _new_dir = dedicated_ministry_dir(self.data.get('name'))
                _new_dir = path.join(settings.MEDIA_ROOT, _new_dir)

                try:
                    rename(_old_dir, _new_dir)
                    # update object media file path attributes
                    if self.instance.banner_img:
                        _img = path.basename(self.instance.banner_img.path)
                        self.instance.banner_img.path = ministry_banner_dir(self.instance, _img)

                    if self.instance.profile_img and self.instance.profile_img.path != DEFAULT_PROFILE_IMG:
                        _img = path.basename(self.instance.profile_img.path)
                        _img = ministry_profile_image_dir(self.instance, _img)
                        self.instance.profile_img = _img
                except FileNotFoundError:
                    # assume there is no dedicated content. This is a redundant catchall.
                    create_ministry_dir(self.instance)

            # handle selection of previously uploaded media
            _img = self.data.get('selected_banner_img', False)
            if _img:
                self.instance.banner_img = ministry_banner_dir(self.instance, _img)

            _img = self.data.get('selected_profile_img', False)
            if _img:
                self.instance.profile_img = ministry_profile_image_dir(self.instance, _img)

        # Handle object relationships
        if self.data.get('address', False):
            self.data['location'] = self.data['address']

        Tag.process_tags(self.instance, self.data.get('tags', ''))

        # Cleaned Data
        # for some reason the `clean_description` overwritten method nullified the value
        self.instance.description = sanitize_wysiwyg_input(self.data.get('description', ''))

        return super(MinistryEditForm, self).save(commit=commit)

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
                   'founded': forms.TextInput(attrs={'class': 'datepicker'}),
                   }
        labels = {'img_path': 'Banner Image',
                  'founded': 'Date Founded',
                  'phone_number': 'Phone',
                  }
