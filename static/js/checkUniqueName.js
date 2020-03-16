/**
 * Helper function for displaying if an input form is valid or not.
 *
 * While adding classes could easily be added using knockout.js functionality,
 *  the asynchronous `getJSON` function adds another layer of complexity.
 *
 * @param selector [in] CSS selector of element to manipulate
 * @param invalid [in] controls if input element is to be styled as invalid or valid
 * @param show_valid [in] controls whether input element is to be styled when valid
 * @returns {boolean} returns the value of `invalid`
 */
function markInvalid(selector, invalid = true, show_valid = false) {
  if (invalid) {
    $(selector).addClass('invalid');
  } else {
    $(selector).removeClass('invalid');
    if (show_valid) {
      $(selector).addClass('valid');
    }
  }
  return invalid;
}

/**
 * knockdown.js model-view which verifies that the given name is unique, shows feedback to the user,
 * and prevents the form from being submitted if the value is invalid.
 *
 * @param url {string} URL to query.
 * @param selector {string} Selector of input element.
 */
function UniqueNameValidator(url, selector = "#name") {
  let self = this;
  self.url = url;
  self.selector = selector;

  self.value = ko.observable($(selector).attr('value'));
  self.valid = ko.computed(checkUniqueName);
  self.validator = checkUniqueName;

  /**
   * Function that facilitates server-side query whether the given name is valid or not.
   *
   * Function does not begin to query until `name` is 4 or more characters long.
   */
  function checkUniqueName() {
    return $.getJSON(self.url, {'name': self.value},
      function (data) {
        if (ko.toJS(self.value).length > 3) {
          return markInvalid(self.selector, !(data.unique));
        }
        return false;
      })
  }
}


/**
 * Form wrapper that prevents an invalid form from being submitted.
 *
 * @param selector {string} selector of form element to validate
 * @param inputs {array} An array of validator objects (which should have a `valid` function)
 */
function FormValidator(selector, inputs) {
  let self = this;
  self.form = $(selector);
  self.inputs = inputs;

  self.formSubmit = function (formElement) {
    if (checkValid()) {
      return true;
    } else {
      // TODO: UI event should occur
    }
  };

  /**
   * Checks every stored input and verifies that it is valid.
   * It is agnostic to implementation details as only `valid` is called, which should return a boolean value.
   *
   *
   * @returns {boolean} false if one input element is invalid. true if all input elements are valid.
   */
  function checkValid() {
    console.log('checking validity');
    for (let i = 0; i < self.inputs.length; i++) {
      if (self.inputs[i].validator() === false) {
        console.log('invalid');
        return false
      }
    }
    return true;
  }
}