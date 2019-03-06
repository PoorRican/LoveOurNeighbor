from django.contrib import admin

from .models import NewsPost, Campaign, Patron, Donation


# Register your models here.
admin.site.register(NewsPost)
admin.site.register(Campaign)
# somehow make these read-only for production. (for statistics only)
admin.site.register(Patron)
admin.site.register(Donation)
