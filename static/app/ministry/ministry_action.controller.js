angular.module('LON').controller('ministryActionCtrl', ministryActionCtrl);
ministryActionCtrl.$inject = ['$scope', 'tagService', 'userFilterService', 'objectService', 'selectImageDialogService'];

function ministryActionCtrl($scope, tagService, userFilterService, objectService, bannerImageService) {
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

  activate();
  tagService.fetch();

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
      const ministry_id = document.getElementById("ministry_id").value;
      const banners_url = "/ministry/" + ministry_id + "/banners/json";
      bannerImageService.get(banners_url)
      .then(function(data) {
        $scope.banner_urls = data;

      });

      const profile_img_url = "/ministry/" + ministry_id + "/profile_img/json";
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
