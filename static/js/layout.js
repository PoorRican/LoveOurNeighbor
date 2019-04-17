// Declare single angular module

var nav_layout = angular.module('loveOurNeighborApp',
  ['ngMaterial', 'ngRoute', 'ngParallax', 'ngMessages']);

// Layout controller and config //
nav_layout.controller('LayoutCtrl', LayoutCtrl);

LayoutCtrl.$inject = ['$scope', '$location', 'searchBarService', 'commentService', 'sideNavService', 'notificationService'];

function LayoutCtrl($scope, $location, searchBarService, commentService, sideNavService, notificationService) {

  $scope.sidenav = sideNavService;

  $scope.search = searchBarService.search;
  $scope.comment = commentService;

  $scope.goto = function (url) {
    $location.url(url);
  };

  notificationService.update();


};


nav_layout.config(function($mdThemingProvider) {
    $mdThemingProvider.theme('default')
        .primaryPalette('orange')
        .accentPalette('purple')
});


// vim:foldmethod=syntax shiftwidth=2 tabstop=2:
