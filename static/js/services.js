nav_layout.factory('tagService', ['$http', '$log', function($http, $log) {
  var available_tags = {};

  service = {
    get: get,
    search: search
  }
  return service;

  function get() {
    var url = '/ministry/tags/all';
    $http.get(url)
    .then(function(response) {
      available_tags = response.data;
    }, function(response) {
      $log.warn('Could not fetch tag list. (Wrong URL?)')});
  };

  function search(query) {
    function createTagFilter(query) {
      var loweredQuery = query.toLowerCase();

      return function filterFn(tag) {
        return (tag.indexOf(loweredQuery) === 0);
      };
    };

    return query ? available_tags.filter(createTagFilter(query)) : [];
  };
}]);
