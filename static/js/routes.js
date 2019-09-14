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
    .when('/ministry/:ministry_id/campaign/:campaign_action', {
        templateUrl : function (params) {
          return '/ministry/' + params.ministry_id + '/campaign/' + params.campaign_action;
        },
        controller  : 'campaignActionCtrl'
    })
    .when('/ministry/news/:obj_type/:obj_id/:action', {
        templateUrl : function (params) {
          return '/ministry/news/' + params.obj_type + '/' + params.obj_id + '/' + params.action;
        },
        controller  : 'newsCtrl'
    })
    .when('/ministry/news/:obj_id/:action', {
      templateUrl : function (params) {
        console.log("here");
        return '/ministry/news/' + params.obj_id + '/' + params.action;
      },
      controller  : 'newsCtrl'
    })
    .when('/ministry/:ministry_id', {
        templateUrl : function (params) {
          return '/ministry/' + params.ministry_id;
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
        controller  : 'peopleCtrl',
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
