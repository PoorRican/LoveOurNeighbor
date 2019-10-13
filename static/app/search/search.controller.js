angular.module('LON').controller('searchCtrl', searchCtrl);
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
