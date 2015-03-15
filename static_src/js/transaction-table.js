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

  $('.transaction-table td.category').click(function () {
    var $this = $(this);

    var $row = $this.closest('tr');
    var pk = $row.data('pk');

    var $static = $this.find('.static');
    var $dynamic = $this.find('.dynamic');

    var $select = $('.transaction-categorise-container select[name=category]').clone();
    $select.find('[value="' + $static.data('category-id') + '"]').attr('selected', 'selected');

    $dynamic.empty().append($select);
    window.initSelectize($select);

    $select[0].selectize.on('dropdown_close', function () {
      var value = this.$control.find('.item').data('value') || this.$control_input.val();
      var createdValue = value !== '' && this.$control.find('.item').data('value') === '';

      if (!createdValue && $static.data('category-id') == value) {
        $dynamic.hide();
        $static.show();
        return;
      }

      var $form = $('.transaction-categorise-container form');
      $form.find('[name=transaction]').val(pk);
      $form.find('[name=create_category]').prop('checked', createdValue);
      $form.find('[name=category]').val(value);
      $form.submit();
    });
    $select[0].selectize.open();

    //
    $static.hide();
    $dynamic.show();
  });
})();
