
function MainCtrl($scope, $rootScope, $location, $http, $cookies, $cookieStore) { /*global controller */

    this.userName = 'BrightStaffer';

};

function loginCtrl($scope, $rootScope, $state, $http, $cookies, $cookieStore, $timeout, loginService) { /* login controller responsible for login functionality */
     $scope.showErr = false;
     $scope.isDisabled = false;
     $scope.emailPattern = /^[a-z]+[a-z0-9._]+@[a-z]+\.[a-z.]{2,5}$/;  //email validation pattern
         $scope.data = {
         user_name: '',
         user_password:''
         };
	/**Create function for user login **/
	$scope.userLogin = function() {
	  $scope.showErr = false;
        var requestObject = {
        	'username': $scope.data.user_name,       // username field value
        	'password': $scope.data.user_password    // password filed value
        };
        if($scope.loginForm.$valid){
        $scope.isDisabled = true;
         loginService.userLogin(requestObject).then(function(response){
         if(response.message == "success") {
          var userData = {};
              userData.first_name = response.first_name;
              userData.last_name = response.last_name;
              userData.token = response.user_token;
              userData.user_email = response.user_name;
           $rootScope.globals.currentUser = userData;   // storing the logged in user data for further communication on site
           $cookieStore.put('userData',userData);
           $state.go('dashboard', "");                  // after successful log in redirection to dashboard view
         }else{
            $scope.showErr = true;
            $timeout( function(){$scope.showErr = false;$scope.isDisabled = false;} , 9000); // removing unsuccessfull error message after 9s

         }
         });

       }
     }

      $scope.hideMessages = function(){ /*Hide error messages when user interact with fieds*/
       $("#loginForm input").each(function(){
            var spanClass = $(this).next('span').attr('class');
            if($(this).val().length <= 0 && ($(this).next('span').hasClass('error'))){
                $(this).next('span').removeClass('error').text("");
            }else if($(this).val().length > 0 && ($(this).next('span').hasClass('error'))){
                $(this).next('span').removeClass('error').text("");
            }
        });
    }
}


function signupCtrl($scope, $rootScope, $state, $http, $window, $timeout,$cookies, $cookieStore, signupService) { /* signup controller responsible for signup form functionality */
    $scope.userRegistration = {};
    $scope.isDisabled = false;
    $scope.errorMessage = '';
    $scope.success = false;
    $scope.passwordStrength = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;  // password validation pattern
    $scope.emailPattern = /^[a-z]+[a-z0-9._]+@[a-z]+\.[a-z.]{2,5}$/;                             // email pattern
    $scope.user_Signup = function() { /* signup function submitting user details to API*/
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
              userData.first_name = response.first_name;
              userData.last_name = response.last_name;
              userData.token = response.user_token;
              userData.user_email = response.user_name;
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

    $scope.hideMessages = function(){ /*Hide error messages when user interact with fieds*/
       $("#signupForm input").each(function(){
            var spanClass = $(this).next('span').attr('class');
            if($(this).val().length <= 0 && ($(this).next('span').hasClass('error'))){
                $(this).next('span').removeClass('error').text("");
            }else if($(this).val().length > 0 && ($(this).next('span').hasClass('error'))){
                $(this).next('span').removeClass('error').text("");
            }
        });
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

function topnavCtrl($scope, $rootScope, $state, $http, $window, $stateParams, $cookies, $cookieStore, $location ){
    this.logout = function(){
          $cookieStore.remove('userData');
          $rootScope.globals = {};
          $state.go('login','');
       }
}

function createProjectCtrl($scope, $rootScope, $state, $http, $window, $stateParams, $cookies, $cookieStore, $location , jobPostService){
    $scope.projectForm = {};
    $rootScope.globals.currentProject_id = '';
    $scope.isValid = false;
    this.projectNamePattern = /^[a-z0-9]+$/i;///((^[ A-Za-z0-9_@./#-]*)|(^[a-zA-Z]+[_@./#-]*)|(^[0-9]+[a-z]+)|(^[a-z]+[0-9]+))+[0-9a-z]+$/i;
    this.companyNamePattern = /^[a-zA-Z]*$/;
    this.locationPattern =/((^^(?!0{5})\d{5})|(^[a-z]*))$/;
    $scope.checkMessage = function(){ /*Hide error messages when user interact with fieds*/
       $("#createProjectForm input").each(function(){
           $scope.isValid = false;
            var spanClass = $(this).next('span').attr('class');
            if($(this).val().length <= 0 && ($(this).next('span').hasClass('error'))){
                $(this).next('span').removeClass('error').text("");
            }else if($(this).val().length > 0 && ($(this).next('span').hasClass('error'))){
                $(this).next('span').removeClass('error').text("");
            }
        });
    }

     $scope.submitStepOne = function(currentState,prevTabId,currentTabId){
         $("#createProjectForm input").each(function(){ /*Show error on blank field when user submit*/
                var spanClass = $(this).next('span').attr('class');
                if($(this).val().length <= 0){
                    $(this).next('span').css('display','block');
                    $(this).next('span').addClass('error').text("Required.");
                }else if($(this).val().length > 0 && ($(this).next('span').hasClass('error'))){
                    $(this).next('span').removeClass('error').text("");
                }
		});

		if($scope.projectForm.projectName && $scope.projectForm.companyDivsion && $scope.projectForm.nameZip)
		  {
            var backButton = angular.element(document.querySelector('#previous'));
              backButton.removeClass('disabled');
            var prevTab = angular.element(document.querySelector(prevTabId));
            prevTab.removeClass('current');
            prevTab.addClass('done');
            prevTab.attr('aria-selected','false');
            var currentTab = angular.element(document.querySelector(currentTabId));
            currentTab.addClass('current');
            currentTab.attr('aria-selected','true');
             $state.go('create.step2','');
		  }

      }



     $scope.SwitchFuction = function () {
      var currentState = $state.current.name;
      var prevTabId;
      var currentTabId;
        switch (currentState) {
            case 'create.step1':
                prevTabId = '#form-t-0';
                currentTabId = '#form-t-1';
                $scope.submitStepOne(currentState,prevTabId,currentTabId);
                break;
            case 'create.step2':
                prevTabId = '#form-t-1';
                currentTabId = '#form-t-2';
                $scope.changeState(currentState,prevTabId,currentTabId);
                $state.go('create.step3','');
                break;
            case 'create.step3':
                prevTabId = '#form-t-2';
                currentTabId = '#form-t-3';
                $scope.changeState(currentState,prevTabId,currentTabId);
                $state.go('create.step4','');
                 var nextButton = angular.element(document.querySelector('#next'));
                 nextButton.css('display','none');
                break;
        }

     }

     $scope.goToBack = function () {
      var currentState = $state.current.name;
        switch (currentState) {
            case 'create.step2':
                $state.go('create.step1','');
                break;
            case 'create.step3':
                $state.go('create.step2','');
                break;
            case 'create.step4':
                var nextButton = angular.element(document.querySelector('#next'));
                 nextButton.css('display','block');
                $state.go('create.step3','');
                prevTabId = '#form-t-3';
                currentTabId = '#form-t-2';
                $scope.changeState(currentState,prevTabId,currentTabId);
                break;
        }

     }
  $scope.update = function(elm , name, value){
  console.log(elm[0].name);
  console.log( $rootScope.globals.currentProject_id)
       var is_published = false;
       var token = $rootScope.globals.currentUser.token;
       var recuriter = $rootScope.globals.currentUser.user_email;
       var requestObject = {};
            if(elm[0].name == "company_name" || "location"){
                var element = angular.element(document.querySelector('#project_name'));
                  if(element && !element[0].value ){
                        element[0].focus();
                        $scope.isValid = true;
                      }
               }

            if($state.current.name == "create.state4")
               is_published = true;

            if(value) {
               requestObject["id"] = $rootScope.globals.currentProject_id;
               requestObject[elm[0].name] = value;
               requestObject["token"] = token;
               requestObject["recuriter"] = recuriter;
               requestObject["is_published"] = is_published;
            console.log(requestObject)
                jobPostService.jobPost(requestObject).then(function(response){
                     if(response.message == "success") {
                       if( $rootScope.globals.currentProject_id == '')
                         $rootScope.globals.currentProject_id = response.project_id;

                         console.log($rootScope.globals.currentProject_id)
                         console.log(response)
                     }else{

                     }
                   });
              }

    }
}

angular
    .module('brightStaffer')
    .controller('MainCtrl', MainCtrl)
    .controller('loginCtrl', loginCtrl)
    .controller('signupCtrl', signupCtrl)
    .controller('forgotCtrl', forgotCtrl)
    .controller('resetPwCtrl', resetPwCtrl)
    .controller('topnavCtrl', topnavCtrl)
    .controller('createProjectCtrl', createProjectCtrl);