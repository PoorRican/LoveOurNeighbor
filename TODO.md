# Immediate Things To Do:
* Display/style errorlist in admin_panel (use `form.BoundField.errors.as_data()` as per [this django doc](https://docs.djangoproject.com/en/3.0/ref/forms/api/))
* selected banner/profile images does not seem to work from views....
* Add padding to content on the home page when there is no MOTD
* Campaigns that have ended should not be shown on the home page as new...
* Reimplement profile/banner selection via knockout.js
* Campaigns that have ended should not be shown on home page
* For homepage, implement [masonry](https://masonry.desandro.com/) to get rid of whitespace in where cards appear
* For search functionality, implement [isotope](https://isotope.metafizzy.co/) with combination toggle filters as per [this codepen](https://codepen.io/desandro/pen/zrMXQv)


# Template Port Errors:
- Allow links cards (at least in MOTD cards) to be visible
- Implement [masonry with lightbox plugin](https://dimsemenov.com/plugins/magnific-popup/) for gallery
- Prevent 'None' from showing up in Campaign/(Ministry?) description
- Ministry/Campaign description should be a dropdown if there are NewsPost's to show
- Format datetime picker
- Reformat strftime in campaign side view
- Change 'Ends' label to 'Ended' in campaign card when Campaign has ended


# Immediate Things to Implement
- Turn link tree/sitemap into a global in Python accessible from jinja2 environment
- Turn MotD into modal and fire every first visit
- Static pages:
    * About Us Blurbs
- Help Blurbs for ministries:
    * Explaining details in Ministry Profile Page
- Add Cookie Consent Banner from Termly
- Unverified ministries/campaigns should not be on homepage
- Create a breadcrumb utility function to determine reverse pathway (w/ URLs) given an object (this should go in `frontend`)


## Internal Fixes
- Profile Image Functionality:
    * Unify naming within angular functions. eg: remove 'banner' naming
    * Dynamically show selected/uploaded image
    * Dynamic sizing of grid in image selection dialog
    * Better image uploading
- Remove 'login_in_as' functionality. Add settings flag to enable/disable this feature.
- Display of Users Email
- Edit ministry/campaign page should provide a link to view object
- Clean up utils/ dir. Create a module with utility functions accessible via a CLI or args.
- Separate create/edit pages for NewsPost
- Why does `python manage.py collectstatic` not collect static files for tinymce app in docker config?
- Tag should have a method to for search URL
- Prevent duplicate donation objects from being created upon repeating GET /donation/confirm
- In create campaign function:
    * Ensure User `is_authorized` for ministry
    * Catch ministries that do not exist


# Medium Priority 
## Soft Release Features
Things to do before ministries will be using the site:
- Donation Table for Ministries
- Graph UI showing donation amount over time:
    * Number of donations
    * Dollar amount
    * Average Dollar Donation
    * Active Monthly Givers
    * Total Monthly Givers
    * Progress towards Monthly Goal
    * 3-month view
- Add Google Forms as feedback
- Unverified Ministries should not be able to create Campaigns
- Campaigns should be highlighted on the homepage:
    - (maybe Campaigns should have their own dedicated page)
    * Campaigns almost completed
    * Campaigns that are close to their goal
- News Post UI update:
    * Posts should be able to be created from the profile/campaign page (like FB)
    * Maybe create a dialog for creating news posts
- Gallery:
    * Ministries should be able to simply upload images for gallery
    * News posts should be able to handle multiple attachments
- Homepage Functionality:
    * Have a section for highlighting new or popular tags
    * Random Featured Ministry
    * Posts/Campaigns from Liked Ministries
- Show banner image in ograph metadata for media sharing
- Generator function to create news feed for Ministry Profile (aggregating Campaigns/News Posts, sorted by `pub_date`)
- Errors:
    * Implement [custom error pages](https://docs.djangoproject.com/en/3.0/topics/http/views/)
    * Implement [error reporting](https://docs.djangoproject.com/en/3.0/howto/error-reporting/)
    * Implement [custom form field error list](https://docs.djangoproject.com/en/3.0/ref/forms/api/#customizing-the-error-list-format)

## Hard Release Features
Things to do before Users will be using the site:
- Better Donation/Transaction UI:
    * Payeezy Direct API
    
# Low Priority
## Styling Changes
- Style Email Templates:
    * Password Reset
    * Email Verification
    * Notification/Update Email
- Progress Bar:
    * Dynamically Loaded
    * Gradient. Color change in completion amount.
    * Pulse/heartbeat animation
- Unify header styling between materialize and angular material
- Profile/Banner Image:
    * Dynamically resize trigger image dimensions
    * Dynamically resize tile dimensions
    * 'Cancel' should undo change
    * 'Done' should upload
    * Banner image trigger should reflect the wide dimensions as it is displayed on view page
- Card offsets button in News tab in Campaign admin panel
- Form buttons in campaign admin panel should match ministry admin panel
- Like button:
    * Add animation to like_button (eg: ripple)
    * Show "unlike" upon hover when liked
- Implement [particle.js](https://github.com/VincentGarreau/particles.js/) as background for 'register' and 'login' pages.    
- In Donation graph, have different colors for different statistics

## Implementation Changes
- Create custom asset handler:
    * Override django's collectstatic method
    * Override django's 'static' function to create url using 'STATIC_URL' and CRM URL while not debugging
- Implement ClassAsView's:
    * Image JSON url's should use identical view function/functor-class
    * Edit Ministry/Create Ministry
    * Edit Campaign/Create Campaign
    * Edit News/Create News
    * Edit User/Create User
- Fix Admin functionality
- Help text should be in a dedicated app so that it is editable
- Implement generic relations for NewsPost [using contenttypes](https://docs.djangoproject.com/en/3.0/ref/contrib/contenttypes/)
- Implement [django-rest-framework](https://www.django-rest-framework.org/) for making way for implementing an app

## Deployment Changes
- nginx container should be built via staged loading to acquire certs and avoid nginx config hacks
