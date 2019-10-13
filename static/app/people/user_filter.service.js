angular.module('LON').factory('userFilterService', userFilterService);
userFilterService.$inject = ['objectService'];

function userFilterService(objectService) {

  return {
    search: search
  };

  function search(query) {
    /**
     * Create filter function for a query string
     */
    function createContactFilter(query) {
      var lowercaseQuery = query.toLowerCase();

      return function filterFn(contact) {
        return (contact.name.toLowerCase().indexOf(lowercaseQuery) === 0) ||
          (contact.email.toLowerCase().indexOf(lowercaseQuery) === 0);
      };
    }

    return query ? objectService.get().requests.filter(createContactFilter(query)) : [];
  }
}
