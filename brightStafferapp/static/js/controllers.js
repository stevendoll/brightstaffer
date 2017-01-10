
function MainCtrl($scope, $rootScope, $location, $http, $cookies, $cookieStore, getTopSixProjects, getAllProjects, paginationData,$window) { /*global controller */
    $rootScope.topSixProjectList = [];   // top six project list array
    $scope.allProjectList = [];          // all project array
    $rootScope.totalProjectCount ='';
    $scope.options = [{name:'10',value:10},{name:'25',value:25},{name:'50',value:50},{name:'100',value:100}]; // select drop-down options
    $scope.countList = $scope.options[0];
    $scope.paginationCounter= 1;
    $scope.tableNext = true;

    this.getTopSixProjects = function(){             // function to fetch top 6 projects
          var requestObject = {
            'token': $rootScope.globals.currentUser.token,       // username field value
            'recruiter': $rootScope.globals.currentUser.user_email   // password field value
         };
         getTopSixProjects.topSix(requestObject).then(function(response){
            if(response.message == "success") {
                $rootScope.topSixProjectList = response.top_project;

              }else{
                console.log('error');
            }
         });
    }

    this.showAllProjects = function(){
          var requestObject = {
            'token': $rootScope.globals.currentUser.token,       // username field value
            'recruiter': $rootScope.globals.currentUser.user_email   // password filed value
         };
         getAllProjects.allProjects(requestObject).then(function(response){
            if(response.message == "success") {
                     $rootScope.totalProjectCount = response.publish_project.pop();
                     $rootScope.totalProjectCount = $rootScope.totalProjectCount.count;
                     $scope.allProjectList = response.publish_project;
                     $rootScope.projectCount = response.publish_project.length;
              }else{
                console.log('error');
            }
         });
    }

    this.getValue = function(countList){    //record count change functionality in all project list view
        $(".loader").css('display','block');

        var requestObject = {
                'token': $rootScope.globals.currentUser.token,       // username field value
                'recruiter': $rootScope.globals.currentUser.user_email,   // password filed value
                'page':$scope.paginationCounter,
                'count':countList.value
             };
             paginationData.paginationApi(requestObject).then(function(response){
                if(response.message == "success") {
                    if(response.Pagination.length > 0)
                       $scope.allProjectList = response.Pagination;
                       $rootScope.projectCount = response.Pagination.length;
                     $(".loader").css('display','none');
                  }else{
                    console.log('error');
                    $(".loader").css('display','none');
                      if(response.success == false){
                            $scope.isSuccess = true;
                            $scope.publishMsg = "No data available.";
                            $('#breakPopup').css('display','block');
                         }

                }
             });
    }

    this.changePage = function($event){                      // page counter pagination functionality
    if( !$scope.tableNext && $event.target.name == "next"){
        return;
    }else if($event.target.name == "prev"){
        $scope.tableNext = true;
    }
     $scope.isSuccess = false;
     var nextButton = angular.element(document.querySelector('#Table_next'));
     var prevButton = angular.element(document.querySelector('#Table_previous'));
         if($event.target.name == "next"){
           $scope.paginationCounter++;
           if(prevButton.hasClass('disabled')){
              prevButton.removeClass('disabled');
           }

         }else if($event.target.name == "prev"){
          if(nextButton.hasClass('disabled'))
                nextButton.removeClass('disabled');
               if($scope.paginationCounter >1){
                  $scope.paginationCounter--;
                     }else{
                        prevButton.addClass('disabled');
                        if(nextButton.hasClass('disabled'))
                            nextButton.removeClass('disabled');

                        return;
                     }
         }

         $(".loader").css('display','block');
         var requestObject = {
                'token': $rootScope.globals.currentUser.token,       // username field value
                'recruiter': $rootScope.globals.currentUser.user_email,   // password filed value
                'page':$scope.paginationCounter,
                'count':$scope.countList.value
             };
             paginationData.paginationApi(requestObject).then(function(response){
                if(response.message == "success") {
                    if(response.Pagination.length > 0)
                       $scope.allProjectList = response.Pagination;
                       $rootScope.projectCount = response.Pagination.length;
                   $(".loader").css('display','none');
                  }else{
                    console.log('error');
                    $(".loader").css('display','none');
                    if(response.success == false){
                        if($event.target.name == "next"){
                           nextButton.addClass('disabled');
                           $scope.paginationCounter--;
                           $scope.tableNext = false;
                        }
                        $scope.isSuccess = true;
                        $scope.publishMsg = "No data available.";
                        $('#breakPopup').css('display','block');

                    }
                }
           });
    }

   this.removePopupBox = function(){
       $('#breakPopup').css('display','none');
        $scope.isSuccess = false;
   }

    $scope.reverse = false;
   this.sortBy = function(propertyName) {                   // filed sorting functionality in all project view
        $scope.reverse = ($scope.propertyName === propertyName) ? !$scope.reverse : false;
        $scope.propertyName = propertyName;
        if($scope.reverse == false){
        if($("#headRow").find(".sorting_asc").length>0){
           $("#headRow").find(".sorting_asc").removeClass("sorting_asc");
         }
         $('#'+propertyName).addClass('sorting_asc');
      } else if($scope.reverse == true){
         if($("#headRow").find(".sorting_desc").length>0){
           $("#headRow").find(".sorting_desc").removeClass("sorting_desc");
         }
         $('#'+propertyName).addClass('sorting_desc');

      }
   }

   this.openNav = function(){

      $("#side-menu").metisMenu();
   }

    this.openSideMenu = function(){
        $("body").toggleClass("mini-navbar");
        SmoothlyMenu();

        function SmoothlyMenu() {
            if (!$('body').hasClass('mini-navbar') || $('body').hasClass('body-small')) {
                // Hide menu in order to smoothly turn on when maximize menu
                $('#side-menu').hide();
                // For smoothly turn on menu
                setTimeout(
                    function () {
                        $('#side-menu').fadeIn(400);
                    }, 200);
            } else if ($('body').hasClass('fixed-sidebar')) {
                $('#side-menu').hide();
                setTimeout(
                    function () {
                        $('#side-menu').fadeIn(400);
                    }, 100);
            } else {
                // Remove all inline style from jquery fadeIn function to reset menu state
                $('#side-menu').removeAttr('style');
            }
        }
    }
   $scope.$on('ngRepeatFinished', function(ngRepeatFinishedEvent) {
   console.log('finished');
    $('.dataTables').DataTable({
                //pageLength: 10,
                responsive: true,
               // dom: '<"col-sm-4 col-md-4 p-a-0 m-t m-b-lg"B><"col-sm-4 col-md-4 p-a-0 m-t small text-muted text-center"i><"col-sm-4 col-md-4 p-a-0 m-t input-group-sm small"f>rt<"col-sm-6 col-md-6 p-a-0 m-t-md small input-group-sm"l><"col-sm-6 col-md-6 p-a-0 m-t-md small input-group-sm"p><"clear">',

//select: {
//            style: 'multi'
//        },
                buttons: [
                    {extend: 'copy', className: 'btn btn-default btn-sm', title: 'Copy'},
                    {extend: 'csv', className: 'btn btn-default btn-sm', title: 'CSV'},
                    {extend: 'excel', className: 'btn btn-default btn-sm', title: 'Excel'},
                    {extend: 'pdf', className: 'btn btn-default btn-sm', title: 'PDF'},
                    {extend: 'print', className: 'btn btn-default btn-sm', title: 'Print',
                     customize: function ($window){
                            $window.document.body.addClass('white-bg');
                            $window.document.body.css('font-size', '15px');

                            $window.document.body.find('table')
                                    .addClass('compact')
                                    .css('font-size', 'inherit');
                    	}
                    }
                ]

            });
       });

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
    this.userLogin = function() {
        $scope.showErr = false;
        $rootScope.checkReqValidation('loginForm');
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
              $scope.isDisabled = true;
            }
         });

        }
    }

    this.hideMessages = function($event){ /*Hide error messages when user interact with fieds*/
        if($event.keyCode !== 13 ){
          $scope.showErr = false;
          $scope.isDisabled = false;
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
}


function signupCtrl($scope, $rootScope, $state, $http, $window, $timeout,$cookies, $cookieStore, signupService) { /* signup controller responsible for signup form functionality */
    $scope.userRegistration = {};
    $scope.isDisabled = false;
    $scope.errorMessage = '';
    $scope.success = false;
    $scope.passwordStrength = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;  // password validation pattern
    $scope.emailPattern = /^[a-z]+[a-z0-9._]+@[a-z]+\.[a-z.]{2,5}$/;
                               // email pattern
    $scope.user_Signup = function() { /* signup function submitting user details to API*/
    $scope.errorMessage = '';
    $rootScope.checkReqValidation('signupForm');
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

    $scope.hideMessages = function($event){ /*Hide error messages when user interact with fieds*/
    if($event.keyCode !== 13 ){
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
}

function forgotCtrl($scope, $rootScope, $state, $http, forgotService) {
     $scope.isDisabled = false;
     $scope.errorMessage = '';
     $scope.isRequired = false;
     $scope.emailPattern = /^[a-z]+[a-z0-9._]+@[a-z]+\.[a-z.]{2,5}$/;
	/**Create function for forgot password **/
	$scope.forgotPassword = function() {
	   $scope.errorMessage = '';
	   $scope.isRequired = true;
        var requestObject = {
        	'email': $scope.user_email
        };
        if($scope.forgotForm.$valid){
            $scope.isRequired = false;
            $scope.isDisabled = true;
           forgotService.forgotPassword(requestObject).then(function(response){
             if(response.message == "success") {
                 $scope.user_email = '';
                 $scope.isDisabled = false;
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
    $scope.data = {};
    $scope.passwordStrength = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;
    $scope.changePassword = function(){
         $scope.isDisabled = true;
         var requestObject = {
        	'token': token,
        	'password': $scope.data.password
        };
       resetPasswordService.resetPassword(requestObject).then(function(response){
         if(response.message == "success") {
           $scope.data = {};
           $scope.successMsg = true;
           $scope.success = true;
         }else{
             $scope.data = {};
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


function createProjectCtrl($scope, $rootScope, $state, $http, $window, $stateParams, $cookies, $cookieStore, $location , $timeout, jobPostService, alchemyAnalysis, updateConcepts, publishProject){
     $scope.projectForm ={
        project_name :'',
        company_name :'',
        location :'',
        description:''
     };
    $rootScope.globals.currentProject_id = '';
    $scope.isProjMaxlength = false;
    $scope.isComMaxlength = false;
    $scope.isLocationMaxlength = false;
    $scope.isProjectnmValid = false;
    $scope.isProjectnmExists = false;
    $scope.isLastStepVisited = false;
    $scope.isError = false;
    $scope.isDescriptionError =false;
    $scope.apiErrorMsg = '';
    $scope.timeout;
    $scope.patternError = false;
    $scope.isFirstStepVisited = true;
    $scope.isSecondStepVisited = false;
    $scope.isthirdStepVisited = false;
    $scope.isLastStepVisited = false;
    $scope.locationPatternMsg = '';
    $rootScope.jobDescriptionResult = '';
    $rootScope.globals.projectDetails = [];
    this.projectNamePattern =/((^[ A-Za-z0-9_@./#-]*)|(^[a-zA-Z]+[_@./#-]*)|(^[0-9]+[a-z]+)|(^[a-z]+[0-9]+))+[0-9a-z]+$/i;// /^[a-z0-9]+$/i;


    $scope.checkMessage = function(){ /*Hide error messages when user interact with fieds*/
       $scope.isDescriptionRequired = false;
       $("#createProjectForm input").each(function(){
            var spanClass = $(this).next('span').attr('class');
            if($(this).val().length <= 0 && ($(this).next('span').hasClass('error'))){
                $(this).next('span').removeClass('error').text("");
            }else if($(this).val().length > 0 && ($(this).next('span').hasClass('error'))){
                $(this).next('span').removeClass('error').text("");
            }
        });
    }


    $scope.takeNext = function(currentState,prevTabId,currentTabId){  // next button view change functionality
        $scope.isProjectnmValid = false;
        $scope.isDescriptionRequired = false;
        $("#createProjectForm input").each(function(){ /*Show error on blank field when user submit*/
                var spanClass = $(this).next('span').attr('class');
                if($(this).val().length <= 0){
                    $(this).next('span').css('display','block');
                    $(this).next('span').addClass('error').text("Required.");
                }else if($(this).val().length > 0 && ($(this).next('span').hasClass('error'))){
                    $(this).next('span').removeClass('error').text("");
                }
        });
        if($scope.projectForm.project_name && $scope.projectForm.company_name && $scope.projectForm.location && !$scope.patternError)
              {
                var backButton = angular.element(document.querySelector('#previous'));
                    backButton.removeClass('disabled');
                    backButton.children(':first').removeClass('disable');
                if($("#tablist").find(".current").length>0){
                    $("#tablist").find(".current").addClass("done");
                    $("#tablist").find(".current").removeClass("current");
                }
                var currentTab = angular.element(document.querySelector(currentTabId));
                    if(currentTab.hasClass('done')){
                       currentTab.removeClass('done');
                    }
                  currentTab.removeClass('disabled');
                  currentTab.addClass('current');
                  $scope.isSecondStepVisited = true;
                  $state.go('create.step2','');
              }

    }

    $scope.takeToStepThree = function(currentState,prevTabId,currentTabId){
    if(!$scope.projectForm.description){
          $scope.isDescriptionRequired = true;

          }else if($scope.projectForm.description){
                 if(!$rootScope.jobDescriptionResult){
                   $(".loader").css('display','block');
                  }

             if($("#tablist").find(".current").length>0){
                    $("#tablist").find(".current").addClass("done");
                    $("#tablist").find(".current").removeClass("current");
                }
             var currentTab = angular.element(document.querySelector(currentTabId));
                if(currentTab.hasClass('done')){
                 currentTab.removeClass('done');
                 }
                 currentTab.removeClass('disabled');
                 currentTab.addClass('current');
                 $scope.isthirdStepVisited = true;
                 $state.go('create.step3','');
          }
    }

    $scope.takeToStepFour = function(currentState,prevTabId,currentTabId){
    if($rootScope.jobDescriptionResult.concept.length > 0){
        var nextButton = angular.element(document.querySelector('#next'));
            nextButton.css('display','none');
        var publishButton = angular.element(document.querySelector('#publish'));
            publishButton.removeClass('disabled');
            publishButton.children(':first').removeClass('disable');
        if($("#tablist").find(".current").length>0){
                $("#tablist").find(".current").addClass("done");
                $("#tablist").find(".current").removeClass("current");
            }
        var currentTab = angular.element(document.querySelector(currentTabId));
            if(currentTab.hasClass('done')){
            currentTab.removeClass('done');
            }
            currentTab.removeClass('disabled');
            currentTab.addClass('current');
            $scope.isLastStepVisited = true;
            $state.go('create.step4','');
      }else if($rootScope.jobDescriptionResult.concept.length == 0){
            $scope.isError = true;
            $scope.apiErrorMsg = 'There is no skills.';
      }
    }

    this.activateTab = function($event){
        var elementId = $event.target.id;
        console.log($event);
        var currentState = $state.current.name;
        var currentTabId;
        var prevTabId;
        var nextButton = angular.element(document.querySelector('#next'));
            nextButton.css('display','block');
        var publishButton = angular.element(document.querySelector('#publish'));
            publishButton.addClass('disabled');
            publishButton.children(':first').addClass('disable');
        if($scope.isFirstStepVisited && elementId == 'form-p-0'){
            if($("#tablist").find(".current").length>0){
                $("#tablist").find(".current").addClass("done");
                $("#tablist").find(".current").removeClass("current");
            }
            if($('#form-t-0').hasClass('done')){
               $('#form-t-0').removeClass('done');
            }
            $('#form-t-0').addClass('current');
            var prevButton = angular.element(document.querySelector('#previous'));
                prevButton.addClass('disabled');
                prevButton.children(':first').addClass('disable');
            $state.go('create.step1','');
        }
        if($scope.isSecondStepVisited && elementId == 'form-p-1'){
           angular.element($event.target).removeAttr('style');
           currentTabId = '#form-t-1';
           prevTabId = '';
           $scope.takeNext(currentState,prevTabId,currentTabId);
        }
        if($scope.isthirdStepVisited && elementId == 'form-p-2'){
           angular.element($event.target).removeAttr('style');
           currentTabId = '#form-t-2';
           prevTabId = '';
           var backButton = angular.element(document.querySelector('#previous'));
            backButton.removeClass('disabled');
            backButton.children(':first').removeClass('disable');
           $scope.takeToStepThree(currentState,prevTabId,currentTabId);
        }
        if($scope.isLastStepVisited && elementId == 'form-p-3'){
           angular.element($event.target).removeAttr('style');
           currentTabId = '#form-t-3';
           prevTabId = '';
           var backButton = angular.element(document.querySelector('#previous'));
            backButton.removeClass('disabled');
            backButton.children(':first').removeClass('disable');
           $scope.takeToStepFour(currentState,prevTabId,currentTabId);
        }
    }


     $scope.SwitchFuction = function () {   // generic function which call different stepwise function
      var currentState = $state.current.name;
      var prevTabId;
      var currentTabId;
        switch (currentState) {
            case 'create.step1':
                prevTabId = '#form-t-0';
                currentTabId = '#form-t-1';
                $scope.takeNext(currentState,prevTabId,currentTabId);
                break;
            case 'create.step2':
                prevTabId = '#form-t-1';
                currentTabId = '#form-t-2';
                $scope.takeToStepThree(currentState,prevTabId,currentTabId);
                break;
            case 'create.step3':
                prevTabId = '#form-t-2';
                currentTabId = '#form-t-3';
                $scope.isDescriptionError = false;
                $scope.takeToStepFour(currentState,prevTabId,currentTabId);
                break;
        }

     }

    $scope.takeBack = function(currentState,prevTabId,currentTabId){
        var prevTab = angular.element(document.querySelector(prevTabId));
        var publishButton = angular.element(document.querySelector('#publish'));
            publishButton.addClass('disabled');
            publishButton.children(':first').addClass('disable');
            prevTab.addClass('current');
            prevTab.removeClass('done');
        var currentTab = angular.element(document.querySelector(currentTabId));
            currentTab.addClass('done');
        if(currentState == "create.step2"){
              $scope.isDescriptionRequired = false;
              var prevButton = angular.element(document.querySelector('#previous'));
                  prevButton.addClass('disabled');
                  prevButton.children(':first').addClass('disable');
              $state.go('create.step1','');
        }else if(currentState == "create.step3"){
              $scope.isError = false;
              $scope.apiErrorMsg = '';
              $state.go('create.step2','');
        }else if(currentState == "create.step4"){
              var nextButton = angular.element(document.querySelector('#next'));
              nextButton.css('display','block');
              $state.go('create.step3','');
        }
    }

    $scope.goToBack = function () {
    var currentState = $state.current.name;
    switch (currentState) {
        case 'create.step2':
            prevTabId = '#form-t-0';
            currentTabId = '#form-t-1';
            $scope.takeBack(currentState,prevTabId,currentTabId);
            break;
        case 'create.step3':
            prevTabId = '#form-t-1';
            currentTabId = '#form-t-2';
            $scope.takeBack(currentState,prevTabId,currentTabId);
            break;
        case 'create.step4':
            prevTabId = '#form-t-2';
            currentTabId = '#form-t-3';
            $scope.takeBack(currentState,prevTabId,currentTabId);
            break;
        }

    }


    $scope.removeValidationMsg = function($event){
         $scope.isProjectnmValid = false;
         $scope.isProjectnmExists = false;
    }

    $scope.checkProjectName = function($event){
    if($event.target.name == "company_name" || "location"){   // if projectName is blank prompt for it
        $scope.checkMessage();
        var element = angular.element(document.querySelector('#project_name'));
          if(element && !element[0].value ){
                $scope.isProjectnmValid = true;
                element[0].focus();
                $event.preventDefault();
              }
       }
    }

    $scope.updateProjectName = function($event){
    if($event.target.value != ''){
    var projectName = $event.target.value;
    var is_published = false;
    var token = $rootScope.globals.currentUser.token;
    var recruiter = $rootScope.globals.currentUser.user_email;
    var requestObject = {};
       requestObject["id"] = $rootScope.globals.currentProject_id;
       requestObject["project_name"] = projectName;
       requestObject["token"] = token;
       requestObject["recruiter"] = recruiter;
       requestObject["is_published"] = is_published;
          jobPostService.jobPost(requestObject).then(function(response){
                 if(response.message == "success") {
                   if( $rootScope.globals.currentProject_id == '')
                     $rootScope.globals.currentProject_id = response.project_id;
                        var ProjectData = [];
                        var valueObj = {'key':'project_id','value':$rootScope.globals.currentProject_id};
                            ProjectData.push(valueObj);
                            valueObj = {'key':'project_name','value':projectName};
                            ProjectData.push(valueObj);
                           $cookies.put('currentProjectId',JSON.stringify(ProjectData));
                 }else{
                       if(response.errorstring){
                         $scope.isProjectnmExists = true;
                       }
                 }
          });
        }
    }

    $scope.validateLocation = function(value){
        $scope.patternError = false;
        var zip = /^(?!0{5})\d{5}$/;
        var city = /((^[ A-Za-z-]*)|(^[a-zA-Z]+[-]*)|(^[0-9]+[a-z]+)|(^[a-z]+[0-9]+))+[0-9a-z]$/i;
    if(!isNaN(value) && value)
     {
       if(!zip.test(value)){
          $scope.patternError = true;
          $scope.locationPatternMsg = 'Enter 5 digit zipcode!';
       }
     }
     else if(value){
        if(!city.test(value)){
           $scope.patternError = true;
           $scope.locationPatternMsg = 'Enter valid city name!';
        }
     }
    }

    $scope.saveData = function(name,value){
     if(value){
          $timeout(saveUpdates(name,value), 2000);  // 2000 = 2 second
        }

    }

    var saveUpdates = function(name , value){
       var is_published = false;
       var token = $rootScope.globals.currentUser.token;
       var recruiter = $rootScope.globals.currentUser.user_email;
       var requestObject = {};
           requestObject["id"] = $rootScope.globals.currentProject_id;
           requestObject[name] = value;
           requestObject["token"] = token;
           requestObject["recruiter"] = recruiter;
           requestObject["is_published"] = is_published;
          jobPostService.jobPost(requestObject).then(function(response){
                 if(response.message == "success") {
                   if ($scope.timeout) {
                            $timeout.cancel($scope.timeout)
                       }
                 }else{
                         $scope.timeout = $timeout(saveUpdates(name,value), 3000);
                 }
            });
    }

    $scope.updateJobDescription = function($event){
    if($event.target.value){
    $rootScope.jobDescriptionResult = '';
    $scope.isDescriptionError = false;
    $scope.apiErrorMsg = '';
    var is_published = false;
    var token = $rootScope.globals.currentUser.token;
    var recruiter = $rootScope.globals.currentUser.user_email;
    var requestObject = {};
           requestObject["id"] = $rootScope.globals.currentProject_id;
           requestObject[$event.target.name] = $event.target.value;
           requestObject["token"] = token;
           requestObject["recruiter"] = recruiter;
           requestObject["is_published"] = is_published;
         alchemyAnalysis.alchemyAPI(requestObject).then(function(response){
                 if(response.message == "success") {
                    $rootScope.jobDescriptionResult = response;
                    if($rootScope.jobDescriptionResult.concept.length == 0){
                      $scope.isDescriptionError = true;
                      $scope.apiErrorMsg = "There is no relevant keywords in your description.";
                    }

                     $(".loader").css('display','none');

                 }else{
                       if(response.errorstring){
                           $scope.isDescriptionError = true;
                           $scope.apiErrorMsg = "Description text data is not valid.";
                        }
                          $(".loader").css('display','none');
                        console.log('error');
                 }
            });
        }

    }

  var validateSkillName = function(skillName) {
        var re =/(^[a-zA-Z_. -][a-zA-Z0-9_. -]{1,50})+$/;
        return re.test(skillName);
  }

  $scope.updateSkillView = function($event){
      $scope.isDescriptionError = false;
      $scope.apiErrorMsg = '';
      if($event.target.value){
        var skill = $event.target.value;
          if(skill.length<2){
               $scope.isDescriptionError = true;
               $scope.apiErrorMsg = 'Please provide atleast 2 character!';
             }
              else if(!validateSkillName(skill)){
                 $scope.isDescriptionError = true;
                 $scope.apiErrorMsg ='First letter sholud be a character!' ;
               }else{
                   var newSkill = $event.target.value;
                   var index = $rootScope.jobDescriptionResult.concept.indexOf(newSkill);
                       if(index == -1){
                            $rootScope.jobDescriptionResult.concept.push(newSkill);
                       }else{
                            $scope.isDescriptionError = true;
                            $scope.apiErrorMsg = 'Already exists!';
                       }
                          $event.target.value = '';
                          $scope.updateSkillSet();
                 }
         }
  }

   $scope.updateSkillSet = function(){
      var is_published = false;
      var token = $rootScope.globals.currentUser.token;
      var recruiter = $rootScope.globals.currentUser.user_email;
      var requestObject = {};
           requestObject["id"] = $rootScope.globals.currentProject_id;
           requestObject["concept"] = $rootScope.jobDescriptionResult.concept;
           requestObject["token"] = token;
           requestObject["recruiter"] = recruiter;
           requestObject["is_published"] = is_published;
           updateConcepts.conceptsAPI(requestObject).then(function(response){
                 if(response.message == "success") {
                         console.log(response);
                 }else{
                        console.log('error');
                 }
            });

   }

    $scope.publishProject = function(){
        if( $state.current.name == 'create.step4'){
        $scope.isSuccess = false;
        $scope.publishMsg = '';
        $(".loader").css('display','block');
        var is_published = true;
        var token = $rootScope.globals.currentUser.token;
        var recruiter = $rootScope.globals.currentUser.user_email;
        var requestObject = {};
        requestObject["id"] = $rootScope.globals.currentProject_id;
        requestObject["token"] = token;
        requestObject["recruiter"] = recruiter;
        requestObject["is_published"] = is_published;
        publishProject.publish(requestObject).then(function(response){
             if(response.message == "success") {
                $(".loader").css('display','none');
                $scope.publishMsg = "Project created successfully.";
                  $('#breakPopup').css('display','block');
                $timeout( function(){
                $('#breakPopup').css('display','none');
                $state.go('dashboard','');} , 3000);

             }else{
                $(".loader").css('display','none');
                  $scope.isSuccess = true;
                $scope.publishMsg = "Please try again.";
                $('#breakPopup').css('display','block');
                    console.log('error');
             }
        });
         $timeout( function(){$(".loader").css('display','none');
                  $scope.isSuccess = true;
                $scope.publishMsg = "Please try again.";
                $('#breakPopup').css('display','block');} , 30000); //timeout after three minutes
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
