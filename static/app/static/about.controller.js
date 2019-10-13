angular.module('LON').controller('aboutController', aboutController);
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
