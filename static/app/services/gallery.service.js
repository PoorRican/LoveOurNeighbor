angular.module('LON').factory('galleryService', galleryService);
galleryService.$inject = ['$http', '$log'];

function galleryService($http, $log) {
  var gallery = [];

  var G = this;

  return {
    'gallery': gallery,
    'get': get
  };


  function get(url) {
    return $http.get(url).then(success, failure);

    function success(response) {
      G.gallery = response.data.gallery;
      return response.data.gallery;
    }

    function failure(response) {
      $log.error('Could not fetch images. (Wrong URL?)');
    }
  }
}
