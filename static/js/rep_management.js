function PersonChip(name, email, img) {
  let self = this;
  self.name = name;
  self.email = email;
  self.img = img;
}

function RepManager(reps, reqs) {
  let self = this;

  self.reps = ko.observableArray([]);
  self.reqs = ko.observableArray([]);

  self.reps_value = ko.pureComputed(function () {
    let reps = [];
    let chip;

    for (chip of self.reps()) {
      reps.push(chip.email);
    }
    return reps.join(', ');
  });
  self.requests_value = ko.pureComputed(function () {
    let reqs = [];
    let chip;

    for (chip of self.reqs()) {
      reqs.push(chip.email);
    }
    return reqs.join(', ');
  });

  // Methods
  self.process_arrays = function (reps, reqs) {
    let val;
    for (val of reps) {
      self.reps.push(new PersonChip(val.name, val.email, val.img));
    }
    for (val of reqs) {
      self.reqs.push(new PersonChip(val.name, val.email, val.img));
    }
  };

  self.add_rep = function (chip) {
    self.reps.push(chip);
    self.reqs.remove(chip);
    console.debug('promoted rep');
  };

  self.del_rep = function (chip) {
    self.reqs.push(chip);
    self.reps.remove(chip);
    console.debug('demoted rep');
  };

  self.del_req = function (chip) {
    self.reqs.remove(chip);
    console.debug('deleted request');
  };

  self.process_arrays(reps, reqs);
}
