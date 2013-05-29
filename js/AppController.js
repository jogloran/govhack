app = angular.module('App', ['ui.bootstrap', 'ngSanitize']);
app.config(function ($dialogProvider) {
  $dialogProvider.options({backdropFade: true, dialogFade: true});
});

function AppController($scope) {
	$scope.world = 'Hello!';

	$scope.currentUnit = 0;
}