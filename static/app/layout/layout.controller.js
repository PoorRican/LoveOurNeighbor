angular.module('LON').controller('LayoutCtrl', LayoutCtrl);

LayoutCtrl.$inject = ['$scope', '$location', 'searchBarService', 'commentService', 'sideNavService', 'notificationService', 'shareThisWrapper'];

function LayoutCtrl($scope, $location, searchBarService, commentService, sideNavService, notificationService, shareThisWrapper) {

  $scope.sidenav = sideNavService;

  $scope.search = searchBarService.search;
  $scope.comment = commentService;
  $scope.share = shareThisWrapper;

  $scope.goto = function (url) {
    $location.url(url);
  };

  notificationService.update();

  $scope.tinymceOptions = {
    height: 500,
    max_height: 750,
    min_width: 300,
    width: 650,
    resize: true,
    mobile: {
      theme: 'mobile',
//          toolbar: [ 'undo', 'bold', 'italic', 'styleselect' ]
    }
  }

}
