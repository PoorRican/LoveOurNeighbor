# Immediate Things To Do:
## styling/template changes
* Allow links cards (at least in MOTD cards) to be visible
* Implement [masonry with lightbox plugin](https://dimsemenov.com/plugins/magnific-popup/) for gallery
* On Ministry view template, title should be moved from center-pane to the left for small screens
* On Campaign view template, title should always be on left pane
* Justify profile image in center of if banner image
* Small ministry card, with profile image on side (to squeeze into feeds)
* Integrate [Infinite Scroll](https://infinite-scroll.com/)
* Loading animation on page load; set opacity of inside content to 0.
* Show description/content on ministry/campaign cards
* Expand the features available in TinyMCE (admin panel)
* In Tag Selector, tag shows up as 'object Object'
* HTTP-escape URLs for media filenames
* In Post Gallery, make a single image look big
* Improve menu in Post View
* Change TZ to EST
* Fix django admin-site functionality for Post objects
* Convert `Tag` to contenttype relation


# Metadata / 3rd-party Integration:
- FBLID on Google Analytics
- Add FB App ID
- Test out sharing (OpenGraph)
- Show banner image in ograph metadata for media sharing
- Add [Facebook Like buttons](https://www.dummies.com/web-design-development/site-development/how-to-add-facebook-connect-to-your-website/)
- Implement [social media authentication](https://auth0.com)
- Implement [Autotrack](https://github.com/googleanalytics/autotrack/) for more in-depth analytics
- Google Analytics events:
    * User Created
    * Donation Button Clicked
    * Like Button Clicked


# Immediate Things to Implement
- Turn link tree/sitemap into a global in Python accessible from jinja2 environment
- Turn MotD into modal and fire every first visit
- Static pages:
    * About Us Blurbs
- Help Blurbs for ministries:
    * Explaining details in Ministry Profile Page
- Add Cookie Consent Banner from Termly


## Internal Fixes
- Implement yum-cron for automatic updates [as per here](https://stackoverflow.com/questions/9206261/how-do-install-security-updates-on-an-amazon-linux-ami-ec2-instance)
- Saving User Profile should take you to /home
- Pass HTTP_REFERER to AdminPanel forms to redirect to referring page before going to admin panel
- Profile Image Functionality:
    * Dynamically show selected/uploaded image
    * Dynamic sizing of grid in image selection dialog
- User Profile:
    * Display Users Email
    * Aggregate `tags` to display to User in feed. This should be customizable.
    * Settings for email notifications. E.g: admin notifications, newsletters.
    * Change Password
- Clean up utils/ dir. Create a module with utility functions accessible via a CLI or args.
- Tag should have a method to for search URL
- Automatically create and rename directories by using [django signals](https://docs.djangoproject.com/en/3.0/ref/signals/#django.db.models.signals.pre_save)
- Disable the submit button until FilePond finishes uploading.
- Implement 'nofollow' attribute to social media and WYSIWYG links (ie: Wikipedia)
- Implement 'noopener' on all User generated links


# Medium Priority 
## Soft Release Features
Things to do before ministries will be using the site:
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
- Homepage Functionality:
    * Have a section for highlighting new or popular tags
    * Random Featured Ministry

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
- Change nav header [based upon scroll position](https://pqina.nl/blog/applying-styles-based-on-the-user-scroll-position-with-smart-css/)
- Show newsletter [based upon scroll position](https://pqina.nl/blog/using-smart-css-to-time-your-wonderful-newsletter-popup/)
- Implement countdowns and number visualizations using [flip](https://pqina.nl/flip/)
