from django.contrib.admin import AdminSite
from django.db import models

from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from tinymce.widgets import AdminTinyMCE

from campaign.admin import CampaignAdmin
from campaign.models import Campaign

from church.admin import ChurchAdmin
from church.models import Church

from donation.admin import DonationAdmin
from donation.models import Donation

from ministry.admin import MinistryProfileAdmin
from ministry.models import Ministry

from post.admin import PostsAdmin
from post.models import Post

from people.admin import UserAdmin
from people.models import User

from public.admin import (
    AboutAdmin, FAQAdmin, MOTDAdmin, SocialMediaLinkAdmin, WebsiteTextAdmin
)
from public.models import (
    AboutSection, FaqSection, MessageOfTheDay, SocialMediaLink, WebsiteText
)

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
admin_site.register(Church, ChurchAdmin)
admin_site.register(Donation, DonationAdmin)
admin_site.register(FaqSection, FAQAdmin)
admin_site.register(MessageOfTheDay, MOTDAdmin)
admin_site.register(Ministry, MinistryProfileAdmin)
admin_site.register(Post, PostsAdmin)
admin_site.register(SocialMediaLink, SocialMediaLinkAdmin)
admin_site.register(Tag, TagAdmin)
admin_site.register(User, UserAdmin)
admin_site.register(WebsiteText, WebsiteTextAdmin)
