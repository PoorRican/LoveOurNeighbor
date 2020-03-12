from django import forms

from frontend.utils import sanitize_wysiwyg_input
from ministry.models import MinistryProfile
from tag.models import Tag

from .models import Campaign
from .utils import create_campaign_dir, campaign_banner_dir


class CampaignEditForm(forms.ModelForm):
    """Form for viewing and editing fields in a Campaign object.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """

    def __init__(self, *args, **kwargs):
        super(CampaignEditForm, self).__init__(*args, **kwargs)
        self.fields['tags'] = forms.CharField(max_length=256, required=False)
        self.fields['selected_banner_img'] = forms.CharField(max_length=64, required=False)

    def clean_content(self):
        self.cleaned_data['content'] = sanitize_wysiwyg_input(self.cleaned_data['content'])

    def save(self, commit=True):
        new_object = False
        try:
            self.instance.ministry
        except MinistryProfile.DoesNotExist:
            new_object = True

        # called during `views.create_campaign`
        if new_object:
            if 'ministry' in self.initial.keys():
                self.instance.ministry = self.initial.get('ministry')
            elif 'ministry' in self.data.keys():
                self.instance.ministry = self.data.get('ministry')
            else:
                raise KeyError("No value for 'ministry' found")

            # object must 'exist' before ForeignKey relationships
            super(CampaignEditForm, self).save(commit=False)

            create_campaign_dir(self.instance)

        # called from `views.admin_panel`
        else:
            banner_img = self.data.get('selected_banner_img', False)
            if banner_img:
                self.instance.banner_img = campaign_banner_dir(self.instance, banner_img)

        Tag.process_tags(self.instance, self.data.get('tags', ''))

        return super(CampaignEditForm, self).save(commit=commit)

    class Meta:
        model = Campaign
        fields = ('title', 'start_date', 'end_date', 'goal',
                  'banner_img', 'content',
                  # TODO: create ui for editing `img_path`
                  )
        widgets = {'content': forms.Textarea(),
                   }
        labels = {'goal': 'Donation Goal'}
