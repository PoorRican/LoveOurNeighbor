""" This script is meant for creating static website content.

    Namely the About Us page, and FAQ sections.

    NOTE
    ====
        This is not meant to be a long term solution.
"""
from os import chdir as cd
from os import getcwd as pwd
from os import listdir as ls
import django
from django.conf import settings

try:
    import frontend.settings as app_settings
except ModuleNotFoundError:
    cd('..')
    try:
        import frontend.settings as app_settings
    except ModuleNotFoundError:
        cd('/LON')
        import frontend.settings as app_settings

settings.configure(INSTALLED_APPS=app_settings.INSTALLED_APPS,
                   DATABASES=app_settings.DATABASES)
django.setup()

faq_sections = (
    ("What is your mission statement and who are you guys?",
     """Our mission statement and board information can be found <a href="/about">here</a>."""),

    ("What type of ministries and campaigns does your platform sponsor?",
     """Our platform solely to sponsors ministries and organizations
        that provide tangible aid to certain humanitarian causes and injustices.&nbsp;&nbsp;
        A non-exclusive list of the types of causes we support can be found here:
      <ul style="list-style-type: circle; margin-left: 1.5em; margin-top: 1em;">
        <li>Underserved School Relief &amp; Education Programs</li>
        <li>Food Insecure/Ending Hunger Programs</li>
        <li>Crumbling Infrastructure Relief</li>
        <li>Disability Relief and Services</li>
        <li>Human Trafficking Relief Services</li>
        <li>Clean Water Services</li>
        <li>Environmental Pollution, Natural Disaster, and War-Ravished Relief Services</li>
        <li>Medicine and Healthcare Services</li>
        <li>Job Training and Poverty Relief Programs</li>
        <li>Migrant Asylum Seeker Services</li>
        <li>Elderly Care Services</li>
        <li>Orphan, Adoption, Social Work, and Foster Children Services</li>
      </ul>"""),

    ("How is your platform different from me uploading a page for our ministry to other social media sites?",
     """Uploading your ministry to other social media websites can be effective and has many benefits,
        however, the nature of such platforms &mdash; to gain revenue by sponsoring and promoting millions of other pages and
        businesses &mdash; obscures the purpose of ministry, and the Kingdom of Christ.&nbsp;&nbsp;
        Our platform focuses on being a social media space for true Christian ministry whose goal is
        positive humanitarian causes. Our goal is to create a virtual community encouraging others with the posts you share
        and values your presence more than other more crowded platforms."""),

    ("Is your fundraising portal secure?",
     """We use industry standard practices in network security and take further measures
        to ensure your data remains protected."""),

    ("How is fundraising on your site different from me using another crowdsourcing platform?",
     """We provide a platform for existing, established ministries and organizations to thrive and
        upload a profile on our site.  Unlike other crowdsourcing sites that fund an individual missions,
        or one-time campaigns, the persistence of descriptive ministry profiles and the ability for ministries
        to post post, both ministries and visitors are benefited by viewing and interacting with ministries
        in a more personal way than just a fundraising website."""),

    ("Do you only accept Christian charities, ministries, and campaigns on your platform?",
     """As of right now, in our first phase of development and existence, we are narrowing our
        focus solely on Christian charities, ministries, and campaigns."""),

    ("Who is going to be allowed to donate?",
     """Donation is open to anyone and has the heart and conviction to donate."""),

    ("How can I trust the ministries I donate to?",
     """It is one of our highest priorities to only feature ministries that reflects the Christian-faith:
        mainly the aspects of love and integrity.</p>

    <p>We will conduct a thorough interview with ministries and will hold our scrutiny of ministries
        to the standards described in the
        <a href="https://www.ecfa.org/PDF/ECFA_Seven_Standards_of_Responsible_Stewardship.pdf">ECFA 7 Standards of Stewardship</a>.&nbsp;
        As we continue to work with new ministries, we will develop effective methods to verify the
        integrity and validity of the ministries we host."""),

    ("Why does the website tag by ministry type, and have geographical tracking?",
     """We hope to show people amazing things that are happening all around the globe, and to encourage
        certain like-minded ministries and organizations to meet one another and begin partnering.&nbsp;&nbsp;
        The geographical and categorical tracking emphasizes our central quest toward unity. Showing the global
        scope and perspective encourages others by emphasizing that the Body of Christ is not exclusive,
        nor does the ministry of Christians exclude any part of the world."""),

    ("Will ministries be “competing” with other similar ministries and non-profits?",
     """<p>With our platform, we hope and pray we can begin to knock down the notion of
        “competition” among ministries and churches, and instead begin encouraging them toward the
        strength of partnership and promotion of unity.  One of our main goals is to actually promote ministries
        who are doing amazing things, but that has never had the privilege of getting press,
        promotion, and spotlight. </p>

    <p>Our website accomplishes this by placing a special emphasis on new or “unpopular” ministries
        alongside of other successful ministries for any given category.  We encourage ministries
        to utilize other social media alongside of our platform, in addition to posting as many
        post updates to increase your presence on the site and to allow others can read about
        what God is doing through your ministry.""")
)
about_section = (
    ("Mission Statement",
     """Committed to glorifying the Lord by providing an online fundraising platform for Christian ministries.
     We encourage the Body of Christ to work in unity to facilitate generous giving of financial aid
     and resources to humanitarian focused causes on a global scale,
     so that the world may know that the Church of Jesus truly loves our neighbor."""),
)


def clear_content():
    """ Function that clears all existing content sections. """

    print("\nDeleting existing Content...\n")

    for s in FaqSection.objects.all():
        s.delete()
    for s in AboutSection.objects.all():
        s.delete()


if __name__ == "__main__":
    try:
        from public.models import FaqSection, AboutSection
    except ModuleNotFoundError:
        cd('..')
        try:
            from public.models import FaqSection, AboutSection
        except ModuleNotFoundError:
            cd('/LON')
            from public.models import FaqSection, AboutSection

    clear_content()

    print("Beginning to Add Static Content...\n")

    print("Creating FAQ Sections\n")
    for title, content in faq_sections:
        FaqSection.objects.create(title=title, content=content)

    print("Creating About Us Section\n")
    for title, content in about_section:
        AboutSection.objects.create(title=title, content=content)

    print("DONE!\n")
