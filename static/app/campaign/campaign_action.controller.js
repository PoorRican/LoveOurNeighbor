angular.module('LON').controller('campaignActionCtrl', campaignActionCtrl);
campaignActionCtrl.$inject = ['$scope', '$routeParams', 'tagService', 'objectService', 'selectImageDialogService', 'confirmDeleteDialogService'];

function campaignActionCtrl($scope, $routeParams, tagService, objectService, bannerImageService, confirmDeleteDialogService) {
  // TODO: change title block

  $scope.currentNavItem = 'Home';
  $scope.share.disabled = true;

  if ($routeParams.campaign_action === 'create') {
    $scope.object = {'tags': []};     // work around
    $scope.filter_tags = tagService.search;
    $scope.tag_service = tagService;
    tagService.fetch();
  }
  if ($routeParams.campaign_action === 'edit') {
    $scope.object = objectService.get;
    $scope.filter_tags = tagService.search;
    $scope.tag_service = tagService;

    $scope.banner_urls = {};
    $scope.select_banner = select_banner;
    $scope.banner_img_dialog = bannerImageService;
    $scope.selected_banner = $scope.banner_img_dialog.selected;

    $scope.profile_img_urls = {};
    $scope.select_profile_img = select_profile_img;
    $scope.profile_img_dialog = bannerImageService;
    $scope.selected_profile_img = $scope.profile_img_dialog.selected;

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
      if ($routeParams.campaign_id) {
        var banners_url = "/t/ministry/campaign/" + $routeParams.campaign_id + "/banners/json";
        bannerImageService.get(banners_url)
        .then(function (data) {
          $scope.banner_urls = data;

        });

        var profile_img_url = "/t/ministry/campaign/" + $routeParams.campaign_id + "/profile_img/json";
        bannerImageService.get(profile_img_url)
        .then(function (data) {
          $scope.profile_img_urls = data;

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

  ga('send', 'pageview', '/campaigns/' + $routeParams.campaign_id);
}
