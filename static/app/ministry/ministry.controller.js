angular.module('LON').controller('ministryCtrl', ministryCtrl);
ministryCtrl.$inject = ['$scope', '$routeParams', '$timeout', 'objectService', 'likeButtonService', 'galleryService'];

function ministryCtrl($scope, $routeParams, $timeout, objectService, likeButtonService, galleryService) {
  // TODO: change title block
  $scope.object = objectService.get;
  $scope.likeButton = likeButtonService;

  $scope.currentNavItem = null;
  $scope.gallery = [];

  // activate dynamic content
  activate();
  share_button();

  $scope.$on('$destroy', function() {
    // stop periodic updating
    objectService.stop();
  });

  function activate() {
    // get ministry content
    objectService.periodically_fetch();

    // get gallery content
    var gallery_url = "/t/ministry/" + $routeParams.ministry_id + "/gallery/json";
    return galleryService.get(gallery_url)
    .then(function(data) {
      $scope.gallery = data;
    })
  }

  function share_button() {
    // hack to update share button with attributes from objectService because promises don't seem to be working
    $scope.share.reset();

    $timeout(update_dom, 250);

    function update_dom() {
      $scope.share.set('title', 'Check out the ministry profile for "' + $scope.object().name + '" on Love Our Neighbor!');
      $scope.share.set('url', 'https://loveourneighbor.org' + $scope.object().url.substr(2));
      $scope.share.update_dom();
    }
  }

  ga('send', 'pageview', '/ministry/' + $routeParams.ministry_id);
}

