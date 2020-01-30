from django.contrib.admin import AdminSite

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

from public.admin import AboutAdmin, FAQAdmin
from public.models import AboutSection, FaqSection


class LONAdminSite(AdminSite):
    site_header = 'LON Administration'


admin_site = LONAdminSite()

admin_site.register(Campaign, CampaignAdmin)
admin_site.register(MinistryProfile, MinistryProfileAdmin)
admin_site.register(NewsPost, NewsPostAdmin)
admin_site.register(User, UserAdmin)
admin_site.register(AboutSection, AboutAdmin)
admin_site.register(FaqSection, FAQAdmin)
admin_site.register(Donation, DonationAdmin)
