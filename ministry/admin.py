from django.contrib import admin

from .models import MinistryProfile
from .models import NewsPost, Campaign, Donation


admin.site.register(MinistryProfile)

# Frontend Functionality
admin.site.register(NewsPost)
admin.site.register(Campaign)
# somehow make these read-only for production. (for statistics only)
admin.site.register(Donation)