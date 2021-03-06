app = angular.module('App', ['ui.bootstrap', 'ngSanitize', 'ngCookies']);
app.config(function ($dialogProvider) {
  $dialogProvider.options({backdropFade: true, dialogFade: true});
});

app.directive('ghSlider', function() {
    return {
      replace: true,
      require: '?ngModel',
      link: function(scope, elem, attrs, ngModel) {
        function propChangeHandler(prop) {
          return function(value, oldValue) {
            // called when max,min expressions change
            var slider = $(elem).slider('option', prop, value);
            var modelValue = ngModel.$viewValue;

            // if the model value is now beyond the new value, clamp it back
            var extremum = slider.slider('option', prop);
            
            if (extremum) {
              if ((prop === 'max' && modelValue > extremum)
               || (prop === 'min' && modelValue < extremum)) {
                ngModel.$setViewValue(extremum);
              }
            }
          };
        }
        scope.$watch(attrs.max, propChangeHandler('max'));
        scope.$watch(attrs.min, propChangeHandler('min'));

        ngModel.$render = function() {
          // called when the model variable changes
          $(elem).slider('values', 0, ngModel.$viewValue[0]);
          $(elem).slider('values', 1, ngModel.$viewValue[1]);
        };

        $(elem).slider({
          range: true,
          min: attrs.min,
          max: attrs.max,
          values: [attrs.min, attrs.max],
          slide: function(event, ui) {
            scope.$apply(function() {
              var start = ui.values[0];
              var end = ui.values[1];

              ngModel.$setViewValue([start, end]);
            });
          }
        });
      },
    }
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

app.directive('ghNeedsPermission', function() {
  return function (scope, element, attrs) {
    console.log('gh needs permission');
    scope.askPermission();
  }
});

var loadingMessageDelay = 1800;

app.directive('ghLoading', function ($timeout) {
    return function (scope, element, attrs) {
      $(window).resize(function(){
          $(element).css({
              position:'absolute',
              left: ($(window).width() - $(element).outerWidth())/2,
              top: ($(window).height() - $(element).outerHeight())/2
          });
      });
      $(window).resize();

      var fn = function() {
        scope.loadingMessage = scope.loadingMessages[++scope.currentLoadingMessageIndex % scope.loadingMessages.length];
        scope.loadingLanguage = scope.loadingLanguages[scope.currentLoadingMessageIndex % scope.loadingMessages.length];
        $timeout(fn, loadingMessageDelay);
      };
      $timeout(fn, loadingMessageDelay);
    };
});

app.directive('ghGraph', function() {
    return function (scope, element, attrs) {
      scope.$watch('currentItem', function(value) {
        console.log('item changed');
        $('#graph').empty();
      new Morris.Line({
      // ID of the element in which to draw the chart.
      element: 'graph',
      // Chart data records -- each entry in this array corresponds to a point on
      // the chart.
      data: scope.currentItem.datapoints,
      // The name of the data record attribute that contains x-values.
      //xkey: 'year',
    xkey: scope.currentItem.xkey,
      // A list of names of data record attributes that contain y-values.
      //ykeys: ['Sydney', 'Melbourne', 'Adelaide', 'Canberra', 'Darwin', 'Perth', 'Brisbane'] ,
    ykeys: scope.currentItem.ykeys,
      // Labels for the ykeys -- will be displayed when you hover over the
      // chart.
      //labels: ['Sydney', 'Melbourne', 'Adelaide', 'Canberra', 'Darwin', 'Perth', 'Brisbane'] ,
    labels: scope.currentItem.labels,
      hideHover: true,
      pointSize: 1,
      });
      });
    };
});

app.directive('ghTimelineGraph', function() {
  console.log('ghTimelineGraph');
	return function (scope, element, attrs) {
    scope.$watch('currentItem', function(value) {
      console.log('timeline graph: item changed');
      if (scope.selectedGraph) {
        $('#timeline-graph').empty();
          new Morris.Line({
            element: 'timeline-graph',
            data:   scope.selectedGraph.datapoints,
          	xkey:   scope.selectedGraph.xkey,
          	ykeys:  scope.selectedGraph.ykeys,
          	labels: scope.selectedGraph.labels,
            hideHover: true,
            pointSize: 1,
            });
      }
    });
	};
});

function AppController($scope, $rootScope, $cookies, $dialog) {
  var c = '#E07E43'
  $scope.modules = [{
    name: 'Present and Past',
    stage: [1, 1],
    colour: c,
    id: 'family'
  },
  {
    name: 'Past in the Present',
    stage: [1, 2],
    colour: c,
    id: 'past'
  },
  {
    name: 'Community and Remembrance',
    stage: [2, 1],
    colour: c,
    id: 'community'
  },
  {
    name: 'First Contact',
    stage: [2, 2],
    colour: c,
    id: 'contact'
  },
  {
    name: 'The Australian Colonies',
    stage: [3, 1],
    colour: c,
    id: 'colonies'
    },  
    {
    name: 'Australia as a Nation',
    stage: [3, 2],
    colour: c,
    id: 'nation',
  },
  ];
	$scope.world = 'Hello!';

  $rootScope.appState = { isLoading: false };
	$rootScope.currentUnit = { unit: -1};
	//$rootScope.currentUnit = { unit: $scope.modules[0] };

  $scope.loadingMessages = ['Loading...', 'Attendere...', 'Περιμένετε', '请稍等...', 'Vui lòng đợi...', 'Bitte warten...', 'Espere...'];
  $scope.loadingLanguages = ['English', 'Italian', 'Greek', 'Chinese', 'Vietnamese', 'German', 'Spanish'];
  $scope.currentLoadingMessageIndex = 0;
  $scope.loadingMessage = $scope.loadingMessages[$scope.currentLoadingMessageIndex];
  $scope.loadingLanguage = $scope.loadingLanguages[$scope.currentLoadingMessageIndex];

  $scope.bodyStyleForUnit = function(unit) {
    if (unit === -1) {
      return { "background-color": "#a8a8a8" };
    } else {
      return { "background-color": "#323C46" };
    }
  }
}
