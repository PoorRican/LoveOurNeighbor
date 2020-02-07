from django.contrib.admin import ModelAdmin


class TagAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description', 'ministries__name', 'campaigns__title')
