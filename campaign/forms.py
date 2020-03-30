from django import forms

from frontend.utils import sanitize_wysiwyg_input
from tag.models import Tag

from .models import Campaign
from .utils import create_campaign_dir, campaign_banner_dir


class NewCampaignForm(forms.ModelForm):
    """ Form for creating a new Campaign object.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """

    def __init__(self, *args, **kwargs):
        super(NewCampaignForm, self).__init__(*args, **kwargs)
        self.fields['tags'] = forms.CharField(max_length=256, required=False)

    def save(self, commit=True) -> Campaign:
        if 'ministry' in self.initial.keys():
            self.instance.ministry = self.initial.get('ministry')
        elif 'ministry' in self.data.keys():
            self.instance.ministry = self.data.get('ministry')
        else:
            raise KeyError("No value for 'ministry' found")

        # object must 'exist' before ForeignKey relationships
        super(NewCampaignForm, self).save(commit=False)
        self.instance.save()

        # object must 'exist' before ForeignKey relationships
        super(NewCampaignForm, self).save(commit=False)

        create_campaign_dir(self.instance)

        Tag.process_tags(self.instance, self.data.get('tags', ''))

        # Cleaned Data
        # for some reason the `clean_description` overwritten method nullified the value
        self.instance.content = sanitize_wysiwyg_input(self.data.get('content', ''))

        return super(NewCampaignForm, self).save(commit=commit)

    class Meta:
        model = Campaign
        fields = ('title', 'start_date', 'end_date', 'goal',
                  'banner_img', 'content',)
        widgets = {'content': forms.Textarea(attrs={'id': 'tinyEditor'}),
                   'start_date': forms.TextInput(attrs={'class': 'pickadate'}),
                   'end_date': forms.TextInput(attrs={'class': 'pickadate'})}
        labels = {'goal': 'Donation Goal'}


class CampaignEditForm(NewCampaignForm):
    """Form for viewing and editing fields in a Campaign object.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """

    def __init__(self, *args, **kwargs):
        super(CampaignEditForm, self).__init__(*args, **kwargs)
        self.fields['selected_banner_img'] = forms.CharField(max_length=64, required=False)

    def save(self, commit=True) -> Campaign:
        banner_img = self.data.get('selected_banner_img', False)
        if banner_img:
            self.instance.banner_img = campaign_banner_dir(self.instance, banner_img)

        Tag.process_tags(self.instance, self.data.get('tags', ''))

        # Cleaned Data
        # for some reason the `clean_description` overwritten method nullified the value
        self.instance.content = sanitize_wysiwyg_input(self.data.get('content', ''))

        return super(forms.ModelForm, self).save(commit=commit)
