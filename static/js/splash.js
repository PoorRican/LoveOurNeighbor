function removeSplash() {
  $("#splash").slideUp("800", function () {
    $("#content").delay(100).animate({"opacity": "1.0"}, 800);
  });
  setTimeout(function() {
    $("#splash").remove();
  }, 800);
};

function youngin() {
  url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";

  var win = window.open(url, '_blank');
  win.focus();
};

// Code to execute when page loads
$(document).ready(function () {
  if ($("#splash").is(":visible")) {  // make .content
    $("#content").css({"opacity": "0"});
  }
});
