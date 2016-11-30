'use strict';

mainApp.config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('[[').endSymbol(']]');
})
mainApp.controller('signupController',
		function($scope, $rootScope, $location, $http, $window, $resource, appService) {

        $scope.user_Signup = function() {
         var requestObject = {
            'firstName':$scope.data.first_name,
        	'lastName': $scope.data.last_name,
        	'userEmail': $scope.data.user_email,
        	'password': $scope.data.password
         };
         appService.userSignup(requestObject).then(function(response){
         if(response.message == "success") {
                  console.log(response);
         }else{
          console.log('response');
         }
       });
     }
});