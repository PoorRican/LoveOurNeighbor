// Declare single angular module

var nav_layout = angular.module('loveOurNeighborApp',
  ['ngMaterial', 'ngRoute', 'ngParallax']);

// Layout controller and config //
nav_layout.controller('LayoutCtrl', LayoutCtrl);

LayoutCtrl.$inject = ['$scope', 'searchBarService', 'commentService', 'sideNavService'];

function LayoutCtrl($scope, searchBarService, commentService, sideNavService) {

  $scope.sidenav = sideNavService;

  $scope.search = searchBarService.search;
  $scope.comment = commentService;

  $scope.goto = function (url) {
    $location.url(url);
  };


};


nav_layout.config(function($mdThemingProvider) {
    $mdThemingProvider.theme('default')
        .primaryPalette('orange')
        .accentPalette('purple')
});


// vim:foldmethod=syntax shiftwidth=2 tabstop=2:
