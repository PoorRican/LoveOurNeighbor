angular.module('LON').controller('campaignCtrl', campaignCtrl);
campaignCtrl.$inject = ['$scope', '$routeParams', '$timeout', 'objectService', 'likeButtonService', 'galleryService'];

function campaignCtrl($scope, $routeParams, $timeout, objectService, likeButtonService, galleryService) {
  $scope.object = objectService.get;
  $scope.likeButton = likeButtonService;

  $scope.gallery = [];

  // activate dynamic content
  activate();

  // activate dynamic content
  $scope.$on('$destroy', function() {
    // Make sure the interval is no longer running
    objectService.stop();
  });

  function activate() {
    const campaign_id = document.getElementById('campaign_id').value;
    // get campaign content
    objectService.periodically_fetch();

    // get gallery content
    const gallery_url = "/campaign/" + campaign_id + "/gallery/json";
    return galleryService.get(gallery_url)
    .then(function(data) {
      $scope.gallery = data;
    })
  }
}
