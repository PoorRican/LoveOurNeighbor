angular.module('LON').controller('searchCtrl', searchCtrl);
searchCtrl.$inject = ['$scope', '$timeout', 'objectService', 'searchFilteringService'];

function searchCtrl($scope, $timeout, objectService, searchFilteringService) {

  $scope.filter_types = searchFilteringService.blank();
  $scope.object = {};
  $scope.distance = 0;

  activate();

  function activate() {
    return objectService.fetch()
    .then(function(data) {
        $scope.distance = data.distances ? data.distances.max : 0;
        $scope.object = data;
      $scope.filter_types = searchFilteringService.populate($scope.object);
      }
    );
  }
}
