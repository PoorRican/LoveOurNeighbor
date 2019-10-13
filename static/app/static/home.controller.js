angular.module('LON').controller('homeController', homeController);
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
