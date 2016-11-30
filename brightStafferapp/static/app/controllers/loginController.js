'use strict';

mainApp.config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('[[').endSymbol(']]');
})
mainApp.controller('loginController',
		function($scope, $rootScope, $location, $http, $window, $resource, appService) {
		 $scope.showErr = false;
         $scope.data = {
         user_name: '',
         user_password:''
         };
	/**Create function for user login **/
	$scope.userLogin = function() {
        var requestObject = {
        	'username': $scope.data.user_name,
        	'password': $scope.data.user_password
        };
       appService.userLogin(requestObject).then(function(response){
         if(response.message == "success") {
                  console.log(response)
         }else{
            $scope.showErr = true;
         }
       });
     }
});