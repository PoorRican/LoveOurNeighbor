angular.module('LON').factory('confirmDeleteDialogService', confirmDeleteDialogService);
confirmDeleteDialogService.$inject = ['$mdDialog'];

function confirmDeleteDialogService($mdDialog) {
  return {
    'close': close,
    'show': show
  };

  function close() {
    $mdDialog.hide();
  }

  function show(ev, name) {
    console.log('test');
    $mdDialog.show({
      contentElement: '#' + name,
      targetEvent: ev,
      clickOutsideToClose: false,
      fullscreen: true
    })
  }
}
