## Bugs
- GeoIP does not work
- Tag search functionality
- create_campaign_dir not defined when posting news
- Default value of "None" in 'ministry:edit_ministry'

### Docker Instance exclusive bugs
- New user sign-up does not work
- MinistryProfile creation gives 500 response code
- Accessing 'ministry:ministry_profile' gives 500 response
- Duplicate how_to_reg icon in user_widget
- invalid url for MinistryProfile image in user widget '//mediafiles/...'


## Internal Fixes
- Make content in WYSIWYG editor required (via JS)
- Make TinyMCE script to template pages that need it. TinyMCE should not be fetched in 'layout.html'
- Implement Fuzzy matching for search function (case-insensitive search)
- Profile Image Functionality:
    * Better image uploading
- Remove comments stub / Remove 'login_in_as' functionality. Add settings flag to enable/disable this feature
- Display of Users Email
- Display users likes


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
- News Tabs in Profile Edit Page
- Unverified Ministries should not be able to create Campaigns


## Hard Release Features
Things to do before Users will be using the site:
- Remove comment placeholders
- Show table of liked MinistryProfiles and Campaigns to users
- Homepage Functionality:
    * Functions for:
        - recently created ministries
        - recently created campaigns
    * Card Display
    * Have a section for highlighting new or popular tags
    * Dynamic MOTD on top
    * Random Featured Ministry
- Implement Ministry Verification:
- User Attributes:
    Part of the screening process:
        * "What Church Do You Attend?":
        * Testimony
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
    
    
    
# Low Priority
## Styling Changes
- Style Email Templates:
    * Password Reset
    * Email Verification
    * Notification/Update Email
- Show start and end dates on campaign card
- MinistryProfile should display profile images on MinistryProfile page
- Progress Bar

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
