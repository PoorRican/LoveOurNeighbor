angular.module('LON').controller('ministryCtrl', ministryCtrl);
ministryCtrl.$inject = ['$scope', '$timeout', 'objectService', 'likeButtonService', 'galleryService'];

function ministryCtrl($scope, $timeout, objectService, likeButtonService, galleryService) {
  $scope.object = objectService.get;
  $scope.likeButton = likeButtonService;
  $scope.gallery = [];

  // activate dynamic content
  // activate();

  function activate() {
    const ministry_id = document.getElementById('ministry_id').value;
    // get ministry content
    objectService.periodically_fetch();

    // get gallery content
    const gallery_url = "/ministry/" + ministry_id + "/gallery/json";
    return galleryService.get(gallery_url)
    .then(function(data) {
      $scope.gallery = data;
    })
  }
}

