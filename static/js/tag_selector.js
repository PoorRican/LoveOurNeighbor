function TagSelector(id, url, tags = [], el = 'tagSelector') {
  let self = this;
  self.url = url;
  self.hidden_input = document.getElementById(id);
  self.tag_input = document.getElementById(el);
  self.selected_tags = [];
  self.available_tags = [];

  // Methods

  /**
   * @brief Updates the contents of hidden input element
   *
   * The input value becomes a string of comma separated values.
   *
   * @see https://materializecss.com/chips.html for more info on the Tags component.
   */
  self.updateTagData = function () {
    let tags = [];
    let _tag = {};    // buffer for iteration to unpack `tag`

    // extract data
    for (_tag of self.tag_input.M_Chips.chipsData) {
      tags.push(_tag.tag);
    }

    self.hidden_input.value = tags.join(', ');
  };

  /**
   * @brief Initializes tag input component
   *
   * @see https://materializecss.com/chips.html for more info on the Tags component
   *
   * @param tags JSON array of existing tags
   */
  self.initTagInput = async function (tags) {
    let tag = {};   // buffer for iteration

    // Get all available tags and format for autocomplete
    const response = await fetch(self.url);
    const all_tags = await response.json();
    const autocompleteOptions = {data: {}};
    for (tag of all_tags) {
      autocompleteOptions.data[tag] = null;
    }
    console.log(autocompleteOptions);

    // Format existing tags
    for (tag of tags) {
      self.selected_tags.push({'tag': tag});
    }

    const options = {
      data: self.selected_tags,
      autocompleteOptions: autocompleteOptions,
      placeholder: 'Enter a Tag',
      secondaryPlaceholder: '+Tag',
      onChipAdd: self.updateTagData,
      onChipDelete: self.updateTagData
    };
    M.Chips.init(self.tag_input, options);
  };

  self.initTagInput(tags).then(self.updateTagData);
}
