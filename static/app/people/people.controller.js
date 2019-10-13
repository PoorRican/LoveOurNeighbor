angular.module('LON').controller('peopleCtrl', peopleCtrl);
peopleCtrl.$inject = ['$scope', '$route', '$routeParams', '$location'];

function peopleCtrl($scope, $route, $routeParams, $location) {
  // TODO: change title block

  $scope.currentNavItem  = null;
  $scope.share.disabled = true;

  if ($routeParams.people_action === 'create') {
    $scope.cleanPasswordPattern = cleanPasswordPattern;

    function cleanPasswordPattern() {
      var cleaned = $scope.password;
      if (cleaned) {
        var chars = [
          [/\\/g, '\\\\'],
          [/\*/g, '\\*'],
          [/\^/g, '\\^'],
          [/\$/g, '\\$'],
          [/\+/g, '\\+'],
          [/\?/g, '\\?'],
          [/\./g, '\\.'],
          [/\(/g, '\\('],
          [/\)/g, '\\)'],
          [/\|/g, '\\|'],
          [/{/g, '\\{'],
          [/}/g, '\\}']
        ];
        for (var i = 0; i < chars.length; i++) {
          cleaned = cleaned.replace(chars[i][0], chars[i][1]);
        }
        return cleaned;
      }
    }
  }
  if ($routeParams.people_action === 'login') {
  }
  if ($routeParams.people_action === 'alias/logout') {
    $location.url('/accounts/profile');
    location.reload();
  }
  ga('send', 'pageview', '/people/' + $routeParams.people_action);
}
