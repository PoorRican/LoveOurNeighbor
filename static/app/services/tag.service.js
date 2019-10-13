angular.module('LON').factory('tagService', tagService);
tagService.$inject = ['$http', '$log', '$mdConstant'];

function tagService($http, $log, $mdConstant) {
  var separatorKeys = [$mdConstant.KEY_CODE.ENTER, $mdConstant.KEY_CODE.COMMA];
  var available_tags = [];

  return {
    fetch: fetch,
    search: search,
    separatorKeys: separatorKeys,
    transform_chip: transform_chip
  };

  function fetch() {
    var url = '/ministry/tags/all';
    return $http.get(url).then(success, failure);

    function success(response) {
      available_tags = response.data;
    }
    function failure(response) {
      $log.warn('Could not fetch tag list. (Wrong URL?)')
    }
  }

  function search(query) {
    function createTagFilter(query) {
      var loweredQuery = query.toLowerCase();

      return function filterFn(tag) {
        return (tag.indexOf(loweredQuery) === 0);
      };
    }

    return query ? available_tags.filter(createTagFilter(query)) : [];
  }

  /**
   * Return the proper object when the append is called.
   */
  function transform_chip(chip) {
    // If it is an object, it's already a known chip
    if (angular.isObject(chip)) {
      return chip;
    }

    // Otherwise, create a new one
    return chip;
  }
}
