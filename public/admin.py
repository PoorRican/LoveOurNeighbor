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


class MOTDAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminTinyMCE()}
    }
    list_display = ('title', 'pub_date', 'edit_date', 'display')
    readonly_fields = ('pub_date', 'edit_date')
    fieldsets = (
        ('Metadata', {'fields': ('pub_date', 'edit_date')}),
        ('Content', {'fields': (('title', 'display'), 'message')})
    )


class WebsiteTextAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminTinyMCE()}
    }
    list_display = ('label',)
