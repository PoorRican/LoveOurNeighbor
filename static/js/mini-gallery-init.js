$(function () {
  const tile = $('.mini-gallery .tile');
  let setHeights = function () {
    tile.height(tile.width());

    // reposition 'show-more' tile
    const sm = $('.show-more span');
    let pad = sm.parent().outerHeight() / 2 - sm.outerHeight();
    sm.parent().css('padding-top', pad);
  };

  setHeights();
  $("window").on("resize", setHeights);
});