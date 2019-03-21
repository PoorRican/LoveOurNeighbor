// Declare single angular module

var nav_layout = angular.module('oneDollarApp', ['ngMaterial', 'ngRoute', 'ngParallax']);

// Layout controller and config //

nav_layout.controller('LayoutCtrl', ['$scope', '$mdSidenav', '$http', '$log', '$location', function($scope , $mdSidenav, $http, $log, $location) {

  $scope.toggleLeft = buildDelayedToggler('left');
  $scope.toggleRight = buildToggler('right');
  $scope.isOpenRight = function(){
    return $mdSidenav('right').isOpen();
  };

  $scope.object = {};
  $scope.update_interval_id = 0;
  $scope.query = null;
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


  $scope.update_object = function() {
    var url = document.getElementById("current_object_json").value
    $http.get(url)
    .then(function(response) {
      $scope.object = response.data;
    }, function(response) {});
  };


  $scope.like = function(url) {
    $http.get(url)
    .then(function(response) {
      $scope.object.liked = response.data;
    }, function(response) {});
  };

  $scope.like_style = function() {
    if ($scope.object && $scope.object.liked) {
      return {'background-color': '#FF7100'};
    } else {
      return {'background-color': '#EEE'};
    }
  };

  $scope.get_search = function() {
    var url = "/ministry/search/" + $scope.query;
    $location.url(url);
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
    .when('/accounts/:account_action*', {
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

    if ($scope.update_interval_id) { clearInterval($scope.update_interval_id); }
    $scope.update_object();
    $scope.update_interval_id = setInterval(function() {
        $scope.update_object();
    }, 15000);

    ga('send', 'pageview', '/home');
  }
]);

nav_layout.controller('archiveController', ['$scope', '$http', '$location',
  function($scope, $http, $location) {
    // TODO: change title block

    $scope.currentNavItem  = 'Archives';

    clearInterval($scope.update_interval_id);

    ga('send', 'pageview', '/campaigns');
  }
]);

nav_layout.controller('faqController', ['$scope', '$http', '$location',
  function($scope, $http, $location) {
    // TODO: change title block

    $scope.currentNavItem  = 'FAQ';

    clearInterval($scope.update_interval_id);

    ga('send', 'pageview', '/faq');
  }
]);

nav_layout.controller('aboutController', ['$scope', '$http', '$location',
  function($scope, $http, $location) {
    // TODO: change title block

    $scope.currentNavItem  = 'About';

    clearInterval($scope.update_interval_id);

    ga('send', 'pageview', '/about');
  }
]);

nav_layout.controller('campaignCtrl', ['$scope', '$http', '$routeParams', '$location',
  function($scope, $http, $routeParams, $location) {
    // TODO: change title block

    $scope.currentNavItem  = 'Home';

    clearInterval($scope.update_interval_id);
    $scope.update_object();
    setInterval(function() {
        $scope.update_object();
    }, 15000);

    ga('send', 'pageview', '/campaigns/' + $routeParams.campaign_id);
  }
]);

nav_layout.controller('campaignActionCtrl', ['$scope', '$http', '$routeParams', '$location',
  function($scope, $http, $routeParams, $location) {
    // TODO: change title block

    $scope.currentNavItem  = 'Home';

    clearInterval($scope.update_interval_id);

    ga('send', 'pageview', '/campaigns/' + $routeParams.campaign_id);
  }
]);

nav_layout.controller('newsCtrl', ['$scope', '$http', '$routeParams', '$location',
  function($scope, $http, $routeParams, $location) {
    // TODO: change title block

    $scope.currentNavItem  = 'Home';

    clearInterval($scope.update_interval_id);

    ga('send', 'pageview', '/campaigns/news/' + $routeParams.post_id);
  }
]);

nav_layout.controller('ministryCtrl', ['$scope', '$http', '$routeParams', '$location',
  function($scope, $http, $routeParams, $location) {
    // TODO: change title block

    $scope.currentNavItem  = null;

    clearInterval($scope.update_interval_id);
    $scope.update_object();
    $scope.update_interval_id = setInterval(function() {
        $scope.update_object();
    }, 15000);

    ga('send', 'pageview', '/ministry/' + $routeParams.ministry_action);
    console.log('ministry action: ' + $routeParams.ministry_action);
  }
]);

nav_layout.controller('ministryActionCtrl', ['$scope', '$http', '$routeParams', '$location',
  function($scope, $http, $routeParams, $location) {
    // TODO: change title block

    $scope.currentNavItem  = null;

    clearInterval($scope.update_interval_id);

    ga('send', 'pageview', '/ministry/' + $routeParams.ministry_id + '/' + $routeParams.ministry_action);
    console.log('ministry action: ' + $routeParams.ministry_action + ' of ' + $routeParams.ministry_id);
  }
]);

nav_layout.controller('accountCtrl', ['$scope', '$http', '$routeParams', '$location',
  function($scope, $http, $routeParams, $location) {
    // TODO: change title block

    $scope.currentNavItem  = null;

    clearInterval($scope.update_interval_id);

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
