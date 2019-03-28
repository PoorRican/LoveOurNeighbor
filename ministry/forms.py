from django import forms

from .models import MinistryProfile, Campaign, NewsPost, Comment


DATE_SEL = ('Year', 'Month', 'Day')


class MinistryEditForm(forms.ModelForm):
    """Form for viewing and editing fields in a MinistryProfile object.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """

    def __init__(self, *args, **kwargs):
        super(MinistryEditForm, self).__init__(*args, **kwargs)

    class Meta:
        model = MinistryProfile
        fields = ('img_path',
                  'name', 'address', 'phone_number', 'website', 'founded',
                  'admin', 'reps', 'description')
        exclude = ('admin',)
        widgets = {'founded': forms.SelectDateWidget(empty_label=DATE_SEL),
                   'description': forms.Textarea(attrs={'rows': 20,
                                                        'cols': 80}),
                   'address': forms.Textarea(attrs={'rows': 3,
                                                    'cols': 30}),
                   }
        labels = {'img_path': 'Banner Image'}


class CampaignEditForm(forms.ModelForm):
    """Form for viewing and editing fields in a Campaign object.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """

    def __init__(self, *args, **kwargs):
        super(CampaignEditForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Campaign
        fields = ('title', 'start_date', 'end_date', 'goal',
                  'img_path', 'content',
                  # TODO: create ui for editing `img_path`
                  )
        widgets = {'start_date': forms.SelectDateWidget(empty_label=DATE_SEL),
                   'end_date': forms.SelectDateWidget(empty_label=DATE_SEL),
                   'content': forms.Textarea(),
                   }
        labels = {'img_path': 'Banner Image'}


class NewsEditForm(forms.ModelForm):
    """Form for viewing and editing fields in a NewsPost object.

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
        widgets = {'content': forms.Textarea(attrs={'rows': 20,
                                                    'cols': 80})}


class CommentForm(forms.ModelForm):
    """Form for viewing and editing fields in a Comment object.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Comment
        fields = ('ministry', 'campaign', 'news_post',
                  'user',
                  'content',)
        exclude = ('ministry', 'campaign', 'news_post',
                   'user')
