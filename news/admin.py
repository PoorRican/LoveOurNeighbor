from django.contrib.admin import ModelAdmin
from django.db import models

from tinymce.widgets import AdminTinyMCE


class NewsPostAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminTinyMCE()}
    }
    list_display = ('title', 'pub_date', 'ministry', 'campaign')
    search_fields = ('title', 'ministry__name', 'campaign__title')
    readonly_fields = ('campaign', 'ministry', 'pub_date')
    fieldsets = (('Metadata', {'fields': ('ministry', 'campaign', 'pub_date')}),
                 ('Content', {'fields': ('title', 'attachment', 'content',),
                              'classes': ('wide',)}),

                 )
