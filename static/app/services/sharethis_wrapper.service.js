/* Wrapper to set HTML DOM property attributes for the sharethis.js service */
angular.module('LON').factory('shareThisWrapper', shareThisWrapper);
shareThisWrapper.$inject = ['$timeout'];

function shareThisWrapper($timeout) {
  var disabled = false;
  var properties = {
    'title': 'Upload your non-profit ministry onto Love Our Neighbor!',
    'url': 'https://loveourneighbor.org',
    'image': '',
    'description': 'Check out this awesome ministry!'
  };

  return {
    disabled: disabled,
    properties: properties,
    reset: reset,
    set: set,
    update_dom: update_dom
  };

  function reset() {
    disabled = false;
    properties = {
      'title': 'Upload your non-profit ministry onto Love Our Neighbor!',
      'url': 'https://loveourneighbor.org',
      'image': '',
      'description': 'Check out this awesome ministry!'
    };
    update_dom();
  }

  function set(key, value) {
    // check validate passed arguments
    if (['title', 'url', 'image', 'description'].includes(key) && value.substring) {
      properties[key] = value;
      return true;
    } else {
      return false;
    }
  }

  function update_dom() {

    $timeout(manipulate_dom, 250);

    function manipulate_dom() {
      var element = document.getElementsByClassName('share-button')[0];

      if (element) {
        element.setAttribute('data-title', properties.title);
        element.setAttribute('data-url', properties.url);
        element.setAttribute('data-image', properties.image);
        element.setAttribute('data-description', properties.description);
      }
    }
  }
}
