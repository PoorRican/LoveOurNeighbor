# High Priority
## Bugs
- Fix timezone error
- GeoIP does not work
- Tag search functionality
- create_campaign_dir not defined when posting news

### Docker Instance exclusive bugs
- New user sign-up does not work
- MinistryProfile creation gives 500 response code

## Internal Fixes
- Make content in WYSIWYG editor required (via JS)
- Make TinyMCE script to template pages that need it. TinyMCE should not be fetched in 'layout.html'
- Implement Fuzzy matching for search function (case-insensitive search)
- Profile Image Functionality:
    * Better image uploading


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
- Implement Password Recovery Feature
- Implement Verification:
    * User Verification
    * Ministry Verification
- Notifications:
    * Email users:
        - Update on the Ministries they like
        - Update admin and reps on MinistryProfile activity
    * Notify Users in Site:
        - Re-implement Angular Notifications
        - Create notification history
- Better Donation/Transaction UI:
    * Payeezy Direct API
- Static Pages to Add:
    * Privacy Policy
    * Terms of Service
    * Statement of Faith:
        - "What makes LON a Christian Ministry"
    
    
    
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
