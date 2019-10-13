angular.module('LON').controller('ministryActionCtrl', ministryActionCtrl);
ministryActionCtrl.$inject = ['$scope', '$location', '$routeParams', 'tagService', 'userFilterService', 'objectService', 'selectImageDialogService', 'confirmDeleteDialogService'];

function ministryActionCtrl($scope, $location, $routeParams, tagService, userFilterService, objectService, bannerImageService, confirmDeleteDialogService) {
  // TODO: change title block

  $scope.currentNavItem = null;
  $scope.share.disabled = true;

  if ($routeParams.ministry_action === 'edit' || $routeParams.ministry_action === 'create') {
    $scope.object = {};

    $scope.filter_users = userFilterService.search;
    $scope.filter_tags = tagService.search;

    $scope.tagService = tagService;

    $scope.banner_urls = {};
    $scope.select_banner = select_banner;
    $scope.banner_img_dialog = bannerImageService;
    $scope.selected_banner = $scope.banner_img_dialog.selected;

    $scope.profile_img_urls = {};
    $scope.select_profile_img = select_profile_img;
    $scope.profile_img_dialog = bannerImageService;
    $scope.selected_profile_img = $scope.profile_img_dialog.selected;

    $scope.confirmDelete = confirmDeleteDialogService;


    if ($routeParams.ministry_action === 'edit') {
      activate();
      tagService.fetch();
    }

    function select_banner(name) {
      // this is a dirty hack, but it works.....
      // for some reason, the selected attribute is never updated via $watch/$digest
      $scope.banner_img_dialog.select(name);
      $scope.selected_banner = name;
    }

    function select_profile_img(name) {
      // this is a dirty hack, but it works.....
      // for some reason, the selected attribute is never updated via $watch/$digest
      $scope.profile_img_dialog.select(name);
      $scope.selected_profile_img = name;
    }

    function activate() {
      var banners_url = "/t/ministry/" + $routeParams.ministry_id + "/banners/json";
      bannerImageService.get(banners_url)
      .then(function(data) {
        $scope.banner_urls = data;

      });

      var profile_img_url = "/t/ministry/" + $routeParams.ministry_id + "/profile_img/json";
      bannerImageService.get(profile_img_url)
      .then(function(data) {
        $scope.profile_img_urls = data;

      });

      return objectService.fetch()
      .then(function(data) {
          $scope.object = data;
        }
      );
    }
  }
  if ($routeParams.ministry_action === 'login') {
    $location.url('/ministry/' + $routeParams.ministry_id);
    location.reload();
  }

  ga('send', 'pageview', '/ministry/' + $routeParams.ministry_id + '/' + $routeParams.ministry_action);
}
