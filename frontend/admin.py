from django.contrib.admin import AdminSite
from django.db import models

from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from tinymce.widgets import AdminTinyMCE

from campaign.admin import CampaignAdmin
from campaign.models import Campaign

from donation.admin import DonationAdmin
from donation.models import Donation

from ministry.admin import MinistryProfileAdmin
from ministry.models import MinistryProfile

from news.admin import NewsPostAdmin
from news.models import NewsPost

from people.admin import UserAdmin
from people.models import User

from public.admin import AboutAdmin, FAQAdmin, SocialMediaLinkAdmin
from public.models import AboutSection, FaqSection, SocialMediaLink

from tag.admin import TagAdmin
from tag.models import Tag


class LONAdminSite(AdminSite):
    site_header = 'LON Administration'


class NewFlatPageAdmin(FlatPageAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminTinyMCE()}
    }
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': (
                'registration_required',
                'template_name',
            ),
        }),
    )


admin_site = LONAdminSite()

admin_site.register(FlatPage, NewFlatPageAdmin)

admin_site.register(AboutSection, AboutAdmin)
admin_site.register(Campaign, CampaignAdmin)
admin_site.register(Donation, DonationAdmin)
admin_site.register(FaqSection, FAQAdmin)
admin_site.register(MinistryProfile, MinistryProfileAdmin)
admin_site.register(NewsPost, NewsPostAdmin)
admin_site.register(SocialMediaLink, SocialMediaLinkAdmin)
admin_site.register(Tag, TagAdmin)
admin_site.register(User, UserAdmin)
