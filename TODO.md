# Immediate Things to Implement
- Static pages:
    * About Us Blurbs
- Help Blurbs for ministries:
    * Explaining start/stop dates (when creating a Campaign)
    * Explaining details in Ministry Profile Page

## Internal Fixes
- Make TinyMCE script to template pages that need it. TinyMCE should not be fetched in 'layout.html'
- Profile Image Functionality:
    * Unify naming within angular functions. eg: remove 'banner' naming
    * Dynamically show selected/uploaded image
    * Dynamic sizing of grid in image selection dialog
    * Better image uploading
- Remove 'login_in_as' functionality. Add settings flag to enable/disable this feature.
- Display of Users Email
- Display users likes
- Title header in cards should provide a link to object.
- Dropdown anchor element item 'Link to ...' should be 'View ...'
- User Widget should provide a link to view ministries
- Edit ministry/campaign page should provide a link to view object
- Clean up utils/ dir. Create a module with utility functions accessible via a CLI or args.
- Admin Interface:
    * Fix login functionality
    * Add donations/payments
- Separate create/edit pages for NewsPost
- Show tags in 'frontpage_ministry_card' widget


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
    * Dynamic MOTD on top
    * Random Featured Ministry
    * Posts/Campaigns from Liked Ministries
- About tab in navigation elements (navbar/sidenav) should be a dropdown showing flatpages.


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
    * Homepage MOTD should be editable via django
    * WYSIWYG editor in django-admin page
    * Admin functions should be better:
        - logout should work
        - admin link should be visible for superusers who are logged in
- Unlike Functionality
- Cards:
    * Add start/end date to campaign cards
    * Add tags to campaign/ministry cards
    
    
    
# Low Priority
## Styling Changes
- Style Email Templates:
    * Password Reset
    * Email Verification
    * Notification/Update Email
- Show start and end dates on campaign card
- Clickable area should not be so big in profile/banner image selection dialog triggers
- 'how_to_reg'/ministry name location in user_widget when 'logged in as'
- MinistryProfile should display profile images on MinistryProfile page
- Progress Bar
- Unify header styling between materialize and angular material
- Better page loading:
    * Navbar User Widget Moves/Resizes
    * In small displays, menu "burger" says 'Menu'
- Profile/Banner Image:
    * Dynamically resize trigger image dimensions
    * Dynamically resize tile dimensions
    * 'Cancel' should undo change
    * 'Done' should upload
    * Banner image trigger should reflect the wide dimensions as it is displayed on view page
- Card offsets button in News tab in Campaign admin panel
- Form buttons in campaign admin panel should match ministry admin panel

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
- Commenting
- Enable tooltips
- Help page
- Implement authors for NewsPost objects
- Enable multiple admins and permissions
- Display help on first login
- Logging for Django
- Mailing List functionality
- Milestones for MinistryProfiles
- Map displaying ministry location (via 'explore' tab)
- User to User messaging
- Social Media logging
- Search functionality should have tags as a search filter

## Deployment Changes
- nginx container should be built via staged loading to acquire certs and avoid nginx config hacks
