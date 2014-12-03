(function () {
  'use strict';

  var previewAjax = null;

  $('#pattern-preview').click(function () {
    // abort current ajax request
    if (previewAjax) {
      previewAjax.abort();
    }

    previewAjax = $.ajax({
      url: $('#preview-results').attr('data-src'),
      data: { pattern: $('#id_pattern').val() },
      success: function (result) {
        $('#preview-results').html(result);
      }
    });
  });
})();
