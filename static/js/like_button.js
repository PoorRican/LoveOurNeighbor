function likeButtonViewModel(url) {

  // Data
  let self = this;
  self.liked = ko.observable();
  self.likes = ko.observable(0);
  self.btnStyle = ko.computed(function () {
    return self.liked() ? 'red-text lighten-3 btn-flat' : 'lighten-2 btn-raised grey-text text-darken-3';
  });
  self.url = url;


  // Methods

  // This encapsulates both the like and unlike functionality
  self.like = function () {
    $.getJSON(self.url, function (data) {
      self.liked(data.liked);
      console.log(data);
    });
  };
}