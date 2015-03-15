(function () {
  'use strict';

  window.initSelectize = function ($elements) {
    $elements.selectize({
      create: true, // allows the user to create a new items that aren't in the list of options
      createOnBlur: true, // when user exits the field new option is created and selected
      persist: false // items created by the user will not show up as available options once they are unselected
    });
  };

  $('[data-toggle="tooltip"]').tooltip();
  window.initSelectize($('select:not(.no-selectize)'));
})();
