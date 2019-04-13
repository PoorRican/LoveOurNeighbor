function blankFilterTypes() {
  return {
        'ministry': false,
        'campaign': false,
        'post': false,
        'distance': 0,
  };
};

// Top-Level View Controllers
nav_layout.controller('homeController', homeController);

homeController.$inject = ['$scope', '$http', '$location'];

function homeController($scope, $http, $location) {
  // TODO: change title block
  $scope.currentNavItem = 'Home';

  $scope.update_object_periodically();
  $scope.$on('$destroy', function() {
    // Make sure that the interval is destroyed too
    $scope.stop_update();
  });

  ga('send', 'pageview', '/home');
};

nav_layout.controller('faqController', faqController);

faqController.$inject = ['$scope', '$http', '$location'];

function faqController($scope, $http, $location) {
  // TODO: change title block

  $scope.currentNavItem = 'FAQ';

  ga('send', 'pageview', '/faq');
};


nav_layout.controller('aboutController', aboutController);

aboutController.$inject = ['$scope', '$http', '$location'];

function aboutController($scope, $http, $location) {
  // TODO: change title block

  $scope.currentNavItem = 'About';

  ga('send', 'pageview', '/about');
}


// Object Controllers

nav_layout.controller('campaignCtrl', campaignCtrl);

campaignCtrl.$inject = ['$scope', '$http', '$routeParams', '$location'];

function campaignCtrl($scope, $http, $routeParams, $location) {
  // TODO: change title block

  $scope.currentNavItem = 'Home';

  $scope.update_object_periodically();
  $scope.$on('$destroy', function() {
    // Make sure that the interval is destroyed too
    $scope.stop_update();
  });

  ga('send', 'pageview', '/campaigns/' + $routeParams.campaign_id);
}


nav_layout.controller('campaignActionCtrl', campaignActionCtrl);

campaignActionCtrl.$inject = ['$scope', '$http', '$routeParams', '$location'];

function campaignActionCtrl($scope, $http, $routeParams, $location) {
  // TODO: change title block

  $scope.currentNavItem = 'Home';

  if ($routeParams.campaign_action == 'edit' || $routeParams.campaign_action == 'create') {
    $scope.update_object();
    $scope.get_tags();
  }

  ga('send', 'pageview', '/campaigns/' + $routeParams.campaign_id);
};


nav_layout.controller('newsCtrl', newsCtrl);

newsCtrl.$inject = ['$scope', '$http', '$routeParams', '$location'];

function newsCtrl($scope, $http, $routeParams, $location) {
  // TODO: change title block

  $scope.currentNavItem = 'Home';

  ga('send', 'pageview', '/campaigns/news/' + $routeParams.post_id);
};


nav_layout.controller('donationCtrl', donationCtrl);

donationCtrl.$inject = ['$scope', '$http', '$routeParams', '$location'];

function donationCtrl($scope, $http, $routeParams, $location) {
  // TODO: change title block

  $scope.currentNavItem = null;

  ga('send', 'pageview', '/donation/' + $routeParams.donation_action);
  console.log('donation action: ' + $routeParams.donation_action);
};


nav_layout.controller('ministryCtrl', ministryCtrl);

ministryCtrl.$inject = ['$scope', '$http', '$routeParams', '$location']

function ministryCtrl($scope, $http, $routeParams, $location) {
  // TODO: change title block

  $scope.currentNavItem = null;

  $scope.update_object_periodically();
  $scope.$on('$destroy', function() {
    // Make sure that the interval is destroyed too
    $scope.stop_update();
  });

  ga('send', 'pageview', '/ministry/' + $routeParams.ministry_action);
  console.log('ministry action: ' + $routeParams.ministry_action);
};


nav_layout.controller('ministryActionCtrl', ministryActionCtrl);

ministryActionCtrl.$inject = ['$scope', '$timeout', '$http', '$routeParams', '$location', 'tagService'];

function ministryActionCtrl($scope, $timeout, $http, $routeParams, $location, tagService) {
  // TODO: change title block

  $scope.currentNavItem = null;

  if ($routeParams.ministry_action == 'edit' || $routeParams.ministry_action == 'edit') {
    $scope.filter_tags = filter_tags;

    tagService.get();
    $scope.update_object();

    function filter_tags(q) {
      return tagService.search(q);
    }
  }
  if ($routeParams.ministry_action == 'login') {
    $location.url('/ministry/' + $routeParams.ministry_id);
    location.reload();
  }

  ga('send', 'pageview', '/ministry/' + $routeParams.ministry_id + '/' + $routeParams.ministry_action);
  console.log('ministry action: ' + $routeParams.ministry_action + ' of ' + $routeParams.ministry_id);
};


nav_layout.controller('accountCtrl', accountCtrl);

accountCtrl.$inject = ['$scope', '$http', '$routeParams', '$location'];

function accountCtrl($scope, $http, $routeParams, $location) {
  // TODO: change title block

  $scope.currentNavItem  = null;

  ga('send', 'pageview', '/account/' + $routeParams.account_action);
  console.log('account action: ' + $routeParams.account_action);
};

nav_layout.controller('peopleCtrl', peopleCtrl);

peopleCtrl.$inject = ['$scope', '$http', '$route', '$routeParams', '$location']

function peopleCtrl($scope, $http, $route, $routeParams, $location) {
  // TODO: change title block

  $scope.currentNavItem  = null;

  if ($routeParams.people_action == 'alias/logout') {
    $location.url('/accounts/profile');
    location.reload();
  }

  ga('send', 'pageview', '/people/' + $routeParams.people_action);
};


// Search Controllers

nav_layout.controller('searchCtrl', searchCtrl);

searchCtrl.$inject = ['$scope', '$http', '$route', '$routeParams', '$location'];

function searchCtrl($scope, $http, $route, $routeParams, $location) {
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
};

nav_layout.controller('searchTagCtrl', searchTagCtrl);
searchTagCtrl.$inject = ['$scope', '$http', '$route', '$routeParams', '$location'];
function searchTagCtrl($scope, $http, $route, $routeParams, $location) {
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
};


// vim:foldmethod=syntax shiftwidth=2 tabstop=2:
