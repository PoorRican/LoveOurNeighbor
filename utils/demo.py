from random import choice, randint
from datetime import date
from uuid import uuid4

import django
from django.db.utils import IntegrityError
from django.conf import settings
import frontend.settings as app_settings

settings.configure(INSTALLED_APPS=app_settings.INSTALLED_APPS,
                   DATABASES=app_settings.DATABASES)
django.setup()


_first_names = "John Steve Matt Josh Isaiah Isaac Paul Esteban Joseph \
Robertino Saturno Innocencia Valentina Genesis Anna Ruth Esther Sophia \
Eliza Stella Estrella Fey Aeryn Akeema Alfonsina Amairani Anais Angelica \
Annika Arwen Azure Briseida Brogan Calantha Carlisia Cesarina Chiari \
Cressida Cristela Cyndel Dasnee Devlan Donica Elfi Emthe Esperanza Golden \
Ila Ismaray Janalyn Javoszia Kalene Kasondra Kerianne Kosta Mahalia \
Maribel Marleigh Marlete Meriel Michelina Monterey Nannette Nisha Odessa \
Omnia Paola Pepper Prudence Remy Scharlette September Shaedde Sharmela \
Shona Tamsyn Tashina Tasia Thedra Tomesa Tressa Truly Tyla Wing Zanna \
Akoyé Blade Blaise Caledon Colburn Coty Curran Dhiradj Drax Eion Evik \
Gareth Herschel Horace Jovino Kenton Kohl Lawson Miiko Monzenn Obidi Ozbel \
Polis Reza Ridge Rocio Sabre Seven Shelton Shiloh Tappah Tarsis Tiberius \
Tramond Tristan Xane Zared".split(" ")
_last_names = "Smith Poderosa Aguilar Flores Lopez Ortiz Ruiz Alvarez \
Garcia Martinez Pena Salazar Castillo Garza Medina Perez Sanchez Castro \
Gomez Mendez Ramirez Santiago Chavez Gonzales Mendoza Ramos Soto Cruz \
Gutierrez Morales Reyes Torres Delgado Guzman Moreno Rios Valdez Diaz \
Hernandez Munoz Rivera Vargas Espinoza Hierra Nunez Rodriguez Vasquez \
Fernandez Jiminez Ortega Romero Vega Chips Hatman Temples Raynott Woodbead \
Nithercott Rummage Southwark Harred Jarsdel Pober Mirren Febland Nighy \
Grader Bonneville Gruger Carla Fernard Portendorfer Azikiwe Asari-Dokubo \
Awolowo Jomo-Gbomo Bello Anikulapo-Kuti Balewa Iwu Akintola Anenih \
Okotie-Eboh Bamgboshe Nzeogwu Biobaku Onwuatuegwu Tinibu Okafor Akinjide \
Okereke Akinyemi Okeke Akiloye Okonkwo Adeyemi Okoye Adesida Okorie Omehia \
Obasanjo Sekibo Babangida Okar Buhari Amaechi Dimka Bankole Diya Nnamani \
Odili Ayim Ibori Okadigbo Igbinedion Ironsi Alamieyeseigha Ojukwu Yar’Adua \
Danjuma Akpabio Effiong Attah Akenzua Chukwumereije Adeoye Akunyili \
Adesina Iweala Saro-Wiwa Okonjo Gowon Ezekwesili Ekwensi Achebe Egwu \
Soyinka Onobanjo Solarin Aguda Gbadamosi Okpara Olanrewaju Mbanefo Magoro \
Boro Madaki Akerele Jang Alakija Oyinlola Balogun Oyenusi Mbadinuju \
Onyejekwe Okiro Onwudiwe Okilo Jakande Jaja Kalejaiye Fagbure Igwe Falana \
Eze Ademola Obi Ohakim Ngige Orji Uba Kalu".split(" ")

