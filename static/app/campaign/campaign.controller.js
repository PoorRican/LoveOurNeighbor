angular.module('LON').controller('campaignCtrl', campaignCtrl);
campaignCtrl.$inject = ['$scope', '$timeout', 'objectService', 'likeButtonService', 'galleryService'];

function campaignCtrl($scope, $timeout, objectService, likeButtonService, galleryService) {
  $scope.object = objectService.get;
  $scope.likeButton = likeButtonService;

  $scope.gallery = [];

  // activate dynamic content
  activate();

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
