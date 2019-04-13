function blankFilterTypes() {
  return {
        'ministry': false,
        'campaign': false,
        'post': false,
        'distance': 0,
  };
};

nav_layout.controller('homeController', ['$scope', '$http', '$location',
  function($scope, $http, $location) {
    // TODO: change title block
    $scope.currentNavItem = 'Home';

    $scope.update_object_periodically();
    $scope.$on('$destroy', function() {
      // Make sure that the interval is destroyed too
      $scope.stop_update();
    });

    ga('send', 'pageview', '/home');
  }
]);

nav_layout.controller('archiveController', ['$scope', '$http', '$location',
  function($scope, $http, $location) {
    // TODO: change title block

    $scope.currentNavItem = 'Archives';

    ga('send', 'pageview', '/campaigns');
  }
]);

nav_layout.controller('faqController', ['$scope', '$http', '$location',
  function($scope, $http, $location) {
    // TODO: change title block

    $scope.currentNavItem = 'FAQ';

    ga('send', 'pageview', '/faq');
  }
]);

nav_layout.controller('aboutController', ['$scope', '$http', '$location',
  function($scope, $http, $location) {
    // TODO: change title block

    $scope.currentNavItem = 'About';

    ga('send', 'pageview', '/about');
  }
]);

nav_layout.controller('campaignCtrl', ['$scope', '$http', '$routeParams', '$location',
  function($scope, $http, $routeParams, $location) {
    // TODO: change title block

    $scope.currentNavItem = 'Home';

    $scope.update_object_periodically();
    $scope.$on('$destroy', function() {
      // Make sure that the interval is destroyed too
      $scope.stop_update();
    });

    ga('send', 'pageview', '/campaigns/' + $routeParams.campaign_id);
  }
]);

nav_layout.controller('campaignActionCtrl', ['$scope', '$http', '$routeParams', '$location',
  function($scope, $http, $routeParams, $location) {
    // TODO: change title block

    $scope.currentNavItem = 'Home';

    if ($routeParams.campaign_action == 'edit' || $routeParams.campaign_action == 'create') {
      $scope.update_object();
      $scope.get_tags();
    }

    ga('send', 'pageview', '/campaigns/' + $routeParams.campaign_id);
  }
]);

nav_layout.controller('newsCtrl', ['$scope', '$http', '$routeParams', '$location', function($scope, $http, $routeParams, $location) {
    // TODO: change title block

    $scope.currentNavItem = 'Home';

    ga('send', 'pageview', '/campaigns/news/' + $routeParams.post_id);
  }
]);

nav_layout.controller('donationCtrl', ['$scope', '$http', '$routeParams', '$location',
  function($scope, $http, $routeParams, $location) {
    // TODO: change title block

    $scope.currentNavItem = null;

    ga('send', 'pageview', '/donation/' + $routeParams.donation_action);
    console.log('donation action: ' + $routeParams.donation_action);
  }
]);

nav_layout.controller('ministryCtrl', ['$scope', '$http', '$routeParams', '$location',
  function($scope, $http, $routeParams, $location) {
    // TODO: change title block

    $scope.currentNavItem = null;

    $scope.update_object_periodically();
    $scope.$on('$destroy', function() {
      // Make sure that the interval is destroyed too
      $scope.stop_update();
    });

    ga('send', 'pageview', '/ministry/' + $routeParams.ministry_action);
    console.log('ministry action: ' + $routeParams.ministry_action);
  }
]);

nav_layout.controller('ministryActionCtrl', ['$scope', '$http', '$routeParams', '$location',
  function($scope, $http, $routeParams, $location) {
    // TODO: change title block

    $scope.currentNavItem = null;

    if ($routeParams.ministry_action == 'edit' || $routeParams.ministry_action == 'edit') {
      $scope.update_object();
      $scope.get_tags();
    }
    if ($routeParams.ministry_action == 'login') {
      $location.url('/ministry/' + $routeParams.ministry_id);
      location.reload();
    }

    ga('send', 'pageview', '/ministry/' + $routeParams.ministry_id + '/' + $routeParams.ministry_action);
    console.log('ministry action: ' + $routeParams.ministry_action + ' of ' + $routeParams.ministry_id);
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

nav_layout.controller('peopleCtrl', ['$scope', '$http', '$route', '$routeParams', '$location',
  function($scope, $http, $route, $routeParams, $location) {
    // TODO: change title block

    $scope.currentNavItem  = null;

    if ($routeParams.people_action == 'alias/logout') {
      $location.url('/accounts/profile');
      location.reload();
    }

    ga('send', 'pageview', '/people/' + $routeParams.people_action);
  }
]);

nav_layout.controller('searchCtrl', ['$scope', '$http', '$route', '$routeParams', '$location',
  function($scope, $http, $route, $routeParams, $location) {
    // TODO: change title block

    $scope.currentNavItem  = null;

    $scope.filter_types = blankFilterTypes();
    function populate_filter_selection() {
      if ($scope.object.ministries.length) {
        $scope.filter_types['ministry'] = true;
      };
      if ($scope.object.campaigns.length) {
        $scope.filter_types['campaign'] = true;
      };
      if ($scope.object.posts.length) {
        $scope.filter_types['post'] = true;
      };
      if ($scope.object.distances.max) {
        $scope.filter_types['distance'] = $scope.object.distances.max;
        $scope.distance = $scope.object.distances.max;
      };
    };

    var url = '/search/' + $routeParams.query + '/json';
    $scope.update_object(url, populate_filter_selection);

    ga('send', 'pageview', '/search/' + $routeParams.query);
  }
]);

nav_layout.controller('searchTagCtrl', ['$scope', '$http', '$route', '$routeParams', '$location',
  function($scope, $http, $route, $routeParams, $location) {
    // TODO: change title block

    $scope.currentNavItem  = null;

    $scope.filter_types = blankFilterTypes();
    function populate_filter_selection() {
      if ($scope.object.ministries.length) {
        $scope.filter_types['ministry'] = true;
      };
      if ($scope.object.campaigns.length) {
        $scope.filter_types['campaign'] = true;
      };
      if ($scope.object.posts.length) {
        $scope.filter_types['post'] = true;
      };
      if ($scope.object.distances.max) {
        $scope.filter_types['distance'] = $scope.object.distances.max;
        $scope.distance = $scope.object.distances.max;
      };
    };

    var url = '/search/tag/' + $routeParams.query + '/json';
    $scope.update_object(url, populate_filter_selection);

    ga('send', 'pageview', '/search/tag/' + $routeParams.query);
  }
]);

// vim:foldmethod=syntax shiftwidth=2 tabstop=2:
