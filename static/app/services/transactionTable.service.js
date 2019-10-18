angular.module('LON').factory('transactionTableService', transactionTableService);
transactionTableService.$inject = ['$http', '$log'];

function transactionTableService($http, $log){
  var transactions = {};
  var orderBy = 'name';

  return {
    fetch: fetch,
    orderBy: orderBy
  };

  function fetch(url) {
    return $http.get(url).then(success, failure);

    function success(response){
      transactions = response.data;
      return response.data;
    }

    function failure(response){
      $log.warn('Could not fetch transactions. (Wrong URL?)');
    }
  }
}
