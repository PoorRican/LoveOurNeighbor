from django.contrib.contenttypes.models import ContentType
from django.views.generic.base import View, ContextMixin
from django.views.generic.edit import CreateView
from django.http import HttpResponse

from braces.views import FormMessagesMixin, UserPassesTestMixin, JSONResponseMixin

from campaign.models import Campaign
from ministry.models import Ministry

from .models import Like


class LikeView(View, JSONResponseMixin):
    """ Encapsulates both 'like' and 'unlike' functionality relating `User` to `Ministry`

    Returns
    -------
    JsonResponse key-value containing 'liked' with a boolean value reflecting
        whether the User 'likes' the ministry.

    """

    def get(self, request, *args, **kwargs):
        # TODO: implement Post
        _objects = {'ministry': Ministry,
                    'campaign': Campaign}
        obj = _objects[kwargs.get('object')]
        obj = obj.objects.get(pk=kwargs.get('pk'))

        return self.render_json_response({'liked': Like.do(obj, request.user)})
