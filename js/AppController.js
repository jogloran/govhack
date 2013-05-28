app = angular.module('App', ['ui.bootstrap', 'ngSanitize']);

function AppController($scope) {
	$scope.world = 'Hello!';
}