/* global google */
(function () {
  'use strict';

  var sources = {};
  var chartLoaded = false;

  function loadDataSources() {
    console.log('loadDataSources');

    $('[data-vis]').each(function () {
      var $this = $(this);
      var src = $this.attr('data-vis-src');
      sources[src] = null;

      $.ajax(src, {
        dataType: 'text'
      })
        .done(function (response) {
          var data = JSON.parse(response, function (key, value) {
            if (typeof value === 'string') {
              var a = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d*)?(?:Z|(\+|-)([\d|:]*))?$/.exec(value);
              if (a)
                return new Date(value);
            }
            return value;
          });

          console.log('loadDataSources: loading source "' + src + '" completed', data);
          sources[src] = data;
          if (chartLoaded) {
            drawChart($this);
          }
        })
        .fail(function (jqXHR, textStatus) {
          console.error('loadDataSources: loading source "' + src + '" failed: ', textStatus);
        });
    });
  }

  function drawChart($target) {
    var src = $target.attr('data-vis-src');
    var dataTable = google.visualization.arrayToDataTable(sources[src].data);

    var type = $target.attr('data-vis');
    var chart = new google.visualization[type]($target.get(0));

    chart.draw(dataTable, sources[src].options);
  }

  function onChartLoaded() {
    chartLoaded = true;

    Object.getOwnPropertyNames(sources).forEach(function (src) {
      var source = sources[src];

      // has the data loaded yet?
      if (!source) {
        return;
      }

      $('[data-vis-src="' + src + '"]').each(function () {
        drawChart($(this));
      });
    });
  }

  function init() {
    if (!$('[data-vis]').length) {
      return;
    }

    loadDataSources();

    var options = {
      packages: ['corechart']
    };

    google.load('visualization', '1', options);
    google.setOnLoadCallback(onChartLoaded);
  }

  init();
})();
