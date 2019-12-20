angular.module('LON').service('selectImageDialogService', selectImageDialogService);
selectImageDialogService.$inject = ['$mdDialog', '$http', '$log'];

function selectImageDialogService($mdDialog, $http, $log) {
  // a custom controller might need to be implemented inside of `show`
  var selected = '';    // for some reason, this property is never mutable from $scope
  var images = {};
  var current = '';

  var bd = this;

  return {
    'banner_current': banner_current,
    'banner_selected': banner_selected,
    'close': close,
    'clear': clear,
    'current': current,
    'get': get,
    'show': show,
    'select': select,
    'selected': selected,
    'images': images
  };

  function banner_current(name) {
    // applies styles for current banner image
    return name === bd.current;
  }

  function banner_selected(name) {
    // applies styles for selected banner image
    return name === bd.selected;
  }

  function clear() {
    bd.selected = '';
  }

  function close() {
    $mdDialog.hide();
  }

  function get(url) {
    return $http.get(url).then(success, failure);

    function success(response) {
      bd.images = response.data.available;
      bd.current = response.data.current;
      return bd.images;
    }

    function failure(response) {
      $log.error('Could not fetch images from ' + url + '. (Wrong URL?)');
    }
  }

  function select(name) {
    bd.selected = name;
  }

  function show(ev, name) {
    $mdDialog.show({
      contentElement: '#' + name,
      targetEvent: ev,
      clickOutsideToClose: false,
      fullscreen: true
    })
  }
}
