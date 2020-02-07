from django.contrib.admin import ModelAdmin
from django.db import models

from tinymce.widgets import AdminTinyMCE


class AboutAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminTinyMCE()}
    }


class FAQAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminTinyMCE()}
    }


class SocialMediaLinkAdmin(ModelAdmin):
    list_display = ('name',)
