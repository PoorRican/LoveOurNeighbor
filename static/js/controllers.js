// Top-Level View Controllers
nav_layout.controller('homeController', homeController);
homeController.$inject = ['$scope', '$http', '$location', 'objectService', 'likeButtonService'];

function homeController($scope, $http, $location, objectService, likeButtonService) {
  // TODO: change title block
  $scope.object = objectService.get;
  $scope.likeButton = likeButtonService;

  $scope.currentNavItem = 'Home';

  $scope.share.reset();               // share button
  objectService.periodically_fetch();

  $scope.$on('$destroy', function() {
    // Make sure the interval is no longer running
    objectService.stop();
  });

  ga('send', 'pageview', '/home');
}


nav_layout.controller('faqController', faqController);
faqController.$inject = ['$scope', '$http', '$location'];

function faqController($scope, $http, $location) {
  // TODO: change title block

  $scope.currentNavItem = 'FAQ';

  // share button
  $scope.share.reset();
  $scope.share.set('title', 'Frequently Asked Questions - Love Our Neighbor');
  $scope.share.set('url', 'https://loveourneighbor.org/FAQ');
  $scope.share.update_dom();

  ga('send', 'pageview', '/faq');
}


nav_layout.controller('aboutController', aboutController);
aboutController.$inject = ['$scope', '$http', '$location'];

function aboutController($scope, $http, $location) {
  // TODO: change title block

  $scope.currentNavItem = 'About';

  // share button
  $scope.share.reset();
  $scope.share.set('title', 'About Love Our Neighbor');
  $scope.share.set('url', 'https://loveourneighbor.org/about');
  $scope.share.update_dom();

  ga('send', 'pageview', '/about');
}


// Campaign Controllers
nav_layout.controller('campaignCtrl', campaignCtrl);
campaignCtrl.$inject = ['$scope', '$routeParams', 'objectService', 'likeButtonService', 'galleryService'];

function campaignCtrl($scope, $routeParams, objectService, likeButtonService, galleryService) {
  // TODO: change title block
  $scope.object = objectService.get;
  $scope.likeButton = likeButtonService;

  $scope.currentNavItem = 'Home';

  $scope.gallery = [];

  // activate dynamic content
  activate();
  share_button();

  // activate dynamic content
  $scope.$on('$destroy', function() {
    // Make sure the interval is no longer running
    objectService.stop();
  });

  function activate() {
    // get campaign content
    objectService.periodically_fetch();

    // get gallery content
    var gallery_url = "/t/ministry/campaign/" + $routeParams.campaign_id + "/gallery/json";
    return galleryService.get(gallery_url)
      .then(function(data) {
        $scope.gallery = data;
      })
  }

  function share_button() {
    // hack to update share button with attributes from objectService because promises don't seem to be working
    $scope.share.reset();

    $timeout(update_dom, 250);

    function update_dom() {
      $scope.share.set('title', 'Check out this fundraiser for ' + $scope.object().name + ' on Love Our Neighbor!');
      $scope.share.set('url', 'https://loveourneighbor.org' + $scope.object().url.substr(2));
      $scope.share.update_dom();
    }
  }
  ga('send', 'pageview', '/campaigns/' + $routeParams.campaign_id);
}

nav_layout.controller('campaignActionCtrl', campaignActionCtrl);
campaignActionCtrl.$inject = ['$scope', '$routeParams', 'tagService', 'objectService', 'bannerImageService'];

function campaignActionCtrl($scope, $routeParams, tagService, objectService, bannerImageService) {
  // TODO: change title block

  $scope.currentNavItem = 'Home';
  $scope.share.disabled = true;

  if ($routeParams.campaign_action === 'create') {
    $scope.object = {'tags': []};     // work around
    $scope.filter_tags = tagService.search;
    $scope.tag_service = tagService;
    tagService.fetch();
  }
  if ($routeParams.campaign_action === 'edit') {
    $scope.object = objectService.get;
    $scope.filter_tags = tagService.search;
    $scope.tag_service = tagService;

    $scope.banner_urls = {};
    $scope.select_banner = select_banner;
    $scope.banner_img_dialog = bannerImageService;
    $scope.selected_banner = $scope.banner_img_dialog.selected;

    $scope.profile_img_urls = {};
    $scope.select_profile_img = select_profile_img;
    $scope.profile_img_dialog = bannerImageService;
    $scope.selected_profile_img = $scope.profile_img_dialog.selected;

    activate();

    function select_banner(name) {
      // this is a dirty hack, but it works.....
      // for some reason, the selected attribute is never updated via $watch/$digest
      $scope.banner_img_dialog.select(name);
      $scope.selected_banner = name;
    }

    function select_profile_img(name) {
      // this is a dirty hack, but it works.....
      // for some reason, the selected attribute is never updated via $watch/$digest
      $scope.profile_img_dialog.select(name);
      $scope.selected_profile_img = name;
    }

    function activate() {
      if ($routeParams.campaign_id) {
        var banners_url = "/t/ministry/campaign/" + $routeParams.campaign_id + "/banners/json";
        bannerImageService.get(banners_url)
        .then(function (data) {
          $scope.banner_urls = data;

        });

        var profile_img_url = "/t/ministry/campaign/" + $routeParams.campaign_id + "/profile_img/json";
        bannerImageService.get(profile_img_url)
        .then(function (data) {
          $scope.profile_img_urls = data;

        });
      }   // TODO: grab ministry banners when creating new campaign

      tagService.fetch();

      return objectService.fetch()
        .then(function(data) {
          $scope.object = data;
        }
      );
    }
  }

  ga('send', 'pageview', '/campaigns/' + $routeParams.campaign_id);
}


