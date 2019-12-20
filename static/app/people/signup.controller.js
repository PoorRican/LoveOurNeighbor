angular.module('LON').controller('signUpCtrl', signUpCtrl);
signUpCtrl.$inject = ['$scope'];

function signUpCtrl($scope) {
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
