from django import forms

from .models import MinistryProfile, Campaign, NewsPost


class MinistryEditForm(forms.ModelForm):
    """Form for viewing and editing name fields in a User object.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """

    def __init__(self, *args, **kwargs):
        super(MinistryEditForm, self).__init__(*args, **kwargs)

    class Meta:
        model = MinistryProfile
        fields = ('name', 'address', 'phone_number',
                  'admin', 'reps', 'img_path',
                  'website', 'founded', 'description')
        exclude = ('admin',)


class CampaignEditForm(forms.ModelForm):
    """Form for viewing and editing name fields in a User object.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """

    def __init__(self, *args, **kwargs):
        super(CampaignEditForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Campaign
        fields = ('title', 'start_date', 'end_date',
                  'goal', 'content', 'img_path',
                  # TODO: create ui for editing `img_path`
                  )


class NewsEditForm(forms.ModelForm):
    """Form for viewing and editing name fields in a User object.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """

    def __init__(self, *args, **kwargs):
        super(NewsEditForm, self).__init__(*args, **kwargs)

    class Meta:
        model = NewsPost
        fields = ('title', 'content',
                  # TODO: create ui for editing `img_path`
                  )
