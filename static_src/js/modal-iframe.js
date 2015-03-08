(function () {
  'use strict';

  var $modal = $('#modal-iframe');
  var $iframeLoading = $('#modal-loading');
  var $iframeContent = $('#modal-iframe-content');
  var $iframe = $iframeContent.find('iframe');

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

      $modal.modal('hide');
    },

    isTop: function () {
      return window === window.top;
    }
  };

  function autoIframeHeight(iframe) {
    iframe.style.height = iframe.contentDocument.body.scrollHeight + 'px';
  }

  $iframe.load(function () {
    // hide loading screen
    $iframeLoading.hide();
    $iframeContent.show();

    // resize iframe content to document size
    var iframe = $iframeContent.find('iframe')[0];
    autoIframeHeight(iframe);

    var observer = new MutationObserver(function () {
      autoIframeHeight(iframe);
    });

    var config = {
      attributes: true,
      childList: true,
      characterData: true,
      subtree: true
    };
    observer.observe(iframe.contentDocument.body, config);
  });

  $modal.on('hidden.bs.modal', function () {
    $iframe.attr('src', 'about:blank');
  });

  $('[data-toggle="modal-iframe"]').click(function () {
    var $this = $(this);
    window.iframeModal.open($this.attr('data-target'));
  });

  $('[data-dismiss="modal-iframe"]').click(function () {
    window.iframeModal.close();
  });
})();
