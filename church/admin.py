from django.contrib.admin import ModelAdmin
from django.db import models

from tinymce.widgets import AdminTinyMCE


class ChurchAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminTinyMCE()}
    }
    list_display = ('name', 'pub_date', 'verified', 'admin')
    search_fields = ('name', 'admin', 'tags__name')
    readonly_fields = ('pub_date',)
    fieldsets = (('Metadata', {'fields': ('pub_date',)}),
                 ('Profile Data',
                  {'fields': (('name', 'verified'), 'description', 'tags', 'profile_img', 'banner_img')}),
                 ('Administration', {'fields': ('admin', 'reps')}),
                 ('Details', {'fields': ('address', 'phone_number', 'website', 'founded', 'staff')}),
                 ('Social Media Links', {'fields': ('facebook', 'instagram', 'youtube', 'twitter')}))
