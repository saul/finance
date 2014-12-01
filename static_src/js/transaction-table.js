(function () {
  'use strict';

  $('.transaction td.expand').click(function () {
    var $this = $(this);
    var $icon = $this.find('span.glyphicon');
    var $info = $this.siblings('td.description');

    var $extra = $info.find('.extra').toggle();
    if ($extra.is(':visible')) {
      $icon.removeClass('glyphicon-collapse-down').addClass('glyphicon-collapse-up');
    } else {
      $icon.removeClass('glyphicon-collapse-up').addClass('glyphicon-collapse-down');
    }

    return false;
  });
})();
