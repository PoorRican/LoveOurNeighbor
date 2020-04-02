from django import forms

from .models import Post


class NewPostForm(forms.ModelForm):
    """Form for creating Post objects.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['media'] = forms.FileField(required=False)

    def clean_media(self):
        _data = self.data.getlist('media')
        while '' in _data:
            _data.remove('')
        self.cleaned_data['media'] = _data

    class Meta:
        model = Post
        fields = ('title', 'content')
        widgets = {'content': forms.Textarea(attrs={'id': 'tinyEditor'})}


class PostEditForm(NewPostForm):
    """Form for viewing and editing fields in a Post object.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """
    pass
