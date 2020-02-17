/*================================================================================
  Item Name: Materialize - Material Design Admin Template
  Version: 5.0
  Author: PIXINVENT
  Author URL: https://themeforest.net/user/pixinvent/portfolio
================================================================================*/

var searchListLi = $(".search-list li"),
   searchList = $(".search-list"),
   searchSm = $(".search-sm"),
   searchBoxSm = $(".search-input-sm .search-box-sm"),
   searchListSm = $(".search-list-sm");

$(function () {
   "use strict";

   // On search input focus, Add search focus class
   $(".header-search-input")
   .focus(function () {
      $(this)
      .parent("form")
      .addClass("header-search-wrapper-focus");
   })
   .blur(function () {
      $(this)
      .parent("form")
      .removeClass("header-search-wrapper-focus");
   });

   //Search box form small screen
   $(".search-button").click(function (e) {
      if (searchSm.is(":hidden")) {
         searchSm.show();
         searchBoxSm.focus();
      } else {
         searchSm.hide();
         searchBoxSm.val("");
      }
   });
   // search input get focus
   $('.search-input-sm').on('click', function () {
      searchBoxSm.focus();
   });

   $(".search-sm-close").click(function (e) {
      searchSm.hide();
      searchBoxSm.val("");
   });
});
