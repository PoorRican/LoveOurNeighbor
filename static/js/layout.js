// Declare single angular module

var nav_layout = angular.module('loveOurNeighborApp',
  ['ngMaterial', 'ngRoute', 'ngParallax']);

// Layout controller and config //
nav_layout.controller('LayoutCtrl', LayoutCtrl);

LayoutCtrl.$inject = ['$scope', '$interval', '$mdSidenav', '$http', '$log', '$location', '$mdConstant', 'searchBarService'];

function LayoutCtrl($scope, $interval, $mdSidenav, $http, $log, $location, $mdConstant, searchBarService) {
  $scope.separatorKeys = [$mdConstant.KEY_CODE.ENTER, $mdConstant.KEY_CODE.COMMA];

  $scope.toggleLeft = buildDelayedToggler('left');
  $scope.toggleRight = buildToggler('right');
  $scope.isOpenRight = function(){
    return $mdSidenav('right').isOpen();
  };

  $scope.search = searchBarService.search;

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
};


nav_layout.config(function($mdThemingProvider) {
    $mdThemingProvider.theme('default')
        .primaryPalette('orange')
        .accentPalette('purple')
});


// vim:foldmethod=syntax shiftwidth=2 tabstop=2:
