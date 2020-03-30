angular.module('LON').controller('newsCtrl', newsCtrl);
newsCtrl.$inject = ['$scope', '$routeParams'];

function newsCtrl($scope, $routeParams) {
  // TODO: change title block

  $scope.currentNavItem = 'Home';

  $scope.news_editor = document.getElementById('initial_tinymce_value').value;

  // share button
  $scope.share.reset();
  $scope.share.set('title', 'Check out what God has done through this ministry!');
  $scope.share.set('url', 'https://loveourneighbor.org/ministry/' + $routeParams.post_id);
  $scope.share.update_dom();

  ga('send', 'pageview', '/campaigns/post/' + $routeParams.post_id);
}
