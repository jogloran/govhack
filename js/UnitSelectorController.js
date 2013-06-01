function UnitSelectorController($scope, $rootScope) {
	$scope.firstUnit = function(unit) {
	  return unit.stage[1] === 1;
	};
	$scope.secondUnit = function(unit) {
	  return unit.stage[1] === 2;
	}

	$scope.firstRowOfUnits = function() {

	};
	$scope.secondRowOfUnits = function() {

	};
}