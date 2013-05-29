function BrowserController($scope, $http) {
	$scope.items = $http.get('/data').then(function(response) {
		return response.data.items;
	});
}