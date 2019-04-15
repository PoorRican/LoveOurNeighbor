nav_layout.config(['$locationProvider', '$routeProvider', function($locationProvider, $routeProvider) {
  $locationProvider.hashPrefix('');

  $routeProvider
    .when('/', {
      redirectTo: '/home'
    })

    // Main Pages
    .when('/home', {
        templateUrl : '/t/home',
        controller  : 'homeController'
    })
    .when('/faq', {
        templateUrl : '/t/faq',
        controller  : 'faqController'
    })
    .when('/about', {
        templateUrl : '/t/about',
        controller  : 'aboutController'
    })

    // Main Functionality
    .when('/donation/:donation_action*', {
        templateUrl : function (params) {
          return '/donation/' + params.donation_action;
       },
        controller  : 'donationCtrl'
    })
    .when('/ministry/campaign/:campaign_id', {
        templateUrl : function (params) {
          return '/ministry/campaign/' + params.campaign_id;
       },
        controller  : 'campaignCtrl'
    })
    .when('/ministry/campaign/:campaign_id/:campaign_action*', {
        templateUrl : function (params) {
          return '/ministry/campaign/' + params.campaign_id + '/' + params.campaign_action;
       },
        controller  : 'campaignActionCtrl'
    })
    .when('/ministry/campaign/news/:post_id', {
        templateUrl : function (params) {
          return '/campaign/news/' + params.post_id;
        },
        controller  : 'newsCtrl'
    })
    .when('/ministry/:ministry_action', {
        templateUrl : function (params) {
          return '/ministry/' + params.ministry_action;
       },
        controller  : 'ministryCtrl'
    })
    .when('/ministry/:ministry_id/:ministry_action*', {
        templateUrl : function (params) {
          return '/ministry/' + params.ministry_id + '/' + params.ministry_action;
       },
        controller  : 'ministryActionCtrl'
    })
   .when('/people/:people_action*', {
        templateUrl : function (params) {
          return '/people/' + params.people_action;
        },
        controller  : 'peopleCtrl'
    })
    .when('/search/:query/', {
        templateUrl : function (params) {
          return '/search/' + params.query;
       },
        controller  : 'searchCtrl'
    })
    .when('/search/tag/:query/', {
        templateUrl : function (params) {
          return '/search/tag/' + params.query;
       },
        controller  : 'searchTagCtrl'
    });

}]);


// vim:foldmethod=syntax shiftwidth=2 tabstop=2: