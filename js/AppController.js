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
    new Morris.Line({
    // ID of the element in which to draw the chart.
    element: 'graph',
    // Chart data records -- each entry in this array corresponds to a point on
    // the chart.
    data: scope.currentItem.datapoints,
    // The name of the data record attribute that contains x-values.
    xkey: 'year',
    // A list of names of data record attributes that contain y-values.
    ykeys: ['Sydney', 'Melbourne', 'Adelaide', 'Canberra', 'Darwin', 'Perth', 'Brisbane'] ,
    // Labels for the ykeys -- will be displayed when you hover over the
    // chart.
    labels: ['Sydney', 'Melbourne', 'Adelaide', 'Canberra', 'Darwin', 'Perth', 'Brisbane'] ,
    hideHover: true,
    pointSize: 1,
    });
	};
});

function AppController($scope, $rootScope) {

  $scope.modules = [{
    name: 'Present and Past',
    stage: [1, 1],
    colour: '#16a085',
    id: 'family'
  },
  {
    name: 'Past in the Present',
    stage: [1, 2],
    colour: '#2980b9',
    id: 'past'
  },
  {
    name: 'Community and Remembrance',
    stage: [2, 1],
    colour: '#8e44ad',
    id: 'community'
  },
  {
    name: 'First Contact',
    stage: [2, 2],
    colour: '#f39c12',
    id: 'contact'
  },
  {
    name: 'The Australian Colonies',
    stage: [3, 1],
    colour: '#e74c3c',
    id: 'colonies'
    },  
    {
    name: 'Australia as a Nation',
    stage: [3, 2],
    colour: '#16a085',
    id: 'nation',
  },
  ];
	$scope.world = 'Hello!';

  $rootScope.appState = { isLoading: false };
	$rootScope.currentUnit = { unit: -1 };

  $scope.loadingMessages = ['Loading...', 'Attendere...', 'Περιμένετε', '请稍等...', 'Vui lòng đợi...', 'Bitte warten...', 'Espere...'];
  $scope.loadingLanguages = ['English', 'Italian', 'Greek', 'Chinese', 'Vietnamese', 'German', 'Spanish'];
  $scope.currentLoadingMessageIndex = 0;
  $scope.loadingMessage = $scope.loadingMessages[$scope.currentLoadingMessageIndex];
  $scope.loadingLanguage = $scope.loadingLanguages[$scope.currentLoadingMessageIndex];
}
