import json

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from tag.models import Tag


def tags_json(request):
    tags = Tag.objects.all()
    _json = [t.name for t in tags]
    _json.sort()
    return HttpResponse(json.dumps(_json))