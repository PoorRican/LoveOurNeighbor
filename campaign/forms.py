from django import forms

from .models import Campaign


class CampaignEditForm(forms.ModelForm):
    """Form for viewing and editing fields in a Campaign object.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """
    tags = forms.CharField(max_length=256, required=False)

    def __init__(self, *args, **kwargs):
        tags = ''
        if 'instance' in kwargs:
            tags = ', '.join([str(i) for i in kwargs['instance'].tags.all()])
        initial = {'tags': tags}
        if 'initial' in kwargs:
            initial = {**kwargs['initial'], **initial}
        super(CampaignEditForm, self).__init__(*args, **kwargs,
                                               initial=initial)

    class Meta:
        model = Campaign
        fields = ('title', 'start_date', 'end_date', 'goal',
                  'banner_img', 'content',
                  # TODO: create ui for editing `img_path`
                  )
        widgets = {'content': forms.Textarea(),
                   }
        labels = {'goal': 'Donation Goal'}