_cities = ("New York, USA", "London, UK", "Dubai, UAE", "Barcelona, Spain",
           "Rio de Janeiro, Brazil",
           "Paris, France", "Oslo, Norway", "Bangkok, Thailand",
           "Berlin, Germany", "Ludz, Poland", "Tokyo, Japan",
           "Hamberg, Germany", "Pamukkale, Turkey", "Lake Hillier, Australia",
           "Badab-e-Surt, Iran", "Hunan Province, China", "Lima, Peru",
           "Cleveland, OH", "Sao Paolo, Brazil", "Buenos Aires, Argentina",
           "Trinidad", "Barceloneta, PR", "Santo Domingo, DR", "Dallas, TX",
           "St Louis, Missouri", "Providence", "Baton Rouge, LA",
           "Mexico City, Mexico", "Venezuela", "Columbia", "Czech Republic",
           "Slovakia", "Laos", "India", "Damascus", "Stilles, Italy",
           "Kuupala, Finland", "St Petersburg, Russia", "Moscow, Russia",
           "Kirachi, Pakistan", "Tianjin, China", "Kinshasha, DR Congo",
           "Delhi, India", "Cairo, Egypt", "Seoul, South Korea",
           "Jakarta, Indonesia", "Wenzhou, China", "Bangalore, India",
           "Ho Chih Minh City, Vietnam", "Shenzhen, China", "Tehran, Iran",
           "Bogota, Colombia", "Baghdad, Iraq", "Hanoi, Vietnam",
           "Santiago, Chile", "Yangon, Myanimar", "Casablanca, Morocco",
           "Melbourne, Australia", "Abidjan, Ivory Coast", "Alexandria, Egypt",
           "Surat, India", "Johannesburg, South Africa",
           "Dar es Salaam, Tanzania", "Giza, Egypt", "New Tapei City, Taiwan",
           "Cape Town, South Africa", "Yokohama, Japan", "Guayaquil, Ecuador",
           "Busan, South Korea", "Algiers, Algeria", "Mashhad, Iran",
           "Pyongyang, North Korea", "Faisalabad, Pakistan",
           "Baku, Azerbaijan", "Nairobi, Kenya", "Lagos, Nigeria",
           "Dhaka, Bangledesh", "Mumbai, India", "Nur-Sultan, Kazakhstan",
           "Tunis, Tunisia", "Cologne, Germany", "Yerevan, Armenia",
           "Birmingham, UK", "T'bilisi, Georgia")

_campaigns = ("New Building", "New Project", "New Location", "New Countries",
              "Another Name", "Quarterly Fundraiser",
              "Administrative Fundraiser", "Easter Fundraiser",
              "Help Us Reach New Cities", "Help us reach other countries",)

_ministry_desc = ("Special", "Another", "Exceptional", "Just a", "A New",
                  "Just another", "Unique", "Tried and True", "Persistent")
_ministry_cat = ("Church building", "Clean Water", "Infrastructure Building",
                 "Educational", "Quality of Life", "Humanitarian",
                 "Philanthropic")
_ministry_post = ["Ministry", "Non-profit", "for Christ", "for the Most High"]
for _ in range(0, round(len(_cities)/2)):
    c = choice(_cities).split(", ")[-1]
    _ministry_post.append("Ministry in %s" % c)
for _ in range(0, round(len(_cities)/2)):
    c = choice(_cities).split(", ")[-1]
    _ministry_post.append("Non-Profit in %s" % c)
for _ in range(0, round(len(_cities)/2)):
    c = choice(_cities).split(", ")[0]
    _ministry_post.append("Ministry in %s" % c)
for _ in range(0, round(len(_cities)/2)):
    c = choice(_cities).split(", ")[0]
    _ministry_post.append("Non-profit in %s" % c)


_news_post_titles = ("Check out what we have done", "Project Update",
                     "News Update", "God is Good!", "New Video", "New Gallery",
                     "Another Update", "Almost Done", "Another Job Well Done",
                     "Progress Report", "Great Things are Coming",
                     "The Good things He Has Done", "Progress Update")

_tags = ["Justice", "Humanitarian", "Quality", "Water", "Homeless",
         "Urban", "Education", "Ministry", "Remote", "Relief"]
for i in range(1, 20):
    _tags.append("Tag %d" % i)


USERS = []
MINISTRIES = []


