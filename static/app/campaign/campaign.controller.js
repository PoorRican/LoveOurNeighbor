angular.module('LON').controller('campaignCtrl', campaignCtrl);
campaignCtrl.$inject = ['$scope', '$routeParams', '$timeout', 'objectService', 'likeButtonService', 'galleryService'];

function campaignCtrl($scope, $routeParams, $timeout, objectService, likeButtonService, galleryService) {
  // TODO: change title block
  $scope.object = objectService.get;
  $scope.likeButton = likeButtonService;

  $scope.currentNavItem = 'Home';

  $scope.gallery = [];

  // activate dynamic content
  activate();
  share_button();

  // activate dynamic content
  $scope.$on('$destroy', function() {
    // Make sure the interval is no longer running
    objectService.stop();
  });

  function activate() {
    // get campaign content
    objectService.periodically_fetch();

    // get gallery content
    const gallery_url = "/t/campaign/" + $routeParams.campaign_id + "/gallery/json";
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
      $scope.share.set('title', 'Check out this fundraiser for ' + $scope.object().name + ' on Love Our Neighbor!');
      $scope.share.set('url', 'https://loveourneighbor.org' + $scope.object().url.substr(2));
      $scope.share.update_dom();
    }
  }
  ga('send', 'pageview', '/campaigns/' + $routeParams.campaign_id);
}
