/**
 * Controls search result filtering.
 *
 * By passing the number of each type of object, checkboxes can be disabled if there are no types to show.
 * Also, the number of items can be shown to the user.
 *
 * @param {number} ministries   Number of MinistryProfiles in results
 * @param {number} campaigns    Number of Campaign objects in results
 * @param {number} posts        Number of Post objects in results
 */
function SearchFilterModel(ministries = 0, campaigns = 0, posts = 0) {
  let self = this;
  // number of items for UI feedback
  self.n_ministries = ko.observable(ministries);
  self.n_campaigns = ko.observable(campaigns);
  self.n_posts = ko.observable(posts);

  // values for checkboxes
  self.ministries = ko.observable(Boolean(ministries));
  self.campaigns = ko.observable(Boolean(campaigns));
  self.posts = ko.observable(Boolean(posts));

  self.relay = function () {
    $grid.masonry('destroy');
    setTimeout(function () {
      $grid.imagesLoaded().progress(function () {
        $grid.masonry();
      });
      console.debug('grid redrawn');
    }, 15);
    return true;
  }
}