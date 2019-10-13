angular.module('LON').factory('searchBarService', searchBarService);
searchBarService.$inject = ['$location', 'sideNavService'];

function searchBarService($location, sideNavService) {
  return {
    search: search
  };

  function search(q) {
    var url = "/search/" + q;
    if (q !== '') {
      $location.url(url);
      sideNavService.close();
    } else {
      sideNavService.close();
    }
  }
}
