from django.contrib.admin import ModelAdmin
from django.db import models

from tinymce.widgets import AdminTinyMCE


class FAQAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminTinyMCE()}
    }
