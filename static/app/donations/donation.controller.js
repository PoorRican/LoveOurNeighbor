angular.module('LON').controller('donationCtrl', donationCtrl);
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
