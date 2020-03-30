from django.contrib.admin import ModelAdmin
from django.db import models

from tinymce.widgets import AdminTinyMCE


class PostsAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminTinyMCE()}
    }
    list_display = ('title', 'pub_date',)
    search_fields = ('title',)
    readonly_fields = ('pub_date',)
    fieldsets = (('Metadata', {'fields': ('pub_date',)}),
                 ('Content', {'fields': ('title', 'attachment', 'content',),
                              'classes': ('wide',)}),

                 )
