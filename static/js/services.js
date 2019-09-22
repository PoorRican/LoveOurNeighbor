// Comment Service
nav_layout.factory('commentService', commentService);

function commentService() {
  return {
    hide: hide,
    show: show
  };

  /** Controls the display of new comment forms on the page.
   *
   *  All elements of 'new_comment' are styled (forms hidden, buttons shown).
   *  Then the targeted comment form is shown and the button is hidden.
   *  This ensures that only a single form is shown at a time.
   *
   *  TODO: comment form should be dynamically created instead of hardcoded
   **/
  function show(event) {
    // reset all 'new_comment' divs to default styling
    reset();

    // style selected form and button respectively
    if ($(event.target).parent().parent()[0].classList.value.includes("wrapper")) {
      // clicked button and not inner text. therefore, dont unpack as many parent elements
      $(event.target).parent().children().css('display', 'block');
      $(event.target).css('display', 'none');
    } else {
      $(event.target).parent().parent().children().css('display', 'block');
      $(event.target).parent().css('display', 'none');
    }
  }

  function hide(event) {
    // hide selected form and button respectively
    if ($(event.target).parent().parent().parent()[0].classList.value.includes("wrapper")) {
      // clicked button and not inner text. therefore, dont unpack as many parent elements
      $(event.target).parent().parent().children().css('display', 'block');
      $(event.target).parent().css('display', 'none');
    } else {
      $(event.target).parent().parent().parent().children().css('display', 'block');
      $(event.target).parent().parent().css('display', 'none');
    }
  }

  function reset() {
    var new_comment_divs = document.getElementsByClassName('new_comment');
    for (d = 0; d < new_comment_divs.length; d++) {
      new_comment_divs[d].children[0].style.display = 'none';
      new_comment_divs[d].children[1].style.display = 'block';
    }
  }
}


// Object Service
nav_layout.factory('objectService', objectService);
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

  function fetch(url=null) {
    if (url == null || angular.isNumber(url)) {
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


// Like Button Service
nav_layout.factory('likeButtonService', likeButtonService);
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


// Search Bar Service
nav_layout.factory('searchBarService', searchBarService);
searchBarService.$inject = ['$location', 'sideNavService'];

function searchBarService($location, sideNavService) {
  return {
    search: search
  };

  function search(q) {
    var url = "/search/" + q;
    if (q !== '') {
      $location.url(url);
      sideNavService.close();
    } else {
      sideNavService.close();
    }
  }
}


// Search Filtering Service
nav_layout.factory('searchFilteringService', searchFilteringService);
searchFilteringService.$inject = ['objectService'];

function searchFilteringService(objectService) {
  var filter_types = {};

  return {
    blank: blank,
    populate: populate
  };

  function blank() {
    return {
      'ministry': false,
      'campaign': false,
      'post': false,
      'distance': 0
    }
  }

  function populate() {

    var object = objectService.get();

    if (object.ministries && object.ministries.length) {
      filter_types['ministry'] = true;
    }
    if (object.campaigns && object.campaigns.length) {
      filter_types['campaign'] = true;
    }
    if (object.posts && object.posts.length) {
      filter_types['post'] = true;
    }
    if (object.distances && object.distances.max) {
      filter_types['distance'] = object.distances.max;
    }
    return filter_types;
  }
}


// Sidenav Service
nav_layout.factory('sideNavService', sideNavService);
sideNavService.$inject = ['$interval', '$log', '$mdSidenav'];

function sideNavService($interval, $log, $mdSidenav) {

  return {
    close: close,
    toggleRight: buildToggler('right')
  };

  function buildToggler(navID) {
    return function () {
      // Component lookup should always be available since we are not using `ng-if`
      $mdSidenav(navID)
      .toggle()
      .then(function () {
        $log.debug("toggle " + navID + " is done");
      });
    }
  }

  function close() {
    // Component lookup should always be available since we are not using `ng-if`
    $mdSidenav('right').close()
    .then(function () {
      $log.debug("close RIGHT is done");
    });
  }
}


// Tag Service
nav_layout.factory('tagService', tagService);
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


// User Filter Service
nav_layout.factory('userFilterService', userFilterService);
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


// Notification Service
nav_layout.factory('notificationService', notificationService);
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


// Banner Image Service
nav_layout.service('bannerImageService', bannerImageService);
bannerImageService.$inject = ['$mdDialog', '$http', '$log'];

function bannerImageService($mdDialog, $http, $log) {
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
      $log.error('Could not fetch images. (Wrong URL?)');
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


// Gallery Image Service
nav_layout.factory('galleryService', galleryService);
galleryService.$inject = ['$http', '$log'];

function galleryService($http, $log) {
  var gallery = [];

  var G = this;

  return {
    'gallery': gallery,
    'get': get
  };


  function get(url) {
    return $http.get(url).then(success, failure);

    function success(response) {
      G.gallery = response.data.gallery;
      return response.data.gallery;
    }

    function failure(response) {
      $log.error('Could not fetch images. (Wrong URL?)');
    }
  }
}


// sharethis.js Wrapper Service
/* Wrapper to set HTML DOM property attributes for the sharethis.js service */
nav_layout.factory('shareThisWrapper', shareThisWrapper);
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

      element.setAttribute('data-title', properties.title);
      element.setAttribute('data-url', properties.url);
      element.setAttribute('data-image', properties.image);
      element.setAttribute('data-description', properties.description);
    }
  }
}

// vim:foldmethod=syntax shiftwidth=2 tabstop=2:
