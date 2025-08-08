'use strict';
document.addEventListener('DOMContentLoaded', function () {
  setTimeout(function () {
    floatchart();
  }, 500);
});

'use strict';

// Define floatchart function
function floatchart() {
  fetch('/pageview-data')
    .then(response => response.json())
    .then(data => {
      var options = {
        chart: {
          height: 450,
          type: 'area',
          toolbar: { show: false }
        },
        dataLabels: { enabled: false },
        colors: ['#1890ff', '#13c2c2', '#f44336'],
        series: [
          { name: 'Admin', data: data.Admin },
          { name: 'Caretaker', data: data.Caretaker },
          { name: 'PWID', data: data.PWID }
        ],
        stroke: { curve: 'smooth', width: 2 },
        xaxis: { categories: data.hours }
      };

      var chartContainer = document.querySelector('#visitor-chart');
      chartContainer.innerHTML = '';
      var chart = new ApexCharts(chartContainer, options);
      chart.render();
    })
    .catch(err => {
      console.error('Failed to load pageview data:', err);
    });
}

// Wait for DOM loaded then run floatchart + render other charts
document.addEventListener('DOMContentLoaded', function () {
  floatchart();

  // Other charts as IIFEs:
  (function () {
    var options = {
      chart: { type: 'bar', height: 365, toolbar: { show: false } },
      colors: ['#13c2c2'],
      plotOptions: { bar: { columnWidth: '45%', borderRadius: 4 } },
      dataLabels: { enabled: false },
      series: [{ data: [80, 95, 70, 42, 65, 55, 78] }],
      stroke: { curve: 'smooth', width: 2 },
      xaxis: {
        categories: ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'],
        axisBorder: { show: false },
        axisTicks: { show: false }
      },
      yaxis: { show: false },
      grid: { show: false }
    };
    var chart = new ApexCharts(document.querySelector('#income-overview-chart'), options);
    chart.render();
  })();

  (function () {
    var options = {
      chart: { type: 'line', height: 340, toolbar: { show: false } },
      colors: ['#faad14'],
      plotOptions: { bar: { columnWidth: '45%', borderRadius: 4 } },
      stroke: { curve: 'smooth', width: 1.5 },
      grid: { strokeDashArray: 4 },
      series: [{ data: [58, 90, 38, 83, 63, 75, 35, 55] }],
      xaxis: {
        type: 'datetime',
        categories: [
          '2018-05-19T00:00:00.000Z',
          '2018-06-19T00:00:00.000Z',
          '2018-07-19T01:30:00.000Z',
          '2018-08-19T02:30:00.000Z',
          '2018-09-19T03:30:00.000Z',
          '2018-10-19T04:30:00.000Z',
          '2018-11-19T05:30:00.000Z',
          '2018-12-19T06:30:00.000Z'
        ],
        labels: { format: 'MMM' },
        axisBorder: { show: false },
        axisTicks: { show: false }
      },
      yaxis: { show: false }
    };
    var chart = new ApexCharts(document.querySelector('#analytics-report-chart'), options);
    chart.render();
  })();

  (function () {
    var options = {
      chart: { type: 'bar', height: 430, toolbar: { show: false } },
      plotOptions: { bar: { columnWidth: '30%', borderRadius: 4 } },
      stroke: { show: true, width: 8, colors: ['transparent'] },
      dataLabels: { enabled: false },
      legend: {
        position: 'top',
        horizontalAlign: 'right',
        show: true,
        fontFamily: `'Public Sans', sans-serif`,
        offsetX: 10,
        offsetY: 10,
        labels: { useSeriesColors: false },
        markers: { width: 10, height: 10, radius: '50%', offsetX: 2, offsetY: 2 },
        itemMargin: { horizontal: 15, vertical: 5 }
      },
      colors: ['#faad14', '#1890ff'],
      series: [
        { name: 'Net Profit', data: [180, 90, 135, 114, 120, 145] },
        { name: 'Revenue', data: [120, 45, 78, 150, 168, 99] }
      ],
      xaxis: { categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'] }
    };
    var chart = new ApexCharts(document.querySelector('#sales-report-chart'), options);
    chart.render();
  })();
});
