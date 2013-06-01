app = angular.module('App', ['ui.bootstrap', 'ngSanitize']);
app.config(function ($dialogProvider) {
  $dialogProvider.options({backdropFade: true, dialogFade: true});
});

app.directive('ghVerticalFluid', function() {
	return function (scope, element, attrs) {
	    $(element).css({'height':($(window).height() - 57 - 40)+'px'});
	    $(window).resize(function(){
	        $(element).css({'height':($(window).height() - 57 - 40)+'px'});
	    });
	};
});

app.directive('ghAffix', function () {
    return function (scope, element, attrs) {
        element.affix({ offset: 67 });
    };
});

app.directive('ghGraph', function() {
	return function (scope, element, attrs) {
		new Morris.Line({
  // ID of the element in which to draw the chart.
  element: 'graph',
  // Chart data records -- each entry in this array corresponds to a point on
  // the chart.
  data: [
    { year: '2008', value: 20 },
    { year: '2009', value: 10 },
    { year: '2010', value: 5 },
    { year: '2011', value: 5 },
    { year: '2012', value: 20 }
  ],
  // The name of the data record attribute that contains x-values.
  xkey: 'year',
  // A list of names of data record attributes that contain y-values.
  ykeys: ['value'],
  // Labels for the ykeys -- will be displayed when you hover over the
  // chart.
  labels: ['Value']
});
	};
});

function AppController($scope) {
  $scope.modules = [{
    name: 'Present and Past',
    stage: [1, 1],
  },
  {
    name: 'Past in the Present',
    stage: [1, 2],
  },
  {
    name: 'Community and Remembrance',
    stage: [2, 1],
  },
  {
    name: 'First Contact',
    stage: [2, 2],
  },
  {
    name: 'The Australian Colonies',
    stage: [3, 1],
  },
  {
    name: 'Australia as a Nation',
    stage: [3, 2],
  }
  ];
	$scope.world = 'Hello!';

	$scope.currentUnit = 0;
}
