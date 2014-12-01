(function () {
  'use strict';

  $('.navbar-nav li a').each(function () {
    var $this = $(this);
    var href = $this.attr('href');

    if (href === location.pathname ||
      (href !== '/' && location.pathname.indexOf(href) === 0)) {
      $this.closest('li').addClass('active');
    }
  });
})();
