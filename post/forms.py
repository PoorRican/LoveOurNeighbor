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
    class Meta(NewPostForm.Meta):
        widgets = {'content': forms.Textarea(attrs={'id': 'tinyEditor'}),
                   'title': forms.TextInput(attrs={'readonly': True, 'required': True})}


class QuickPostForm(NewPostForm):
    """
    Form used in the `quick_post` jinja2 macro.

    This changes the `content` Field to use a basic text editor.

    See Also
    --------
    "templates/macros/parts/quick_post.html"
    """

    class Meta(NewPostForm.Meta):
        labels = {'title': 'Post Title'}
        widgets = {'content': forms.Textarea(attrs={'class': 'materialize-textarea', 'autocomplete': 'off'}),
                   'title': forms.TextInput(attrs={'autocomplete': 'off', 'required': True})}
