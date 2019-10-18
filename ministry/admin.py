from django.contrib import admin

from .models import MinistryProfile
from news.models import NewsPost

admin.site.register(MinistryProfile)

# Frontend Functionality
admin.site.register(NewsPost)
# somehow make these read-only for production. (for statistics only)