def lorem():
    l = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed \
    do eiusmod tempor incididunt ut labore et dolore magna aliqua. Velit \
    euismod in pellentesque massa placerat duis. Gravida arcu ac \
    tortor dignissim convallis aenean. Id nibh tortor id aliquet. \
    Neque volutpat ac tincidunt vitae semper quis lectus nulla at. In \
    metus vulputate eu scelerisque felis imperdiet. Amet facilisis \
    magna etiam tempor orci eu. Malesuada pellentesque elit eget \
    gravida cum. Rhoncus mattis rhoncus urna neque viverra. Enim nulla \
    aliquet porttitor lacus luctus accumsan tortor posuere ac. Urna nec \
    tincidunt praesent semper feugiat. Vel risus commodo viverra maecenas. \
    Parturient montes nascetur ridiculus mus mauris vitae ultricies. Nibh \
    sed pulvinar proin gravida hendrerit lectus a. In egestas erat \
    imperdiet sed euismod nisi porta lorem mollis. In vitae turpis massa \
    sed. Hendrerit dolor magna eget est. Ultricies integer quis auctor \
    elit. Egestas tellus rutrum tellus pellentesque eu tincidunt tortor \
    aliquam nulla.

    Sit amet consectetur adipiscing elit ut aliquam purus sit. Bibendum at \
    varius vel pharetra vel turpis nunc. Mi in nulla posuere sollicitudin \
    aliquam. Magna etiam tempor orci eu lobortis. Habitasse platea \
    dictumst vestibulum rhoncus est pellentesque elit. Vel pretium lectus \
    quam id leo in vitae turpis massa. Cursus euismod quis viverra nibh \
    cras. Neque convallis a cras semper auctor. Suspendisse potenti nullam \
    ac tortor vitae. Placerat in egestas erat imperdiet sed \
    euismod.

    Viverra accumsan in nisl nisi. Nisl nisi scelerisque eu ultrices vitae \
    auctor eu augue ut. Augue ut lectus arcu bibendum. Malesuada bibendum \
    arcu vitae elementum curabitur vitae. In metus vulputate eu \
    scelerisque felis imperdiet proin fermentum. In dictum non consectetur \
    a erat nam. Mauris pharetra et ultrices neque ornare aenean euismod. \
    Ac turpis egestas maecenas pharetra convallis posuere morbi. Ac felis \
    donec et odio pellentesque diam volutpat commodo sed. Orci sagittis eu \
    volutpat odio. Vulputate dignissim suspendisse in est ante in nibh \
    mauris. Sit amet dictum sit amet justo donec enim diam vulputate. \
    Tincidunt eget nullam non nisi est sit. Et netus et malesuada fames ac \
    turpis. Tellus in hac habitasse platea dictumst vestibulum rhoncus \
    est. Arcu odio ut sem nulla pharetra diam sit amet. Euismod quis \
    viverra nibh cras. Et egestas quis ipsum suspendisse ultrices gravida \
    dictum. Ullamcorper sit amet risus nullam eget felis eget. Augue lacus \
    viverra vitae congue eu consequat ac felis donec.

    Vestibulum lectus mauris ultrices eros. Tristique sollicitudin nibh \
    sit amet commodo nulla. Nullam vehicula ipsum a arcu cursus vitae \
    congue mauris rhoncus. Est ultricies integer quis auctor elit sed. Sit \
    amet purus gravida quis blandit turpis cursus in. Aenean euismod \
    elementum nisi quis eleifend quam adipiscing vitae proin. Nunc aliquet \
    bibendum enim facilisis. Sed vulputate mi sit amet mauris commodo. Est \
    velit egestas dui id. Amet dictum sit amet justo donec. Morbi tempus \
    iaculis urna id. Sed pulvinar proin gravida hendrerit. Arcu non odio \
    euismod lacinia at quis risus sed vulputate. Magna ac placerat \
    vestibulum lectus mauris ultrices eros in cursus. Id diam vel quam \
    elementum pulvinar etiam non. Fringilla est ullamcorper eget nulla \
    facilisi etiam dignissim. Accumsan lacus vel facilisis volutpat est \
    velit egestas dui. Fermentum posuere urna nec \
    tincidunt.

    Cursus eget nunc scelerisque viverra mauris. Egestas sed tempus urna \
    et pharetra pharetra massa massa. In nibh mauris cursus mattis \
    molestie a. Ipsum suspendisse ultrices gravida dictum fusce. Felis \
    eget nunc lobortis mattis aliquam faucibus purus in. At urna \
    condimentum mattis pellentesque id nibh tortor id. Integer eget \
    aliquet nibh praesent tristique magna sit amet purus. Duis convallis \
    convallis tellus id interdum velit laoreet id. Bibendum neque egestas \
    congue quisque egestas diam in arcu. Et odio pellentesque diam \
    volutpat commodo sed egestas egestas fringilla. Eget est lorem ipsum \
    dolor. Leo in vitae turpis massa sed elementum tempus egestas sed. \
    Arcu non odio euismod lacinia at quis risus sed \
    vulputate."""
    return l


def create_demo_user():
    global USERS

    f_name = choice(_first_names)
    l_name = choice(_last_names)
    d_name = "%s %c" % (f_name, l_name[0])

    loc = choice(_cities)
    email = "%s@email.com" % uuid4().hex

    u = User.objects.create(email=email,
                            first_name=f_name,
                            last_name=l_name,
                            display_name=d_name,
                            _location=loc,)
    USERS.append(u)


def create_demo_ministry():
    t = choice(_ministry_cat)
    name = "%s %s %s" % (choice(_ministry_desc),
                         t,
                         choice(_ministry_post))

    admin = choice(USERS)

    desc = lorem().split("\n\n")[:2]
    desc = "<p>%s</p>" % ("</br><br>".join(desc))

    loc = choice(_cities)

    pn = (randint(100, 999),
          randint(100, 999),
          randint(1000, 9999))
    pn = "+1(%d)%d-%d" % pn

    site = "https://%s.loveourneighbor.org" % uuid4().hex

    found = date(2019, 3, 9)

    t = [t]
    for _ in range(0, 5):
        t.append(choice(_tags))
    t = ", ".join(t)

    try:
        m = MinistryProfile.objects.create(name=name,
                                           admin=admin,
                                           description=desc,
                                           address=loc,
                                           founded=found,
                                           phone_number=pn,
                                           website=site,)

        Tag.process_tags(m, t)
    except IntegrityError:
        name = "%s %d" % (name, randint(0, 5))
        m = MinistryProfile.objects.create(name=name,
                                           admin=admin,
                                           description=desc,
                                           address=loc,
                                           founded=found,
                                           phone_number=pn,
                                           website=site,)

        Tag.process_tags(m, t)

    global MINISTRIES
    MINISTRIES.append(m)
    return m


def create_demo_campaign(ministry):
    title = choice(_campaigns)

    s_d = date(2018, randint(1, 12), randint(1, 28))
    e_d = date(2019, randint(1, 12), randint(1, 28))

    desc = lorem().split("\n\n")[:1]
    desc = "<p>%s</p>" % ("</br><br>".join(desc))

    goal = randint(10, 100)
    goal = goal * pow(10, randint(2, 4))

    t = []
    for _ in range(0, 5):
        t.append(choice(_tags))
    t = ", ".join(t)

    c = Campaign.objects.create(title=title,
                                ministry=ministry,
                                start_date=s_d,
                                end_date=e_d,
                                content=desc,
                                goal=goal,)
    Tag.process_tags(c, t)
    return c


def create_demo_news(obj, _type):
    title = choice(_news_post_titles)

    desc = lorem().split("\n\n")[:2]
    desc = "<p>%s</p>" % ("</br><br>".join(desc))

    np = Post.objects.create(title=title,
                             content=desc,
                             **{_type: obj})
    return np


def sim_likes(obj):
    _iter = randint(25, 500)
    for i in range(0, _iter):
        u = choice(USERS)
        obj.likes.add(u)
    obj.save()


if __name__ == "__main__":
    from people.models import User
    from ministry.models import MinistryProfile
    from campaign.models import Campaign
    from tag.models import Tag
    from news.models import Post

    print("Beginning to populate database...\n")
    print("Starting with User objects...")
    for _ in range(0, 1000):
        create_demo_user()
    print("Created Users!\n")

    print("Creating MinistryProfile, Campaign, Post objects...\
(this might take a while)")
    count = 0
    ministry_iter = 100
    for _ in range(0, ministry_iter):
        m = create_demo_ministry()
        print("Created %s " % m.name)
        # TODO: comment 20 times per ministry
        sim_likes(m)                           # simulate likes for ministry
        for __ in (_, _):
            create_demo_news(m, 'ministry')  # create post posts for ministry
            # TODO: comment 20 times per ministry > post post
            c = create_demo_campaign(m)  # create campaigns for ministry
            # TODO: comment 20 times per campaign
            sim_likes(c)  # simulate likes for campaign
            create_demo_news(c, 'campaign')  # create post posts per campaign
            # TODO: comment 20 times post post
        count += 1
        if not count % 10:
            print("%d/%d Complete..." % (count, ministry_iter))
    print("DONE!\n")
