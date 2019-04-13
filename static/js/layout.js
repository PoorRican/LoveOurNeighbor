// Declare single angular module

var nav_layout = angular.module('oneDollarApp',
  ['ngMaterial', 'ngRoute', 'ngParallax']);

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
  $scope.update_object = function(url=null, f=null) {
    if (url == null | angular.isNumber(url)) {
      try {
        url = document.getElementById("current_object_json").value;
      }
      catch(e) {
        $log.warn("no value 'current_object_json' on page...");
        return null;
      }
    };
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

      if (angular.isFunction(f)) {
        f();
      };
    }, function(response) {
      $log.warn('Could not fetch tag list. (Wrong URL?)')});
  };



  $scope.goto = function (url) {
    $location.url(url);
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

  $scope.get_search = function(q=null) {
    if (q == null & $scope.query) { var q = $scope.query; };
    var url = "/search/" + q;
    if (q!=null) {
      $location.url(url);
      $scope.close();
    } else {
      $scope.close();
    }
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


nav_layout.config(function($mdThemingProvider) {
    $mdThemingProvider.theme('default')
        .primaryPalette('orange')
        .accentPalette('purple')
});

// vim:foldmethod=syntax shiftwidth=2 tabstop=2:
