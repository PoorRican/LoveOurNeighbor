from django import forms

from comment.models import Comment


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