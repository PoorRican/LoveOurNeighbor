nav_layout.factory('objectService', objectService);

objectService.$inject = ['$http', '$interval', '$log'];

function objectService($http, $interval, $log) {
  var interval_id = 0;
  var object = {};

  var service = {
    fetch: fetch,
    get: get,
    periodically_fetch: periodically_fetch,
    stop: stop,
  }
  return service;

  function fetch(url=null) {
    if (url == null | angular.isNumber(url)) {
      try {
        url = document.getElementById("current_object_json").value;
      }
      catch(e) {
        $log.warn("no value 'current_object_json' on page...");
        return null;
      }
    };
    $http.get(url)
    .then(function(response) {
      var data = response.data;
      if (data.founded) {
        data.founded = new Date(data.founded);
      };
      if (data.start_date) {
        data.start_date = new Date(data.start_date);
      };
      if (data.end_date) {
        data.end_date = new Date(data.end_date);
      };

      object = data;
    }, function(response) {
      $log.warn('Could not fetch tag list. (Wrong URL?)')});
  };

  function get() {
    return object;
  };

  function periodically_fetch() {
    fetch();
    interval_id = $interval(get, 15000);
  };

  function stop() {
    if (angular.isDefined(interval_id)) {
      $interval.cancel(interval_id);
     interval_id  = undefined;
    };
  };
};


nav_layout.factory('likeButtonService', likeButtonService);

likeButtonService.$inject = ['$http', '$log', 'objectService'];

function likeButtonService($http, $log, objectService) {
  var service = {
    like: like,
    style: style
  };
  return service

  function like(url) {
    $http.get(url)
    .then(function(response) {
      // don't assume that the object has changed on server side. i think this is proper use of REST
      objectService.fetch();
    }, function(response) {
      $log.error("Unable to like object. Maybe incorrect URL?");
    });
  };

  function style() {
    if (objectService.get().liked) {
      return {'background-color': '#FF7100'};
    } else {
      return {'background-color': '#EEE'};
    }
  };
};


nav_layout.factory('searchBarService', searchBarService);
searchBarService.$inject = ['$location'];
function searchBarService($location) {
  var service = {
    search: search,
  }
  return service;

  function search(q=null) {
    var url = "/search/" + q;
    if (q != '') {
      $location.url(url);
    };
  };

};


nav_layout.factory('searchFilteringService', searchFilteringService);

searchFilteringService.$inject = ['objectService'];

function searchFilteringService(objectService) {
  var filter_types = {};

  var service = {
    blank: blank,
    populate: populate
  };
  return service;

  function blank() {
    return {
        'ministry': false,
        'campaign': false,
        'post': false,
        'distance': 0,
    }
  }

  function populate() {

    var object = objectService.get();

    if (object.ministries && object.ministries.length) {
      filter_types['ministry'] = true;
    };
    if (object.campaigns && object.campaigns.length) {
      filter_types['campaign'] = true;
    };
    if (object.posts && object.posts.length) {
      filter_types['post'] = true;
    };
    if (object.distances && object.distances.max) {
      filter_types['distance'] = object.distances.max;
    };

    return filter_types;
  };
};


nav_layout.factory('tagService', tagService);

tagService.$inject = ['$http', '$log'];

function tagService($http, $log) {
  var available_tags = {};

  var service = {
    fetch: fetch,
    search: search,
    transform_chip: transform_chip
  }
  return service;

  function fetch() {
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
  };
};


nav_layout.factory('userFilterService', userFilterService);


userFilterService.$inject = ['objectService'];

function userFilterService(objectService) {

  var service = {
    search: search
  }
  return service;

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
    };

    return query ? objectService.get().requests.filter(createContactFilter(query)) : [];
  };
};


// vim:foldmethod=syntax shiftwidth=2 tabstop=2:
