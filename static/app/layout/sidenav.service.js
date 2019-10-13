angular.module('LON').factory('sideNavService', sideNavService);
sideNavService.$inject = ['$interval', '$log', '$mdSidenav'];

function sideNavService($interval, $log, $mdSidenav) {

  return {
    close: close,
    toggleRight: buildToggler('right')
  };

  function buildToggler(navID) {
    return function () {
      // Component lookup should always be available since we are not using `ng-if`
      $mdSidenav(navID)
      .toggle()
      .then(function () {
        $log.debug("toggle " + navID + " is done");
      });
    }
  }

  function close() {
    // Component lookup should always be available since we are not using `ng-if`
    $mdSidenav('right').close()
    .then(function () {
      $log.debug("close RIGHT is done");
    });
  }
}
