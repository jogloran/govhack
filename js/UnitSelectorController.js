function UnitSelectorController($scope, $rootScope, $dialog, $cookies) {
	function installPosition(position) {
	  $rootScope.appState.coords = position.coords;
	  console.log($rootScope.appState);
	}

	$scope.askPermission = function() {
		if (typeof $cookies.askedPermission === 'undefined') {
		    var title = "Can Our History use your suburb?";
		    var msg = "Our History can find out your suburb so you can learn about your local area. Ask your parent, guardian or teacher for permission, or just press 'Don't use my location'.";
		    var btns = [{result:'cancel', label: "Don't use my location"}, {result:'ok', label: 'Use my location', cssClass: 'btn-primary'}];

		    var dialog = $dialog.messageBox(title, msg, btns)
		    .open()
		    .then(function(result){
		      if (result === "ok") {
		        if (navigator.geolocation) {
		          console.log('getting position');
		          navigator.geolocation.getCurrentPosition(installPosition);
		        }
		      }

		      $cookies.askedPermission = 'yes';
		    });
		    console.log(dialog);
		}

	    $cookies.askedPermission = 'yes';
	  };
}