// News Controller
nav_layout.controller('newsCtrl', newsCtrl);
newsCtrl.$inject = ['$scope', '$routeParams'];

function newsCtrl($scope, $routeParams) {
  // TODO: change title block

  $scope.currentNavItem = 'Home';

  // share button
  $scope.share.reset();
  $scope.share.set('title', 'Check out what God has done through this ministry!');
  $scope.share.set('url', 'https://loveourneighbor.org/ministry/' + $routeParams.post_id);
  $scope.share.update_dom();

  ga('send', 'pageview', '/campaigns/news/' + $routeParams.post_id);
}


// Donation Controller
nav_layout.controller('donationCtrl', donationCtrl);
donationCtrl.$inject = ['$scope', '$routeParams'];

function donationCtrl($scope, $routeParams) {
  // TODO: change title block

  $scope.currentNavItem = null;
  console.log($routeParams.donation_action);

  // share button
  if ($routeParams.donation_action === 'admin') {   // sharing of administrative page
    $scope.share.reset();
    $scope.share.set('title', 'Help support Love Our Neighbor');
    $scope.share.set('url', 'https://loveourneighbor.org/donation/admin');
    $scope.share.update_dom();
  } else {
    $scope.share.disabled = true;
  }

  ga('send', 'pageview', '/donation/' + $routeParams.donation_action);
  console.log('donation action: ' + $routeParams.donation_action);
}


// Ministry Controllers
nav_layout.controller('ministryCtrl', ministryCtrl);
ministryCtrl.$inject = ['$scope', '$routeParams', '$timeout', 'objectService', 'likeButtonService', 'galleryService'];

function ministryCtrl($scope, $routeParams, $timeout, objectService, likeButtonService, galleryService) {
  // TODO: change title block
  $scope.object = objectService.get;
  $scope.likeButton = likeButtonService;

  $scope.currentNavItem = null;
  $scope.gallery = [];

  // activate dynamic content
  activate();
  share_button();

  $scope.$on('$destroy', function() {
    // stop periodic updating
    objectService.stop();
  });

  function activate() {
    // get ministry content
    objectService.periodically_fetch();

    // get gallery content
    var gallery_url = "/t/ministry/" + $routeParams.ministry_id + "/gallery/json";
    return galleryService.get(gallery_url)
      .then(function(data) {
        $scope.gallery = data;
      })
  }

  function share_button() {
    // hack to update share button with attributes from objectService because promises don't seem to be working
    $scope.share.reset();

    $timeout(update_dom, 250);

    function update_dom() {
      $scope.share.set('title', 'Check out the ministry profile for "' + $scope.object().name + '" on Love Our Neighbor!');
      $scope.share.set('url', 'https://loveourneighbor.org' + $scope.object().url.substr(2));
      $scope.share.update_dom();
    }
  }

  ga('send', 'pageview', '/ministry/' + $routeParams.ministry_id);
}

nav_layout.controller('ministryActionCtrl', ministryActionCtrl);
ministryActionCtrl.$inject = ['$scope', '$location', '$routeParams', 'tagService', 'userFilterService', 'objectService', 'bannerImageService'];

function ministryActionCtrl($scope, $location, $routeParams, tagService, userFilterService, objectService, bannerImageService) {
  // TODO: change title block

  $scope.currentNavItem = null;
  $scope.share.disabled = true;

  if ($routeParams.ministry_action === 'edit' || $routeParams.ministry_action === 'create') {
    $scope.object = {};

    $scope.filter_users = userFilterService.search;
    $scope.filter_tags = tagService.search;

    $scope.tagService = tagService;

    $scope.banner_urls = {};
    $scope.select_banner = select_banner;
    $scope.banner_img_dialog = bannerImageService;
    $scope.selected_banner = $scope.banner_img_dialog.selected;

    $scope.profile_img_urls = {};
    $scope.select_profile_img = select_profile_img;
    $scope.profile_img_dialog = bannerImageService;
    $scope.selected_profile_img = $scope.profile_img_dialog.selected;

    activate();
    tagService.fetch();

    function select_banner(name) {
      // this is a dirty hack, but it works.....
      // for some reason, the selected attribute is never updated via $watch/$digest
      $scope.banner_img_dialog.select(name);
      $scope.selected_banner = name;
    }

    function select_profile_img(name) {
      // this is a dirty hack, but it works.....
      // for some reason, the selected attribute is never updated via $watch/$digest
      $scope.profile_img_dialog.select(name);
      $scope.selected_profile_img = name;
    }

    function activate() {
      var banners_url = "/t/ministry/" + $routeParams.ministry_id + "/banners/json";
      bannerImageService.get(banners_url)
      .then(function(data) {
        $scope.banner_urls = data;

      });

      var profile_img_url = "/t/ministry/" + $routeParams.ministry_id + "/profile_img/json";
      bannerImageService.get(profile_img_url)
      .then(function(data) {
        $scope.profile_img_urls = data;

      });

      return objectService.fetch()
      .then(function(data) {
          $scope.object = data;
        }
      );
    }
  }
  if ($routeParams.ministry_action === 'login') {
    $location.url('/ministry/' + $routeParams.ministry_id);
    location.reload();
  }

  ga('send', 'pageview', '/ministry/' + $routeParams.ministry_id + '/' + $routeParams.ministry_action);
  console.log('ministry action: ' + $routeParams.ministry_action + ' of ' + $routeParams.ministry_id);
}


// User Profile Controller
nav_layout.controller('peopleCtrl', peopleCtrl);
peopleCtrl.$inject = ['$scope', '$route', '$routeParams', '$location'];

function peopleCtrl($scope, $route, $routeParams, $location) {
  // TODO: change title block

  $scope.currentNavItem  = null;
  $scope.share.disabled = true;

  if ($routeParams.people_action === 'create') {
    $scope.cleanPasswordPattern = cleanPasswordPattern;

    function cleanPasswordPattern() {
      var cleaned = $scope.password;
      if (cleaned) {
        var chars = [
          [/\\/g, '\\\\'],
          [/\*/g, '\\*'],
          [/\^/g, '\\^'],
          [/\$/g, '\\$'],
          [/\+/g, '\\+'],
          [/\?/g, '\\?'],
          [/\./g, '\\.'],
          [/\(/g, '\\('],
          [/\)/g, '\\)'],
          [/\|/g, '\\|'],
          [/{/g, '\\{'],
          [/}/g, '\\}']
        ];
        for (var i = 0; i < chars.length; i++) {
          cleaned = cleaned.replace(chars[i][0], chars[i][1]);
        }
        return cleaned;
      }
    }
  }
  if ($routeParams.people_action === 'login') {
  }
  if ($routeParams.people_action === 'alias/logout') {
    $location.url('/accounts/profile');
    location.reload();
  }
  ga('send', 'pageview', '/people/' + $routeParams.people_action);
}


// Search Controllers
nav_layout.controller('searchCtrl', searchCtrl);
searchCtrl.$inject = ['$scope', '$timeout', '$routeParams', 'objectService', 'searchFilteringService'];

function searchCtrl($scope, $timeout, $routeParams, objectService, searchFilteringService) {
  // TODO: change title block

  $scope.filter_types = searchFilteringService.blank();
  $scope.object = {};
  $scope.distance = 0;

  $scope.currentNavItem  = null;

  // share button
  $scope.share.reset();
  $scope.share.set('title', 'Check out all of these ministries on Love Our Neighbor');
  $scope.share.set('url', 'https://loveourneighbor.org/search/' + $routeParams.query);
  $scope.share.update_dom();

  activate();

  function activate() {
    var url = '/t/search/' + $routeParams.query + '/json';
    return objectService.fetch(url)
      .then(function(data) {
        $scope.distance = data.distances ? data.distances.max : 0;
        $scope.filter_types = searchFilteringService.populate();
        $scope.object = data;
      }
    );
  }
  ga('send', 'pageview', '/search/' + $routeParams.query);
}

nav_layout.controller('searchTagCtrl', searchTagCtrl);
searchTagCtrl.$inject = ['$scope', '$timeout', '$routeParams', 'objectService', 'searchFilteringService'];

function searchTagCtrl($scope, $timeout, $routeParams, objectService, searchFilteringService) {
  // TODO: change title block
  $scope.filter_types = searchFilteringService.blank();
  $scope.object = {};
  $scope.distance = 0;

  $scope.currentNavItem  = null;

  // share button
  $scope.share.reset();
  $scope.share.set('title', 'Check out all of these ministries regarding ' + $routeParams.query + ' on Love Our Neighbor');
  $scope.share.set('url', 'https://loveourneighbor.org/search/tag/' + $routeParams.query);
  $scope.share.update_dom();

  activate();

  function activate() {
    var url = '/t/search/' + $routeParams.query + '/json';
    return objectService.fetch(url)
      .then(function(data) {
        $scope.distance = data.distances ? data.distances.max : 0;
        $scope.filter_types = searchFilteringService.populate();
        $scope.object = data;
      }
    );
  }
  ga('send', 'pageview', '/search/tag/' + $routeParams.query);
}

// vim:foldmethod=syntax shiftwidth=2 tabstop=2:
