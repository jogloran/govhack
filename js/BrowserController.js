function BrowserController($scope, $http) {
	$scope.selectedIndex = 0;
	$scope.currentItem = null;

	$scope.$watch('selectedIndex', function(newValue, oldValue) {
		console.log('watcher');
		if ($scope.items) {
			$scope.currentItem = $scope.items[newValue];
		}
	});

	$http.get('/data').success(function(data) {
		$scope.items = data.items;
		$scope.currentItem = $scope.items[0];
	});

	Mousetrap.bind('left', function(e) {
		$scope.$apply(function(scope) {
			if (scope.selectedIndex > 0) {
				scope.selectedIndex--;
			}

			parallax.panel.left();
		});
	});
	Mousetrap.bind('right', function(e) {
		$scope.$apply(function(scope) {
			if (scope.selectedIndex < scope.items.length - 1) {
				scope.selectedIndex++;
			}

			parallax.panel.right();
		});
	});
}