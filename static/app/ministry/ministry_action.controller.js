{
  angular.module('LON').controller('ministryActionCtrl', ministryActionCtrl);
  ministryActionCtrl.$inject = ['$scope', 'tagService', 'userFilterService', 'objectService', 'selectImageDialogService'];

  function ministryActionCtrl($scope, tagService, userFilterService, objectService, selectImageService) {
    const ministry_id = document.getElementById('ministry_id');

    // creating a new ministry
    if (ministry_id === null) {
      $scope.object = {'tags': []};     // work around
      $scope.filter_tags = tagService.search;
      $scope.tag_service = tagService;
      tagService.fetch();
    }
    // editing ministry
    else {
      $scope.object = {};

      $scope.filter_users = userFilterService.search;
      $scope.filter_tags = tagService.search;

      $scope.tagService = tagService;

      $scope.banner_urls = {};
      $scope.select_banner = select_banner;
      $scope.banner_img_dialog = selectImageService;
      $scope.selected_banner = $scope.banner_img_dialog.selected;

      $scope.profile_img_urls = {};
      $scope.select_profile_img = select_profile_img;
      $scope.profile_img_dialog = selectImageService;
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
        const banners_url = "/ministry/" + ministry_id.value + "/banners/json";
        $scope.banner_img_dialog.get(banners_url)
        .then(function (data) {
          $scope.banner_urls = data;

        });

        const profile_img_url = "/ministry/" + ministry_id.value + "/profile_img/json";
        $scope.profile_img_dialog.get(profile_img_url)
        .then(function (data) {
          $scope.profile_img_urls = data;

        });

        return objectService.fetch()
        .then(function (data) {
            $scope.object = data;
          }
        );
      }
    }
  }
}
