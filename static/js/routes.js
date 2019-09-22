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
  .when('/t/donation/:donation_action*', {
        templateUrl : function (params) {
          return '/t/donation/' + params.donation_action;
       },
        controller  : 'donationCtrl'
    })
  .when('/t/ministry/campaign/:campaign_id', {
        templateUrl : function (params) {
          return '/t/ministry/campaign/' + params.campaign_id;
       },
        controller  : 'campaignCtrl'
    })
  .when('/t/ministry/campaign/:campaign_id/:campaign_action*', {
        templateUrl : function (params) {
          return '/t/ministry/campaign/' + params.campaign_id + '/' + params.campaign_action;
        },
        controller  : 'campaignActionCtrl'
    })
  .when('/t/ministry/:ministry_id/campaign/:campaign_action', {
        templateUrl : function (params) {
          return '/t/ministry/' + params.ministry_id + '/campaign/' + params.campaign_action;
        },
        controller  : 'campaignActionCtrl'
    })
  .when('/t/ministry/news/:obj_type/:obj_id/:action', {
        templateUrl : function (params) {
          return '/t/ministry/news/' + params.obj_type + '/' + params.obj_id + '/' + params.action;
        },
        controller  : 'newsCtrl'
    })
  .when('/t/ministry/news/:obj_id/:action', {
      templateUrl : function (params) {
        console.log("here");
        return '/t/ministry/news/' + params.obj_id + '/' + params.action;
      },
      controller  : 'newsCtrl'
    })
  .when('/t/ministry/:ministry_id', {
        templateUrl : function (params) {
          return '/t/ministry/' + params.ministry_id;
       },
        controller  : 'ministryCtrl'
    })
  .when('/t/ministry/:ministry_id/:ministry_action*', {
        templateUrl : function (params) {
          return '/t/ministry/' + params.ministry_id + '/' + params.ministry_action;
        },
        controller  : 'ministryActionCtrl'
    })
   .when('/people/:people_action*', {
        templateUrl : function (params) {
          return '/people/' + params.people_action;
        },
        controller  : 'peopleCtrl',
    })
    .when('/search/:query/', {
        templateUrl : function (params) {
          return '/t/search/' + params.query;
       },
        controller  : 'searchCtrl'
    })
    .when('/search/tag/:query/', {
        templateUrl : function (params) {
          return '/t/search/tag/' + params.query;
       },
        controller  : 'searchTagCtrl'
    });

}]);


// vim:foldmethod=syntax shiftwidth=2 tabstop=2:
