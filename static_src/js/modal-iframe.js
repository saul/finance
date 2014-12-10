(function () {
  'use strict';

  var $modal = $('#modal-iframe');
  var $iframeLoading = $('#modal-loading');
  var $iframeContent = $('#modal-iframe-content');
  var $iframe = $('#modal-iframe-content iframe');

  window.iframeModal = {
    open: function (href) {
      if (!this.isTop()) {
        console.warn('iframeModal.open: not top');
        return window.top.iframeModal.open(href);
      }

      // show loading screen
      $iframeLoading.show();
      $iframeContent.hide();

      // set iframe src
      $iframe.attr('src', href);

      // show modal
      $modal.modal('show');
    },

    close: function () {
      if (!this.isTop()) {
        return window.top.iframeModal.close();
      }
    },

    isTop: function () {
      return window === window.top;
    }
  };

  $iframe.load(function () {
    // hide loading screen
    $iframeLoading.hide();
    $iframeContent.show();
  });

  $modal.on('hidden.bs.modal', function () {
    $iframe.attr('src', 'about:blank');
  });

  $('[data-toggle="modal-iframe"]').click(function () {
    var $this = $(this);
    window.iframeModal.open($this.attr('data-target'));
  });
})();
