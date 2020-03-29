from django import forms

from news.models import Post


class NewPostForm(forms.ModelForm):
    """Form for creating Post objects.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """

    class Meta:
        model = Post
        fields = ('title', 'content',
                  'attachment')
        widgets = {'content': forms.Textarea(attrs={'id': 'tinyEditor'})}


class NewsEditForm(forms.ModelForm):
    """Form for viewing and editing fields in a Post object.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """

    def __init__(self, *args, **kwargs):
        super(NewsEditForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Post
        fields = ('title', 'content',
                  'attachment',)
        widgets = {'content': forms.Textarea(attrs={'id': 'tinyEditor'})}
