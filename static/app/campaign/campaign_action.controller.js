angular.module('LON').controller('campaignActionCtrl', campaignActionCtrl);
campaignActionCtrl.$inject = ['$scope', 'tagService', 'objectService', 'selectImageDialogService', 'confirmDeleteDialogService'];

function campaignActionCtrl($scope, tagService, objectService, selectImageService, confirmDeleteDialogService) {
  const campaign_id = document.getElementById('campaign_id');

  $scope.banner_urls = {};
  $scope.select_banner = select_banner;
  $scope.banner_img_dialog = selectImageService;
  $scope.selected_banner = $scope.banner_img_dialog.selected;

  $scope.filter_tags = tagService.search;

  $scope.tag_service = tagService;

  // creating a new campaign
  if (campaign_id === null) {
    $scope.object = {'tags': []};     // work around
    $scope.filter_tags = tagService.search;
    tagService.fetch();
  }
  // edit campaign
  else {
    $scope.object = objectService.get;

    $scope.confirmDelete = confirmDeleteDialogService;

    activate();

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
      if (!(campaign_id === null)) {
        const banners_url = "/campaign/" + campaign_id.value + "/banners/json";
        selectImageService.get(banners_url)
        .then(function (data) {
          $scope.banner_urls = data;

        });
      }   // TODO: grab ministry banners when creating new campaign

      tagService.fetch();

      return objectService.fetch()
      .then(function(data) {
          $scope.object = data;
        }
      );
    }
  }
}
