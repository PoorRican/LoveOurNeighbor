nav_layout.filter('stripHTML', function() {
  return function(text) {
    return  text ? String(text).replace(/<[^>]+>/gm, '  ') : '  ';
  };
});

nav_layout.filter('withinDistance', function() {
  return function(items, distance) {
    if (items) {
      var results = [];
      var r = 0;
      for (var i = 0; i < items.length; i++) {
        if (items[i].distance < distance) {
          results[r++] = items[i];
        }
      }
      return results;
    }
  };
});

// vim:foldmethod=syntax shiftwidth=2 tabstop=2:
