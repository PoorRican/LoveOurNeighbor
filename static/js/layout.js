// Declare single angular module

var nav_layout = angular.module('oneDollarApp', ['ngMaterial', 'ngRoute', 'ngParallax']);

// Layout controller and config //

nav_layout.controller('LayoutCtrl', ['$scope', '$interval', '$mdSidenav', '$http', '$log', '$location', '$mdConstant', function($scope, $interval, $mdSidenav, $http, $log, $location, $mdConstant) {
  $scope.separatorKeys = [$mdConstant.KEY_CODE.ENTER, $mdConstant.KEY_CODE.COMMA];

  $scope.toggleLeft = buildDelayedToggler('left');
  $scope.toggleRight = buildToggler('right');
  $scope.isOpenRight = function(){
    return $mdSidenav('right').isOpen();
  };
  $scope.profileMenuOpen = false;
  $scope.openProfileMenuDown = function() {
    $scope.profileMenuOpen = !($scope.profileMenuOpen);
  }


  $scope.query = null;


  var update_interval_id = 0;
  $scope.object = {};

  $scope.stop_update = function() {
    if (angular.isDefined(update_interval_id)) {
      $interval.cancel(update_interval_id);
      update_interval_id = undefined;
    };
  };
  $scope.update_object_periodically = function() {
    $scope.update_object();
    update_interval_id = $interval($scope.update_object, 15000);
  };
  $scope.update_object = function() {
    try {
      var url = document.getElementById("current_object_json").value;
    }
    catch(e) {
      $log.warn("no value 'current_object_json' on page...");
      return null;
    }
    $http.get(url)
    .then(function(response) {
      var data = response.data;
      if (data.founded) {
        data.founded = new Date(data.founded);
      };
      if (data.start_date) {
        data.start_date = new Date(data.start_date);
      };
      if (data.end_date) {
        data.end_date = new Date(data.end_date);
      };
      $scope.object = data;
    }, function(response) {
      $log.warn('Could not fetch tag list. (Wrong URL?)')});
  };


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

  /**
   * Return the proper object when the append is called.
   */
  $scope.transformChip = function (chip) {
    // If it is an object, it's already a known chip
    if (angular.isObject(chip)) {
      return chip;
    }

    // Otherwise, create a new one
    return chip;
  };

  $scope.get_tags = function() {
    var url = '/ministry/tags/all';
    $http.get(url)
    .then(function(response) {
      var data = response.data;
      $scope.available_tags = data;
    }, function(response) {
      $log.warn('Could not fetch tag list. (Wrong URL?)')});
  };

  $scope.tagSearch = function(query) {
    function createTagFilter(query) {
      var loweredQuery = query.toLowerCase();

      return function filterFn(tag) {
        return (tag.indexOf(loweredQuery) === 0);
      };
    };

    return query ? $scope.available_tags.filter(createTagFilter(query)) : [];
  };

  $scope.contactSearch = function(query) {
    /**
     * Create filter function for a query string
     */
    function createContactFilter(query) {
      var lowercaseQuery = query.toLowerCase();

      return function filterFn(contact) {
        return (contact.name.toLowerCase().indexOf(lowercaseQuery) === 0) ||
            (contact.email.toLowerCase().indexOf(lowercaseQuery) === 0);
      };
    };

      return query ? $scope.object.requests.filter(createContactFilter(query)) : [];
  };

  $scope.like = function(url) {
    $http.get(url)
    .then(function(response) {
      $scope.object.liked = response.data;
    }, function(response) {});
    $scope.update_object();
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

  /** Controls the display of new comment forms on the page.
   *
   *  All elements of 'new_comment' are styled (forms hidden, buttons shown).
   *  Then the targeted comment form is shown and the button is hidden.
   *  This ensures that only a single form is shown at a time.
   *
   *  TODO: comment form should be dynamically created instead of hardcoded
   **/
  $scope.unhide_new_comment = function(event) {

    // reset all 'new_comment' divs to default styling
    var new_comment_divs = document.getElementsByClassName('new_comment');
    for (d = 0; d < new_comment_divs.length; d++) {
      new_comment_divs[d].children[0].style.display = 'none';
      new_comment_divs[d].children[1].style.display = 'block';
    }

    // style selected form and button respectively
    if ($(event.target).parent().parent()[0].classList.value.includes("wrapper")) {
      // clicked button and not inner text. therefore, dont unpack as many parent elements
      $(event.target).parent().children().css('display', 'block');
      $(event.target).css('display', 'none');
    } else {
      $(event.target).parent().parent().children().css('display', 'block');
      $(event.target).parent().css('display', 'none');
    };
  };

  $scope.hide_new_comment = function(event) {
    // hide selected form and button respectively
    if ($(event.target).parent().parent().parent()[0].classList.value.includes("wrapper")) {
      // clicked button and not inner text. therefore, dont unpack as many parent elements
      $(event.target).parent().parent().children().css('display', 'block');
      $(event.target).parent().css('display', 'none');
    } else {
      $(event.target).parent().parent().parent().children().css('display', 'block');
      $(event.target).parent().parent().css('display', 'none');
    };
  };
}]);


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
    .when('/accounts/:account_action*', {
        templateUrl : function (params) {
          return '/accounts/' + params.account_action;
        },
        controller  : 'accountCtrl'
    })
    .when('/people/:people_action*', {
        templateUrl : function (params) {
          return '/people/' + params.people_action;
        },
        controller  : 'peopleCtrl'
    });
}]);


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
    if ($routeParams.ministry_id == 'search') {
      $scope.update_object();
      $scope.filtered_results = $scope.object.results;
      console.log($scope.object.results);
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


nav_layout.config(function($mdThemingProvider) {
    $mdThemingProvider.theme('default')
        .primaryPalette('orange')
        .accentPalette('purple')
        .dark()
});

// vim:foldmethod=syntax:
