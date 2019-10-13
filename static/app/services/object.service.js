angular.module('LON').factory('objectService', objectService);
objectService.$inject = ['$http', '$interval', '$log'];

function objectService($http, $interval, $log) {
  var interval_id = 0;
  var object = {};

  return {
    fetch: fetch,
    get: get,
    periodically_fetch: periodically_fetch,
    stop: stop
  };

  function fetch(url) {
    if (url === undefined || angular.isNumber(url)) {
      try {
        url = document.getElementById("current_object_json").value;
      } catch (e) {
        $log.warn("no value 'current_object_json' on page...");
        return null;
      }
    }
    return $http.get(url)
    .then(function (response) {
      var data = response.data;
      if (data.founded) {
        data.founded = new Date(data.founded);
      }
      if (data.start_date) {
        data.start_date = new Date(data.start_date);
      }
      if (data.end_date) {
        data.end_date = new Date(data.end_date);
      }
      object = data;
      return data;
    }, function (response) {
      $log.warn('Could not fetch object. (Wrong URL?)')
    });
  }

  function get() {
    return object;
  }

  function periodically_fetch() {
    fetch();
    interval_id = $interval(get, 15000);
  }

  function stop() {
    if (angular.isDefined(interval_id)) {
      $interval.cancel(interval_id);
      interval_id = undefined;
    }
  }
}
