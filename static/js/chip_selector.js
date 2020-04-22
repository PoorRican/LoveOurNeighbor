function ChipSelector(id, url, el, chips = [], placeholder='Enter a Tag', secondaryPlaceholder='+Tag') {
  let self = this;
  self.url = url;
  self.hidden_input = document.getElementById(id);
  self.chip_input = document.getElementById(el);
  self.selected_chips = [];

  // Methods

  /**
   * @brief Updates the contents of hidden input element
   *
   * The input value becomes a string of comma separated values.
   *
   * @see https://materializecss.com/chips.html for more info on the Tags component.
   */
  self.updateChipData = function () {
    let chips = [];
    let _chip = {};    // buffer for iteration to unpack `tag`

    // extract data
    for (_chip of self.chip_input.M_Chips.chipsData) {
      chips.push(_chip.tag);
    }

    self.hidden_input.value = chips.join(', ');
  };

  /**
   * @brief Initializes tag input component
   *
   * @see https://materializecss.com/chips.html for more info on the Chips component
   *
   * @param chips JSON array of current object chips. Array of String or Array of Objects containing `name` and `image`.
   */
  self.initChipInput = async function (chips) {
    let chip = {};   // buffer for iteration

    // TODO: this seems to be one big heuristic... sorry...

    // Get all available chips and format for autocomplete
    const response = await fetch(self.url);
    const all_chips = await response.json();
    const autocompleteOptions = {data: {}};
    for (chip of all_chips) {
      // when `tag` has an image and `all_chips` is an Array of Arrays
      if (chip.hasOwnProperty('profile_img')) {
        autocompleteOptions.data[chip.name] = chip.profile_img;
      }
      // when `all_chips` is an Array of String
      else {
        autocompleteOptions.data[chip] = null;
      }
    }

    // Format existing chips
    for (chip of chips) {
      if (chip.hasOwnProperty('profile_img')) {
        self.selected_chips.push({'tag': chip.name, 'image': chip.profile_img});
      }
      else {
        self.selected_chips.push({'tag': chip.name});
      }
    }

    const options = {
      data: self.selected_chips,
      autocompleteOptions: autocompleteOptions,
      placeholder: placeholder,
      secondaryPlaceholder: secondaryPlaceholder,
      onChipAdd: self.updateChipData,
      onChipDelete: self.updateChipData
    };
    M.Chips.init(self.chip_input, options);
  };

  self.initChipInput(chips).then(self.updateChipData);
}
