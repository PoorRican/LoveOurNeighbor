function PreviousImage(name, src) {
  let self = this;
  self.name = name;
  self.src = src;

  self.klass = ko.observable('');

  // Methods
  self.style = ko.pureComputed(function () {
    if (self.klass() !== '') {
      return 'prev_img-' + self.klass();
    } else {
      return '';
    }
  });
  self.selected = ko.pureComputed(function () {
    return self.klass() === 'selected'
  });
  self.current = ko.pureComputed(function () {
    return self.klass() === 'current'
  });
}

function PreviousImageSelection(name, url) {
  let self = this;
  self.name = name;                   // name of the hidden input
  self.url = url;
  self.current = '';                  // name of the current `PreviousImage`
  self.selected = ko.observable();    // name of the selected `PreviousImage`
  self.available = ko.observableArray([]);

  self.show = ko.pureComputed(function () {
    return self.available().length >= 1;
  });

  // Methods
  self.get_available = function () {
    $.getJSON(self.url, function (data) {
      self.current = data.current;
      for (let i = 0; i < data.available.length; i++) {
        let img = data.available[i];
        self.available.push(new PreviousImage(img.name, img.src));
      }
      self.reset();
    });
  };

  self.reset = function () {
    for (let i = 0; i < self.available().length; i++) {
      self.available()[i].klass('');
      if (self.available()[i].name === self.selected()) {
        self.available()[i].klass('selected');
        console.log('found selected');
      }
      if (self.available()[i].name === self.current) {
        self.available()[i].klass('current');
        console.log('found current');
      }
    }
  };

  self.choose_image = function (image) {
    self.selected(image.name);
    self.reset();
  };

  self.open = function () {
    let $grid = $('.grid').masonry({
      itemSelector: '.grid-item',
      percentPosition: true
    });
    $grid.imagesLoaded().progress(function () {
      $grid.masonry('layout');
    });
  };

  // automatically fetch JSON
  if (self.url !== null) {
    self.get_available();
  }
}