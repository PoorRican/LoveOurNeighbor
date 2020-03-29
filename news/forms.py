from django import forms

from news.models import NewsPost


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
                  'attachment',
                  )
        widgets = {'content': forms.Textarea(attrs={'id': 'tinyEditor'})}
