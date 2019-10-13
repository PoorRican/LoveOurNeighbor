angular.module('LON').config(function($mdThemingProvider) {
  $mdThemingProvider.theme('default')
  .primaryPalette('orange')
  .accentPalette('purple')
});

angular.module('LON').config(['$httpProvider', function($httpProvider) {
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
  $httpProvider.defaults.headers.common['X-CSRFToken'] = '{{ csrf_token }}';
}]);
