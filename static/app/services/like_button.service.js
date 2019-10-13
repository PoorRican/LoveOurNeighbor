angular.module('LON').factory('likeButtonService', likeButtonService);
likeButtonService.$inject = ['$http', '$log', 'objectService'];

function likeButtonService($http, $log, objectService) {
  return {
    like: like,
    style: style
  };

  function like(url) {
    $http.get(url)
    .then(function (response) {
      // don't assume that the object has changed on server side. i think this is proper use of REST
      objectService.fetch();
    }, function (response) {
      $log.error("Unable to like object. Maybe incorrect URL?");
    });
  }

  function style() {
    if (objectService.get().liked) {
      return {'background-color': '#FF7100'};
    } else {
      return {'background-color': '#EEE'};
    }
  }
}
