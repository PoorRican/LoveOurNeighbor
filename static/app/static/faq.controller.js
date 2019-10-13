angular.module('LON').controller('faqController', faqController);
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

