function CreateTopicController($scope, dialog) {
	$scope.submit = function() {
		$scope.currentUnit.unit = { query: $scope.topicString, yearRange: $scope.year };

		dialog.close();
	};

	$scope.year = [1900, 2000];
}