angular.module('LON').factory('searchFilteringService', searchFilteringService);
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

  function populate(object) {

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
