function BrowserController($scope, $http, $dialog, $timeout, $rootScope, $filter) {
	function makeItems(items) {
		return items.map(function(item) {
			var item= {
				startDate: item.start + ',01,01',
				endDate: item.end ? item.end + ',01,01' : null,
				headline: item.title,
				text: item.subtitle,
				asset: {
					media: item.url,
				}
			};
			console.log(item);
			return item;
		});
	}

	function makeModelFromAddedItems(items) {
		var model = {
			timeline: {
				headline: 'My timeline',
				type: 'default',
				text: '<h3>' + $scope.currentUnit.unit.name + '</h3>',
				asset: {
					'media': 'images/' + $scope.currentUnit.unit.id + '.jpg'
				},
				date: makeItems(items)
			}
		};

		return model
	}

	$scope.selectedIndex = 0;
	$scope.currentItem = null;

	$scope.addedItems = [];

	// get a graph from addedItems
	$scope.selectedGraph = null;

	$scope.updateSelectedGraph = function() {
		var items = $scope.addedItems;
		var found = false;
		for (var i in items) {
			var item = items[i];
			if (item.type === 'graph') {
				$scope.selectedGraph = item;
				found = true;
				break;
			}
		}

		if (!found) {
			$scope.selectedGraph = null;
		}

		console.log('selected: ' + $scope.selectedGraph);
	}

	$scope.filterQuery = null;

	$scope.displayDialog = function() {
		console.log('open');
		$scope.timelineShown = true;

		unbindKeys();

		var model = makeModelFromAddedItems($scope.addedItems);

		var timeline_config = {
		    width:              '100%',
		    height:             '380',
		    source:             model,
		    embed_id:           'timeline-embed',
		}

		$timeout(function() {
			createStoryJS(timeline_config);
		}, 1000);
	};

	$scope.close = function() {
		console.log('close');
		$scope.timelineShown = false;

		rebindKeys();
	}

	$scope.$watch('selectedIndex', function(newValue, oldValue) {
		console.log('watcher');
		if ($scope.items) {
			$scope.currentItem = $scope.items[newValue];
		}
	});

	var lat, lng;
	if ($rootScope.appState.coords) {
		lat = $rootScope.appState.coords.latitude;
		lng = $rootScope.appState.coords.longitude;
	}

	if ($rootScope.currentUnit.unit.query) {
		params = {
			q: $rootScope.currentUnit.unit.query,
			start: $rootScope.currentUnit.unit.yearRange[0],
			end: $rootScope.currentUnit.unit.yearRange[1],
			lat: lat,
			lng: lng,
		}
	} else {
		params = { module: $rootScope.currentUnit.unit.id, 
			lat: lat, 
			lng: lng }
	}

	$http.get('/data', {
		params: params
	}).success(function(data) {
		$scope.items = data.items;
		$scope.items=$filter('orderBy')($scope.items,['start', 'title', 'url']);
		$scope.items=$filter('filter')($scope.items,$scope.filterQuery);
		$scope.currentItem = $scope.items[0];

		$scope.items.forEach(function(item) {
			item.rotation = rand();
		});

		console.log($scope.items);

		$rootScope.appState.isLoading = false;
	});

	function rebindKeys() {
		Mousetrap.bind(['left', 'up'], function(e) {
			$scope.$apply(function(scope) {
				if (scope.selectedIndex > 0) {
					scope.selectedIndex--;
				}
			});
		});
		Mousetrap.bind(['right', 'down'], function(e) {
			$scope.$apply(function(scope) {
				if (scope.selectedIndex < scope.items.length - 1) {
					scope.selectedIndex++;
				}
			});
		});
		Mousetrap.bind('+', function(e) {
			$('body').find('#add-to-timeline-button').click();
		});
		Mousetrap.bind('-', function(e) {
			$('body').find('#remove-from-timeline-button').click();
		})
	}

	function unbindKeys() {
		['left', 'right', 'up', 'down', '+', '-'].forEach(function(e) {
			Mousetrap.unbind(e);
		});
	}

	function rand() {
		return 2.0*Math.random() - 1.0;
	}

	$scope.transformStyle = function(item) {
		return { 'transform': 'rotate(' + item.rotation + 'deg)' };
	};

	rebindKeys();
}