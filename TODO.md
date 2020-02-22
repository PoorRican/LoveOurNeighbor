# Template Port Errors:
- Tab bar in card_area has blank space on sides
- Allow links cards (at least in MOTD cards) to be visible
- MinistryProfile admin panel should have separate form for details and admin/rep management
- Implement news_card using new materialize elements
- Implement [masonry with lightbox plugin](https://dimsemenov.com/plugins/magnific-popup/) for gallery


# Bugs
- Prevent duplicate donation objects from being created upon repeating GET /donation/confirm
- MinistryProfile like button does not work

# Immediate Things to Implement
- Turn link tree/sitemap into a global in Python accessible from jinja2 environment
- Turn MotD into modal and fire every first visit
- Static pages:
    * About Us Blurbs
- Help Blurbs for ministries:
    * Explaining start/stop dates (when creating a Campaign)
    * Explaining details in Ministry Profile Page
- Add Cookie Consent Banner from Termly
- Unverified ministries/campaigns should not be on homepage
- If a home page card does not have a banner_img, it should not have a large value for margin-top
- Create a breadcrumb utility function to determine reverse pathway (w/ URLs) given an object (this should go in `frontend`)

## Internal Fixes
- Profile Image Functionality:
    * Unify naming within angular functions. eg: remove 'banner' naming
    * Dynamically show selected/uploaded image
    * Dynamic sizing of grid in image selection dialog
    * Better image uploading
- Remove 'login_in_as' functionality. Add settings flag to enable/disable this feature.
- Display of Users Email
- Display users likes
- Edit ministry/campaign page should provide a link to view object
- Clean up utils/ dir. Create a module with utility functions accessible via a CLI or args.
- Separate create/edit pages for NewsPost
- Why does `python manage.py collectstatic` not collect static files for tinymce app in docker config?
- Tag should have a method to for search URL


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
- Show table of liked MinistryProfiles and Campaigns to users
- Homepage Functionality:
    * Have a section for highlighting new or popular tags
    * Random Featured Ministry
    * Posts/Campaigns from Liked Ministries
- Show banner image in ograph metadata for media sharing
- Show feedback for denied transaction in `confirm_donation`
- Implement similar ministries/campaigns via Tags to display on Ministry Profile page
- Generator function to create news feed for Ministry Profile (aggregating Campaigns/News Posts, sorted by `pub_date`)

## Hard Release Features
Things to do before Users will be using the site:
- User Attributes:
    * Part of the screening process:
        - "What Church Do You Attend?":
        - Testimony
- Notifications:
    * Email users:
        - Update on the Ministries they like
        - Update admin and reps on MinistryProfile activity
    * Notify Users in Site:
        - Use [this toastr.js library](https://github.com/CodeSeven/toastr) to display notifications retrieved via
        [js Fetch API](https://scotch.io/tutorials/how-to-use-the-javascript-fetch-api-to-get-data)
        - Create notification history
- Better Donation/Transaction UI:
    * Payeezy Direct API
- Static Pages to Add:
    * Privacy Policy
    * Terms of Service
    * Statement of Faith:
        - "What makes LON a Christian Ministry"
- Django-Admin
    * admin link should be visible for superusers who are logged in
    
    
    
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

## Features
### Priority
- User to User messaging
- Church profiles
- Mailing List functionality

### Low Priority
- Commenting
- Enable tooltips
- Help page
- Enable multiple admins and permissions
- Display help on first login
- Milestones for MinistryProfiles (email/notification)
- Map displaying ministry location (via 'explore' tab)

### Unimportant
- Implement authors for NewsPost objects
- Logging for Django
- Social Media logging
- Search functionality should have tags as a search filter

## Deployment Changes
- nginx container should be built via staged loading to acquire certs and avoid nginx config hacks
