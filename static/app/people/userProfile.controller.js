{
  angular.module('LON').controller('userProfileCtrl', userProfileCtrl);
  userProfileCtrl.$inject = ['$scope', 'transactionTableService', 'selectImageDialogService'];

  function userProfileCtrl($scope, transactionTableService, selectImageService) {
    $scope.donations = {};
    $scope.donationTableService = transactionTableService;

    $scope.profile_img_urls = {};
    $scope.select_profile_img = select_profile_img;
    $scope.profile_img_dialog = selectImageService;
    $scope.selected_profile_img = $scope.profile_img_dialog.selected;

    activate();

    function select_profile_img(name) {
      // this is a dirty hack, but it works.....
      // for some reason, the selected attribute is never updated via $watch/$digest
      $scope.profile_img_dialog.select(name);
      $scope.selected_profile_img = name;
    }

    function activate() {

      const profile_img_url = "/people/profile_img/json";
      $scope.profile_img_dialog.get(profile_img_url)
      .then(function (data) {
        $scope.profile_img_urls = data;
      });

      const donation_url = '/people/donations/json';
      return $scope.donationTableService.fetch(donation_url).then(function (data) {
        $scope.donations = data;
        return $scope.donations;
      });
    }
  }
}
