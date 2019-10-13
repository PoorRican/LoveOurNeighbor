angular.module('LON').factory('commentService', commentService);

function commentService() {
  return {
    hide: hide,
    show: show
  };

  /** Controls the display of new comment forms on the page.
   *
   *  All elements of 'new_comment' are styled (forms hidden, buttons shown).
   *  Then the targeted comment form is shown and the button is hidden.
   *  This ensures that only a single form is shown at a time.
   *
   *  TODO: comment form should be dynamically created instead of hardcoded
   **/
  function show(event) {
    // reset all 'new_comment' divs to default styling
    reset();

    // style selected form and button respectively
    if ($(event.target).parent().parent()[0].classList.value.includes("wrapper")) {
      // clicked button and not inner text. therefore, dont unpack as many parent elements
      $(event.target).parent().children().css('display', 'block');
      $(event.target).css('display', 'none');
    } else {
      $(event.target).parent().parent().children().css('display', 'block');
      $(event.target).parent().css('display', 'none');
    }
  }

  function hide(event) {
    // hide selected form and button respectively
    if ($(event.target).parent().parent().parent()[0].classList.value.includes("wrapper")) {
      // clicked button and not inner text. therefore, dont unpack as many parent elements
      $(event.target).parent().parent().children().css('display', 'block');
      $(event.target).parent().css('display', 'none');
    } else {
      $(event.target).parent().parent().parent().children().css('display', 'block');
      $(event.target).parent().parent().css('display', 'none');
    }
  }

  function reset() {
    var new_comment_divs = document.getElementsByClassName('new_comment');
    for (d = 0; d < new_comment_divs.length; d++) {
      new_comment_divs[d].children[0].style.display = 'none';
      new_comment_divs[d].children[1].style.display = 'block';
    }
  }
}
