from django import forms

from django_drf_filepond.api import store_upload
from django_drf_filepond.models import TemporaryUpload

from .models import Post


class NewPostForm(forms.ModelForm):
    """Form for creating Post objects.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['media'] = forms.FileField(required=False)

    def clean_filepond(self):
        self.cleaned_data['media'] = self.data.getlist('media')

    class Meta:
        model = Post
        fields = ('title', 'content')
        widgets = {'content': forms.Textarea(attrs={'id': 'tinyEditor'})}


class NewsEditForm(NewPostForm):
    """Form for viewing and editing fields in a Post object.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        upload_ids = []
        for i in self.instance.media.all():
            upload_ids.append(i.image.upload_id)
