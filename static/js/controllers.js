// Top-Level View Controllers
nav_layout.controller('homeController', homeController);

homeController.$inject = ['$scope', '$http', '$location', 'objectService', 'likeButtonService']

function homeController($scope, $http, $location, objectService, likeButtonService) {
  // TODO: change title block
  $scope.object = objectService.get;
  $scope.likeButton = likeButtonService;

  $scope.currentNavItem = 'Home';
  objectService.periodically_fetch();
  $scope.$on('$destroy', function() {
    // Make sure that the interval is destroyed too
    objectService.stop();
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

campaignCtrl.$inject = ['$scope', '$routeParams', 'objectService', 'likeButtonService'];

function campaignCtrl($scope, $routeParams, objectService, likeButtonService) {
  // TODO: change title block
  $scope.object = objectService.get;
  $scope.likeButton = likeButtonService;

  $scope.currentNavItem = 'Home';

  objectService.periodically_fetch();
  $scope.$on('$destroy', function() {
    // Make sure that the interval is destroyed too
    objectService.stop();
  });

  ga('send', 'pageview', '/campaigns/' + $routeParams.campaign_id);
}


nav_layout.controller('campaignActionCtrl', campaignActionCtrl);

campaignActionCtrl.$inject = ['$scope', '$routeParams', 'tagService', 'objectService'];

function campaignActionCtrl($scope, $routeParams, tagService, objectService) {
  // TODO: change title block

  $scope.currentNavItem = 'Home';

  if ($routeParams.campaign_action == 'edit' || $routeParams.campaign_action == 'create') {
    $scope.object = objectService.get;
    $scope.filter_tags = tagService.search;
    $scope.tag_service = tagService;

    objectService.fetch();
    tagService.fetch();
  }

  ga('send', 'pageview', '/campaigns/' + $routeParams.campaign_id);
};


nav_layout.controller('newsCtrl', newsCtrl);

newsCtrl.$inject = ['$scope', '$routeParams'];

function newsCtrl($scope, $routeParams) {
  // TODO: change title block

  $scope.currentNavItem = 'Home';

  ga('send', 'pageview', '/campaigns/news/' + $routeParams.post_id);
};


nav_layout.controller('donationCtrl', donationCtrl);

donationCtrl.$inject = ['$scope', '$routeParams'];

function donationCtrl($scope, $routeParams) {
  // TODO: change title block

  $scope.currentNavItem = null;

  ga('send', 'pageview', '/donation/' + $routeParams.donation_action);
  console.log('donation action: ' + $routeParams.donation_action);
};


nav_layout.controller('ministryCtrl', ministryCtrl);

ministryCtrl.$inject = ['$scope', '$routeParams', 'objectService', 'likeButtonService']

function ministryCtrl($scope, $routeParams, objectService, likeButtonService) {
  // TODO: change title block
  $scope.object = objectService.get;
  $scope.likeButton = likeButtonService;

  $scope.currentNavItem = null;

  objectService.periodically_fetch();
  $scope.$on('$destroy', function() {
    // Make sure that the interval is destroyed too
    objectService.stop();
  });

  ga('send', 'pageview', '/ministry/' + $routeParams.ministry_action);
  console.log('ministry action: ' + $routeParams.ministry_action);
};


nav_layout.controller('ministryActionCtrl', ministryActionCtrl);

ministryActionCtrl.$inject = ['$scope', '$routeParams', 'tagService', 'userFilterService', 'objectService'];

function ministryActionCtrl($scope, $routeParams, tagService, userFilterService, objectService) {
  // TODO: change title block

  $scope.currentNavItem = null;

  if ($routeParams.ministry_action == 'edit' || $routeParams.ministry_action == 'edit') {
    $scope.object = objectService.get;
    $scope.filter_users = userFilterService.search;
    $scope.filter_tags = tagService.search;
    $scope.tagService = tagService;

    tagService.fetch();
    objectService.fetch();
  }
  if ($routeParams.ministry_action == 'login') {
    $location.url('/ministry/' + $routeParams.ministry_id);
    location.reload();
  }

  ga('send', 'pageview', '/ministry/' + $routeParams.ministry_id + '/' + $routeParams.ministry_action);
  console.log('ministry action: ' + $routeParams.ministry_action + ' of ' + $routeParams.ministry_id);
};


nav_layout.controller('peopleCtrl', peopleCtrl);

peopleCtrl.$inject = ['$scope', '$route', '$routeParams', '$location']

function peopleCtrl($scope, $route, $routeParams, $location) {
  // TODO: change title block

  $scope.currentNavItem  = null;

  if ($routeParams.people_action == 'signup') {
  };

  if ($routeParams.people_action == 'login') {
  };

  if ($routeParams.people_action == 'alias/logout') {
    $location.url('/accounts/profile');
    location.reload();
  };

  ga('send', 'pageview', '/people/' + $routeParams.people_action);
};


// Search Controllers

nav_layout.controller('searchCtrl', searchCtrl);

searchCtrl.$inject = ['$scope', '$timeout', '$routeParams', 'objectService', 'searchFilteringService'];

function searchCtrl($scope, $timeout, $routeParams, objectService, searchFilteringService) {
  // TODO: change title block

  $scope.filter_types = searchFilteringService.blank();
  $scope.object = objectService.get;
  $scope.distance = 0;

  $scope.currentNavItem  = null;

  var url = '/search/' + $routeParams.query + '/json';
  objectService.fetch(url);
  $timeout(
  (function(){
    $scope.filter_types = searchFilteringService.populate();
    $scope.distance = $scope.object().distances ? $scope.object().distances.max : 0;
  }), 100);

  ga('send', 'pageview', '/search/' + $routeParams.query);
};


nav_layout.controller('searchTagCtrl', searchTagCtrl);

searchTagCtrl.$inject = ['$scope', '$timeout', '$routeParams', 'objectService', 'searchFilteringService'];

function searchTagCtrl($scope, $timeout, $routeParams, objectService, searchFilteringService) {
  // TODO: change title block
  $scope.filter_types = searchFilteringService.blank();
  $scope.object = objectService.get;
  $scope.distance = 0;

  $scope.currentNavItem  = null;

  var url = '/search/tag/' + $routeParams.query + '/json';
  objectService.fetch(url);
  $timeout(
  (function(){
    $scope.filter_types = searchFilteringService.populate();
    $scope.distance = $scope.object().distances ? $scope.object().distances.max : 0;
  }), 100);

  ga('send', 'pageview', '/search/tag/' + $routeParams.query);
};


// vim:foldmethod=syntax shiftwidth=2 tabstop=2:
