/**
 * INSPINIA - Responsive Admin Theme
 *
 */

/**
 * MainCtrl - controller
 */
function MainCtrl($scope, $rootScope, $location, $http, $cookies, $cookieStore) {

    this.userName = 'BrightStaffer';

};

function loginCtrl($scope, $rootScope, $state, $http, $cookies, $cookieStore, loginService) {
     $scope.showErr = false;
     $scope.isDisabled = false;
     $scope.emailPattern = /^[a-z]+[a-z0-9._]+@[a-z]+\.[a-z.]{2,5}$/;
         $scope.data = {
         user_name: '',
         user_password:''
         };
	/**Create function for user login **/
	$scope.userLogin = function() {
	  $scope.showErr = false;
        var requestObject = {
        	'username': $scope.data.user_name,
        	'password': $scope.data.user_password
        };
        if($scope.loginForm.$valid){
        $scope.isDisabled = true;
         loginService.userLogin(requestObject).then(function(response){
         if(response.message == "success") {
         console.log(response)
          var userData = {};
              userData.first_name = response.first_name;
              userData.last_name = response.last_name;
              userData.token = response.user_token;
              userData.user_email = response.user_name;
           $rootScope.globals.currentUser = userData;
           $cookieStore.put('userData',userData);
           console.log($cookieStore);
           $state.go('dashboard', "");
         }else{
            $scope.showErr = true;
            $scope.isDisabled = false;
         }
         });
       }
     }
}


function signupCtrl($scope, $rootScope, $state, $http, $window, $timeout,$cookies, $cookieStore, signupService) {
    $scope.userRegistration = {};
    $scope.isDisabled = false;
    $scope.errorMessage = '';
    $scope.success = false;
    $scope.passwordStrength = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;
    $scope.emailPattern = /^[a-z]+[a-z0-9._]+@[a-z]+\.[a-z.]{2,5}$/;
    $scope.user_Signup = function() {
     $scope.errorMessage = '';
         var requestObject = {
            'firstName':$scope.userRegistration.first_name,
        	'lastName': $scope.userRegistration.last_name,
        	'userEmail': $scope.userRegistration.user_email,
        	'password': $scope.userRegistration.password
         };
       if($scope.signupForm.$valid){
            $scope.isDisabled = true;
             signupService.userSignup(requestObject).then(function(response){
             if(response.message == "success") {
               $scope.errorMessage = "Your account has been created!";
               $scope.signupForm.$setPristine();
               $scope.userRegistration = {};
              var userData = {};
              userData.message = response.message;
               $rootScope.globals.currentUser = userData;
               $cookieStore.put('userData',userData);
               $state.go('dashboard', "");
             }else{
              $scope.errorMessage ="User with this email already exists!";
              $scope.isDisabled = false;
             }
           });
       }
    }
}

function forgotCtrl($scope, $rootScope, $state, $http, forgotService) {
     $scope.isDisabled = false;
     $scope.errorMessage = '';
     $scope.emailPattern = /^[a-z]+[a-z0-9._]+@[a-z]+\.[a-z.]{2,5}$/;
	/**Create function for forgot password **/
	$scope.forgotPassword = function() {
	   $scope.errorMessage = '';
        var requestObject = {
        	'email': $scope.user_email
        };
       if($scope.forgotForm.$valid){
            $scope.isDisabled = true;
           forgotService.forgotPassword(requestObject).then(function(response){
             if(response.message == "success") {
               $scope.errorMessage = 'Link to reset password is sent on your mail! Please check.';
             }else{
                $scope.errorMessage = 'No account with this email id.';
                $scope.isDisabled = false;

             }
           });
         }
     }
}


function resetPwCtrl($scope, $rootScope, $state, $http, $window, $stateParams, $location , resetPasswordService) {

    var token =$window.location.href.split('reset_password_confirm/')[1].replace('/','');
    $scope.isDisabled = false;
    $scope.successMsg = false;
    $scope.failMessage = false;
    $scope.success = false;
    $scope.passwordStrength = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;
    $scope.changePassword = function(){
         $scope.isDisabled = true;
         var requestObject = {
        	'token': token,
        	'password': $scope.data.password
        };
       resetPasswordService.resetPassword(requestObject).then(function(response){
         if(response.message == "success") {
           $scope.successMsg = true;
           $scope.success = true;
         }else{
             $scope.failMessage = true;
         }
       });
    }

    $scope.changePath= function () {
     var path = 'http://'+$window.location.host + '/#/login';
     $window.location.href = path;
    }
}

function dashboardCtrl($scope, $rootScope, $state, $http, $window, $stateParams, $cookieStore, $location ){
  $scope.logout = function(){
        $cookieStore.remove('userData');
          $rootScope.globals = {};
          $state.go('login', "");
    }

}

angular
    .module('brightStaffer')
    .controller('MainCtrl', MainCtrl)
    .controller('loginCtrl', loginCtrl)
    .controller('signupCtrl', signupCtrl)
    .controller('forgotCtrl', forgotCtrl)
    .controller('resetPwCtrl', resetPwCtrl)
    .controller('dashboardCtrl', dashboardCtrl);