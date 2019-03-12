// Declare single angular module

var nav_layout = angular.module('oneDollarApp', ['ngMaterial', 'ngRoute', 'ngParallax']);

// Layout controller and config //

nav_layout.controller('LayoutCtrl', ['$scope', '$mdSidenav', '$http', '$log', function($scope , $mdSidenav, $http, $log) {

  $scope.toggleLeft = buildDelayedToggler('left');
  $scope.toggleRight = buildToggler('right');
  $scope.isOpenRight = function(){
    return $mdSidenav('right').isOpen();
  };

  $scope.campaign = null;
  /**
   * Supplies a function that will continue to operate until the
   * time is up.
   */
  function debounce(func, wait, context) {
    var timer;
    return function debounced() {
      var context = $scope,
          args = Array.prototype.slice.call(arguments);
      $timeout.cancel(timer);
      timer = $timeout(function() {
        timer = undefined;
        func.apply(context, args);
      }, wait || 10);
    };
  }
  /**
   * Build handler to open/close a SideNav; when animation finishes
   * report completion in console
   */
  function buildDelayedToggler(navID) {
    return debounce(function() {
      // Component lookup should always be available since we are not using `ng-if`
      $mdSidenav(navID)
        .toggle()
        .then(function () {
          $log.debug("toggle " + navID + " is done");
        });
    }, 200);
  }
  function buildToggler(navID) {
    return function() {
      // Component lookup should always be available since we are not using `ng-if`
      $mdSidenav(navID)
        .toggle()
        .then(function () {
          $log.debug("toggle " + navID + " is done");
        });
    }
  }

  $scope.close = function () {
      // Component lookup should always be available since we are not using `ng-if`
      $mdSidenav('right').close()
        .then(function () {
          $log.debug("close RIGHT is done");
        });
    };


  $scope.update_campaign = function(cam_id) {
    $http.get('/campaign/' + cam_id + '/json')
    .then(function(response) {
      $scope.campaign = response.data;
    }, function(response) {});
  };
}]);


nav_layout.config(function($routeProvider) {
  $routeProvider
    .when('/', {
      redirectTo: '/home'
    })

    // Main Pages
    .when('/home', {
        templateUrl : '/t/home',
        controller  : 'homeController'
    })
    .when('/campaigns', {
        templateUrl : '/t/campaigns',
        controller  : 'archiveController'
    })
    .when('/faq', {
        templateUrl : '/t/faq',
        controller  : 'faqController'
    })
    .when('/about', {
        templateUrl : '/t/about',
        controller  : 'aboutController'
    })

    // Media Pages
    .when('/campaign/:campaign_id', {
        templateUrl : function (params) {
          return '/campaign/' + params.campaign_id;
       },
        controller  : 'campaignCtrl'
    })
    .when('/campaign/news/:post_id', {
        templateUrl : function (params) {
          return '/campaign/news/' + params.post_id;
        },
        controller  : 'newsCtrl'
    })
    .when('/accounts/:account_action', {
        templateUrl : function (params) {
          return '/accounts/' + params.account_action;
        },
        controller  : 'accountCtrl'
    });
});


nav_layout.controller('homeController', ['$scope', '$http', '$location',
  function($scope, $http, $location) {
    // TODO: change title block

    $scope.currentNavItem  = 'Home';

    $scope.update_campaign(1);
    setInterval(function() {
        $scope.update_campaign(1);
    }, 15000);

    ga('send', 'pageview', '/home');
  }
]);
nav_layout.controller('archiveController', ['$scope', '$http', '$location',
  function($scope, $http, $location) {
    // TODO: change title block

    $scope.currentNavItem  = 'Archives';

    ga('send', 'pageview', '/campaigns');
  }
]);
nav_layout.controller('faqController', ['$scope', '$http', '$location',
  function($scope, $http, $location) {
    // TODO: change title block

    $scope.currentNavItem  = 'FAQ';

    ga('send', 'pageview', '/faq');
  }
]);
nav_layout.controller('aboutController', ['$scope', '$http', '$location',
  function($scope, $http, $location) {
    // TODO: change title block

    $scope.currentNavItem  = 'About';

    ga('send', 'pageview', '/about');
  }
]);

nav_layout.controller('campaignCtrl', ['$scope', '$http', '$routeParams', '$location',
  function($scope, $http, $routeParams, $location) {
    // TODO: change title block

    $scope.currentNavItem  = 'Home';

    $scope.update_campaign(1);

    ga('send', 'pageview', '/campaigns/' + $routeParams.campaign_id);
  }
]);
nav_layout.controller('newsCtrl', ['$scope', '$http', '$routeParams', '$location',
  function($scope, $http, $routeParams, $location) {
    // TODO: change title block

    $scope.currentNavItem  = 'Home';

    ga('send', 'pageview', '/campaigns/news/' + $routeParams.post_id);
  }
]);
nav_layout.controller('accountCtrl', ['$scope', '$http', '$routeParams', '$location',
  function($scope, $http, $routeParams, $location) {
    // TODO: change title block

    $scope.currentNavItem  = null;

    ga('send', 'pageview', '/account/' + $routeParams.account_action);
    console.log('account action: ' + $routeParams.account_action);
  }
]);


nav_layout.config(function($mdThemingProvider) {
    $mdThemingProvider.theme('default')
        .primaryPalette('purple')
        .accentPalette('orange')
});

// vim:foldmethod=syntax:
