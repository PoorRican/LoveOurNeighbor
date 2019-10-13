angular.module('LON').factory('notificationService', notificationService);
notificationService.$inject = ['$mdToast', '$http', '$log', '$interval', '$timeout'];

function notificationService($mdToast, $http, $log, $interval, $timeout) {
  var messages = [];

  return {
    get: get,
    show: show,
    update: update
  };

  function get() {
    var url = 'people/messages/json';
    $http.get(url).then(success, failure);

    function success(response) {
      messages = response.data;
      // TODO: append to current messages
    }

    function failure(response) {
      $log.error('Could not fetch messages. (Wrong URL?)');
    }
  }

  function show() {
    if (messages.length) {
      var notificationArea = 'top right';
      var msg = messages[0].message;
      var msg_type = messages[0].type;
      var msg_style = '';
      if (msg_type === 'error' || msg_type === 'warning') {
        msg_style = 'md-warn';
      } else if (msg_type === 'success') {
        msg_style = 'GREEN';
      } else if (msg_type === 'info') {
        msg_style = 'GREEN';
      }
      $mdToast.show(
        $mdToast.simple()
        .textContent(msg)
        .toastClass(msg_style)
        // TODO: iterate over multiple messages
        // TODO: style toast in some way
        .position(notificationArea)
        .hideDelay(10000)
        .parent('#notificationArea'))
      .then(function () {
        $log.log('Message toast dismissed.');
      }).catch(function () {
        $log.log('Message toast failed or was forced to close early by another toast.');
      });
    }
  }

  function update() {
    getAndNotify();

    $interval(getAndNotify, 5500);

    function getAndNotify() {
      get();
      $timeout(show, 200);
    }
  }
}
