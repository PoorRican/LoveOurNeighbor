
   ██                                      ███████                     ████     ██         ██         ██      ██
  ░██                                     ██░░░░░██                   ░██░██   ░██        ░░   █████ ░██     ░██
  ░██        ██████  ██    ██  █████     ██     ░░██ ██   ██ ██████   ░██░░██  ░██  █████  ██ ██░░░██░██     ░██       ██████  ██████
  ░██       ██░░░░██░██   ░██ ██░░░██   ░██      ░██░██  ░██░░██░░█   ░██ ░░██ ░██ ██░░░██░██░██  ░██░██████ ░██████  ██░░░░██░░██░░█
  ░██      ░██   ░██░░██ ░██ ░███████   ░██      ░██░██  ░██ ░██ ░    ░██  ░░██░██░███████░██░░██████░██░░░██░██░░░██░██   ░██ ░██ ░
  ░██      ░██   ░██ ░░████  ░██░░░░    ░░██     ██ ░██  ░██ ░██      ░██   ░░████░██░░░░ ░██ ░░░░░██░██  ░██░██  ░██░██   ░██ ░██
  ░████████░░██████   ░░██   ░░██████    ░░███████  ░░██████░███      ░██    ░░███░░██████░██  █████ ░██  ░██░██████ ░░██████ ░███
  ░░░░░░░░  ░░░░░░     ░░     ░░░░░░      ░░░░░░░    ░░░░░░ ░░░       ░░      ░░░  ░░░░░░ ░░  ░░░░░  ░░   ░░ ░░░░░    ░░░░░░  ░░░


# Introduction

At the moment, this codebase is the backbone to the Love Our Neighbor platform. It was created by a security and feature conscious
individual who wants nothing more than for the Love Our Neighbor to remain secure and able to provide any and all features with
little dependence on frameworks such as WordPress or even mid-level libraries to provide some functionality. That being said,
most of the codebase is custom (eg: profiles, like functionality, donations, etc). There are some parts of that have been overwritten
or otherwise swapped (ie: [user authentication](#auth), [django template language](#dtl)). Both custom parts and overwritten parts has been documented
within the code itself, is (further described in this document (under 'Implementation Notes'))[#implementation-notes], and `CONTRIBUTING.md`
explains how any future additions or modifications to the code should be performed.

In the future, this codebase should be capable of providing the backend functionality for any mobile apps. It would be prudent to not store
any critical information on this webapp, nor conduct any critical functions (ie: financial, or invoicing functions) using this webapp.
I would be most disappointed...

That being said, if you have not met me, let this document be some form of relief. If you have had the pleasure of knowing me, may you
understand me further... As to whoever you are, let not the complexity of this code insight any enmity between you and me...

      ┳┏━┓┓━┓┳ ┓┳━┓  ┳━┓┳━┓┓ ┳o┳━┓  ┳━┓o┏━┓┳ ┓┳━┓┳━┓┏━┓┳━┓
    ┏ ┃┃ ┃┗━┓┃ ┃┣━   ┃ ┃┃━┫┃┏┛┃┃ ┃  ┣━ ┃┃ ┳┃ ┃┣━ ┃┳┛┃ ┃┃━┫
    ┗━┇┛━┛━━┛┇━┛┻━┛  ┇━┛┛ ┇┗┛ ┇┇━┛  ┇  ┇┇━┛┇━┛┻━┛┇┗┛┛━┛┛ ┇


## Hierarchical Overview

Use this section as a basic guide to each module as you become familiar and internalize the layout of the codebase. Please refer
to the model documentation and function docstrings within each module.

Each part of the website is modular. Like any good code, there is some reusable code. Much of the general, `frontend` contains much of the
backend and any utility function or base-class that is used in more than one module. It is also where the django settings lives, and
where the root URLCONF is defined. This app folder also initiates the jinja2 environment, where you'll find the global tags available
within templates. Note that there are no template directories within the app-folders: there is no reason behind this; you are encouraged
to move the named folders is `templates` to their respective app-folders. 

Then comes the second most essential part: Users. This is has been renamed `people` to remind both you and I who Users are...
The built-in `django.contrib.auth` functionality has been [mostly overwritten](#auth). The overwritten parts includes functions and forms
to create new users, email verification, password reset, and any high-level user functions and templates. There is no special class or model
for ministry/church admin nor staff.

The rest of the modules can be divided into "functional" modules (ie: `explore` and `search`) and "content" modules. The functional modules
map or may not provide views or templates but exist to provide some broad function --  `explore` module provides rudimentary GeoSpatial calculation
functionality, and the `search` module provides basic search. Following, the "content" modules can be further divided to "static" content
(ie: `public`) and "dynamic" content.

There are 2 levels/hierarchies to the "dynamic" content, top-level modules the "profile" models/modules (ie: `ministry` and `church`) and `campaign`,
and low-level modules (eg: `donation`, `post`, `activity`, etc). These are determined if the models are "parent" models, which can be associated
with "children" models (eg: a `campaign` can have many `donations`). Children typically can have one parent, but parent models can be "parents"
to other instances of the same type (eg: `ministry` can sponsor another `ministry`, or a `church` can be part of a group or association of `churches`).
From a hierarchical standpoint, `campaign` really is the only mid-level model as it **ONLY** exists as a child of `ministry`, but is the only model
with a relationship to `donation` and can children `post`, `activity`, `comment`, and `tag` models.

# <a name="Implementation Notes"></a>Implementation Notes

## Overwritten Functionality

I know you might be thinking to yourself, "But *why??*". Don't worry, herein lies the reasoning as to why the django-templating-language
has been replaced with [jinja2](https://jinja.palletsprojects.com/en/2.11.x/) and why `django.contrib.auth` has been replaced with `people`...

### Regarding the Django Templating Language versus Jinja2
<a name="dtl"></a>

Many parts of the website have been encapsulated into reusable macros (placed in "templates/macros"). This allows the website to be coded in
a programmatic function and allows for template files to be cleaner, smaller and easier to read. For example, there is [`input_fields`](templates/macros/parts/input_field.html)
which encapsulates rendering an input form field, label, form errors, help text, and even an optional icon... all enclosed in a div field...
There are many other similar reusable pieces such as [`breadcrumbs`](templates/macros/parts/breadcrumbs.html), [`donate_button`](templates/macros/parts/input_field.html)
[`like_button`](templates/macros/parts/like_button.html), and [`tag_chips`](templates/macros/parts/tag_chips.html) (just to name a few) that are agnostic
to the content, but display functionality in a clean reusable way. The passing of arguments in Jinja2 macros is a much more "Pythonic" way
of templating and allows for more expressive and has allowed the complex pages to be broken down into simple reusable parts.

There are other macros that act as complex functions or inheritable classes, for example [`base_content_card`](templates/macros/parts/base_content_card.html)
is used inside of [`ministry_card`](templates/ministry/ministry_card.html), [`campaign_card`](templates/campaign/campaign_card.html), and
[`post_card`](templates/post/post_card.html) to render all card types similarly with differing content and menu options.

The only aspect of using Jinja2 that might seem cumbersome is the fact that the environment needs to be explicitly defined in [jinja.py](frontend/jinja.py),
however this also provides the ability to easily import custom functions, filters, and variables available in the global namespace in all templates.
Some functionality of the DTL has needed to be duplicated (eg: `get_messages`), but I would imagine that explicitly passing these
to the environment helps reduce the memory overhead (this has not been verified).

The good news is that Jinja2 has been modeled after the DTL and is almost identical.

### Regarding the insufficiency of `django.contrib.auth`
<a name="auth"></a>

I will not disagree with you that django does not have plenty of advanced built-in high-level functionality. Sometimes this advanced functionality
proves cumbersome when it comes to advanced customization. For example, the built-in `User` class uses "username" as the primary key, and writing a new class
provides that fix, but you are still stuck with that "black box" of the specific implementations and are then locked into the built-in URLs have little
room for customization. You would then need to create a `Profile` model and link the `User` via a 1-to-1 relationship to store any other data.

You can view most of these reasons as simply excuses that originated from before the website was even publicly available. The **true** reason now as to
why this module should remain (and be improved) is for what happens when someone donates ***without*** having an account. The "payeezy form" has
been customized to get the donors email address -- just as [donorbox gathers compulsory info](https://donorbox.org/features). Payeezy passes this email value
along with the rest of transaction data as the transaction finishes. When the server receives and processes the data, a new `User` is created
(with `is_active` set to `False`) alongside of the `Donation`. This email has no privilege while `is_active` is `False`. Reinventing the wheel
allows for a user to "use" this email address to "create" a new email account. In reality, all that happens is that the password field gets populated,
and the `is_active` flag gets set to `True`!


## Servers / AWS

### Initialization of Parameters and Secrets (eg: API-keys, and passwords)

Parameters for `frontend.settings` come from environment variables which are set in the Dockerfile and come from
AWS Systems Manager > Parameter Store. Therefore, all EC2 instances should have appropriate the IAM Role to have access to both
S3 **AND** AWS Systems Manager.

This might not be the most secure method. Hypothetically, in a compromised server, it is low-hanging fruit for an
attacker to dump all environment variables. While dumping the memory of the running django instance to extract keys
requires more time and precision and might be harder to exfiltrate if tools are not ready beforehand. The alternative I propose
is to have python get the values directly and pass them to `frontend.settings`.

The LORD willing, such paranoia will not be necessary...


### Tutorials 
