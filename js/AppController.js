app = angular.module('App', ['ui.bootstrap', 'ngSanitize']);

app.directive('ghAffix', function () {
    return function (scope, element, attrs) {
        element.affix({ offset: 67 });
    };
});

function AppController($scope) {
	$scope.world = 'Hello!';

	$scope.currentUnit = 0;
}