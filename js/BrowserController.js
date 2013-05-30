function BrowserController($scope, $http) {
	$scope.selectedIndex = 0;
	$scope.currentItem = null;

	$scope.addedItems = [];

	$scope.filterQuery = null;

	$scope.resultFilter = function(e) {
		var result = new RegExp($scope.filterQuery).exec(e.title) !== null;
		console.log($scope);
		return result;
	};

	$scope.$watch('selectedIndex', function(newValue, oldValue) {
		console.log('watcher');
		if ($scope.items) {
			$scope.currentItem = $scope.items[newValue];
		}
	});

	$http.get('/data').success(function(data) {
		$scope.items = data.items;
		$scope.currentItem = $scope.items[0];

		$scope.items.forEach(function(item) {
			item.rotation = rand();
		});

		console.log($scope.items);
	});

	Mousetrap.bind('left', function(e) {
		$scope.$apply(function(scope) {
			if (scope.selectedIndex > 0) {
				scope.selectedIndex--;
			}
		});
	});
	Mousetrap.bind('right', function(e) {
		$scope.$apply(function(scope) {
			if (scope.selectedIndex < scope.items.length - 1) {
				scope.selectedIndex++;
			}
		});
	});

	function rand() {
		return 2.0*Math.random() - 1.0;
	}

	$scope.transformStyle = function(item) {
		return { 'transform': 'rotate(' + item.rotation + 'deg)' };
	};
}