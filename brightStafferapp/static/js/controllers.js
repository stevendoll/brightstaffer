
function MainCtrl($scope, $rootScope, $location, $http, $cookies, $cookieStore, getTopSixProjects, getAllProjects, paginationData,$window,$state,$timeout,$stateParams, $uibModal ) { /*global controller */
    $rootScope.topSixProjectList = [];   // top six project list array
    $rootScope.allProjectList = [];          // all project array
    $rootScope.totalProjectCount =0;
    $rootScope.projectCountStart = 1;
    $rootScope.projectCountEnd = 0;
    $rootScope.paginationCounter= 1;
    $scope.stateArray = ['projects','create.step1','create.step2','create.step3','create.step4'];
    $rootScope.isDevice = false;
    $rootScope.projectListView = [{name:'Select Project',value:'Select Project'},{name:'Search Project',value:'Search Project'}];

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
        $rootScope.paginationCounter = 1;
        var count = 10;
        if($rootScope.countList){
            count=$rootScope.countList.value;
         }
         $('html, body').animate({ scrollTop: 0 }, 'fast');
          var requestObject = {
            'token': $rootScope.globals.currentUser.token,       // username field value
            'recruiter': $rootScope.globals.currentUser.user_email,
            'count':count                                    // password filed value
         };
         getAllProjects.allProjects(requestObject).then(function(response){
            if(response.message == "success") {
                    var nextButton = document.getElementById('Table_next');
                    nextButton = angular.element(nextButton);
                    var prevButton = document.getElementById('Table_previous');
                    prevButton = angular.element(prevButton);
                     $rootScope.totalProjectCount = response.count;
                     $rootScope.allProjectList = response.published_projects;
                     for(var i=0;i<$rootScope.allProjectList.length;i++){
                         var project = {name:$rootScope.allProjectList[i].project_name,
                                        value:$rootScope.allProjectList[i].id};
                            $rootScope.projectListView.push(project);
                         }
                     $rootScope.projectCountEnd = response.published_projects.length;
                     $rootScope.projectNext = response.next;
                     $rootScope.projectPrevious = response.previous;
                     if($rootScope.projectNext != null){
                          nextButton.removeClass('disabled');
                          nextButton.parent().removeClass('disabled');
                         }
                     if($rootScope.projectPrevious != null){
                        prevButton.removeClass('disabled');
                        prevButton.parent().removeClass('disabled');
                     }
            }else{
                console.log('error');
            }
        });
    }


   this.removePopupBox = function(){
        $('#breakPopup').css('display','none');
        $rootScope.isSuccess = false;
   }

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
        var value = document.getElementById('emailInput').value;
        if(!value)
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

function topnavCtrl($scope, $rootScope, $state, $http, $window, $stateParams, $cookies, $cookieStore, $location, searchApis ){
    $scope.searchKeywords = '';
    this.logout = function(){
          $cookieStore.remove('userData');
          $rootScope.globals = {};
          $state.go('login','');
    }

    this.getSearchData = function(){
    console.log($scope.searchKeywords);
      if($scope.searchKeywords){
         var requestObject = {
            'keyword':$scope.searchKeywords
             };
             searchApis.talentSearch(requestObject).then(function(response){
                if(response.message == "success") {
                    console.log(response);
                  }else{
                    console.log('error');
                }
             });
      }
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
                var mainUl = angular.element(document.querySelector('#projectBtns'));
                    if(mainUl.hasClass('twobtn')){
                       mainUl.removeClass('twobtn');
                    }
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
        }
        else if($scope.projectForm.description){
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
             var mainUl = angular.element(document.querySelector('#projectBtns'));
                    if(mainUl.hasClass('twobtn')){
                       mainUl.removeClass('twobtn');
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
        var mainUl = angular.element(document.querySelector('#projectBtns'));
            mainUl.addClass('twobtn');
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
            $scope.isDescriptionError = true;
            $scope.apiErrorMsg = 'Required.';
      }
    }

    this.activateTab = function($event){
        var elementId = $event.target.id;
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
              var mainUl = angular.element(document.querySelector('#projectBtns'));
                if(mainUl.hasClass('twobtn')){
                   mainUl.removeClass('twobtn');
                }
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
            },function(error){
                 if(error){
                     $scope.timeout = $timeout(saveUpdates(name,value), 1000);
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
                          if($rootScope.jobDescriptionResult == ''){
                             $rootScope.jobDescriptionResult = {};
                             $rootScope.jobDescriptionResult.concept = [];
                          }
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
                 $scope.apiErrorMsg ='Input should contain first letter as character and allowed special characters are (. - _).';
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
        $scope.isPublish = false;
        $(".loader").css('display','block');
        var is_published = true;
        $scope.isPublish = false;
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
               // $scope.publishMsg = "Project created successfully.";
                 $scope.isPublish = true;
                  $state.go('dashboard','');
             }else{
                $(".loader").css('display','none');
                  $scope.isSuccess = true;
                $scope.publishMsg = "Please try again.";
                $('#breakPopup').css('display','block');
                    console.log('error');
             }
        });
         $timeout( function(){
                 if( $scope.isPublish == false){
                 $(".loader").css('display','none');
                  $scope.isSuccess = true;
                $scope.publishMsg = "Please try again.";
                $('#breakPopup').css('display','block');}
                } , 30000); //timeout after three minutes
         }
    }

    $scope.gotoTop = function(){
        $('html, body').animate({ scrollTop: 0 }, 'fast');
    }
}


function tableCtrl($scope, $rootScope, $location, $http, $cookies, $cookieStore, getTopSixProjects, getAllProjects, paginationData,$window,$state,$timeout) { /*global controller */
    $scope.options = [{name:'10',value:10},{name:'25',value:25},{name:'50',value:50},{name:'100',value:100}]; // select drop-down options
    $rootScope.countList = $scope.options[0];
    $scope.hidenData = {};
    $scope.popupMsg = '';
    $scope.apiHit = false;

    this.setButton = function(){
        var nextButton = angular.element(document.querySelector('#Table_next'));
        var prevButton = angular.element(document.querySelector('#Table_previous'));
        if($rootScope.projectNext != null){
          nextButton.removeClass('disabled');
          nextButton.parent().removeClass('disabled');
         }
         if($rootScope.projectPrevious != null){
            prevButton.removeClass('disabled');
            prevButton.parent().removeClass('disabled');
         }
    }

    this.getValue = function(countList){    //record count change functionality in all project list view
        var nextButton = angular.element(document.querySelector('#Table_next'));
        var prevButton = angular.element(document.querySelector('#Table_previous'));
        $(".loader").css('display','block');
        var requestObject = {
                'token': $rootScope.globals.currentUser.token,       // username field value
                'recruiter': $rootScope.globals.currentUser.user_email,   // password filed value
                'count':countList.value
             };
             getAllProjects.allProjects(requestObject).then(function(response){
                $scope.apiHit = true;
                if(response.message == "success") {
                    if(response.published_projects.length > 0)
                       $rootScope.allProjectList = response.published_projects;

                       $rootScope.projectCountEnd = response.published_projects.length;
                       $rootScope.projectNext = response.next;
                       $rootScope.projectPrevious = response.previous;
                        if($rootScope.projectNext == null){
                          nextButton.addClass('disabled');
                          nextButton.parent().addClass('disabled');
                         }else{
                            if(nextButton.hasClass('disabled')){
                             nextButton.removeClass('disabled');
                             nextButton.parent().removeClass('disabled');
                            }

                         }
                         if($rootScope.projectPrevious == null){
                            prevButton.addClass('disabled');
                            prevButton.parent().addClass('disabled');
                         }
                       $(".loader").css('display','none');
                  }else{
                    console.log('error');
                    $(".loader").css('display','none');
                      if(response.success == false){
                            $rootScope.isSuccess = true;
                            $scope.popupMsg = "No data available.";
                            $('#breakPopup').css('display','block');
                      }
                }
             });
    }

    this.changePage = function($event){                  // pagination with previous and next button event handler
     $rootScope.isSuccess = false;
     var url = '';
     $scope.popupMsg = '';
     var nextButton = angular.element(document.querySelector('#Table_next'));
     var prevButton = angular.element(document.querySelector('#Table_previous'));
         if($event.target.name == "next"){
           $rootScope.paginationCounter++;
           $('#countDropdown').css('display','none');
            url = $rootScope.projectNext;
         }else if($event.target.name == "prev"){
               if($rootScope.paginationCounter >1){
                    $rootScope.paginationCounter--;
                    if($rootScope.paginationCounter ==1)
                    {
                      $('#countDropdown').css('display','');
                    }
                  }
                url = $rootScope.projectPrevious;
         }
         $(".loader").css('display','block');
         var requestObject = {
              'url': url
             };
         paginationData.paginationApi(requestObject).then(function(response){
             $scope.apiHit = true;
                if(response.message == "success") {
                    if(response.published_projects.length > 0)
                       $rootScope.allProjectList = response.published_projects;
                       $rootScope.projectNext = response.next;
                       $rootScope.projectPrevious = response.previous;
                       if($event.target.name == "next"){
                       $rootScope.projectCountStart =  $rootScope.projectCountEnd +1;
                       $rootScope.projectCountEnd = $rootScope.projectCountEnd + response.published_projects.length;
                       }else if($event.target.name == "prev"){
                       $rootScope.projectCountStart = $rootScope.projectCountStart -response.published_projects.length;
                       if($rootScope.projectCountStart <= 0)
                          $rootScope.projectCountStart = 1;
                       $rootScope.projectCountEnd = $rootScope.projectCountStart + response.published_projects.length -1;
                       if($rootScope.projectCountEnd <10)
                         $rootScope.projectCountEnd = 10 ;
                       }
                       if($rootScope.projectNext == null){
                          nextButton.addClass('disabled');
                          nextButton.parent().addClass('disabled');
                         }else{
                            if(nextButton.hasClass('disabled')){
                              nextButton.removeClass('disabled');
                              nextButton.parent().removeClass('disabled');
                            }
                         }
                         if($rootScope.projectPrevious == null){
                            prevButton.addClass('disabled');
                            prevButton.parent().addClass('disabled');
                         }else{
                             if(prevButton.hasClass('disabled')){
                             prevButton.removeClass('disabled');
                             prevButton.parent().removeClass('disabled');
                             }
                         }
                   $(".loader").css('display','none');
                  }else{
                    $(".loader").css('display','none');
                    if(response.success == false){
                        if($event.target.name == "next"){
                           nextButton.addClass('disabled');
                           $rootScope.paginationCounter--;
                           if($rootScope.paginationCounter == 1){
                                 prevButton.addClass('disabled');
                           }
                           $scope.tableNext = false;
                        }
                        $rootScope.isSuccess = true;
                        $scope.popupMsg = "No data available.";
                        $('#breakPopup').css('display','block');

                    }
                }
           });
    }

    $scope.$on('ngRepeatFinished', function(ngRepeatFinishedEvent) {    // table responsiveness initialization after data render
      $timeout(function () {
             tableInitialise();
          },1000);
        if(navigator.userAgent.match(/iPhone/i)){
             $('.buttons-excel').css('display','none');
            }
       });

   var update_size = function() {
        $('.dataTables').css({ width: $('.dataTables').parent().width() });
        if($scope.apiHit){
         tableInitialise();
          }
   };

    $(window).resize(function() {       // on window resize table resize for responsiveness
        clearTimeout(window.refresh_size);
        window.refresh_size = setTimeout(function() { update_size(); }, 250);
    });

    var tableInitialise = function(){
           $scope.hidenData = {};
          var table = $('.dataTables').DataTable({
                responsive: true,
                retrieve: true,
                paging: true,
                autoWidth: false,
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
          showHideColumn();
    }
    var showHideColumn = function(){        // on table responsiveness show and hide column value
    var tableHead = document.getElementsByTagName('th');
    var displayRows = $(".dataTables").find("tbody>tr");
     angular.forEach(tableHead, function(th)
     {
      var columnIndex = th.cellIndex;
        if(th.style['display'] == "none")
        {
         for(var currentRow =0; currentRow < displayRows.length; currentRow++)
         {
          if($scope.hidenData[currentRow])
          {
                 $scope.hidenData[currentRow] = $scope.hidenData[currentRow];
          }else
          {
                $scope.hidenData[currentRow]=[];
          }
             var data = {};
                 data["title"] = th.innerText;
                 data["index"] = columnIndex;
            if(currentRow !=0 && currentRow%2 == 0)
            {
               $(displayRows[currentRow]).addClass('even');
            }else
             {
                $(displayRows[currentRow]).addClass('odd');
             }
            $(displayRows[currentRow]).find("td:eq(0)").addClass("sorting_1");
            $(displayRows[currentRow]).find("td:eq("+columnIndex+")").css('display','none');
            data["value"] = $(displayRows[currentRow]).find("td:eq("+columnIndex+")").text();
            $scope.hidenData[currentRow].push(data);
          }
       }
        else {
            for(var currentRow =0; currentRow < displayRows.length; currentRow++)
             {
                $(displayRows[currentRow]).find("td:eq(0)").addClass("sorting_1");
                $(displayRows[currentRow]).find("td:eq("+columnIndex+")").css('display','');
             }

        }
     });
   }

    $scope.showChild = function($event,row){
        if($($event.target.parentElement).hasClass('parent')){
           $($event.target.parentElement).css("background-color",'#ffffff');
        }else{
           $($event.target.parentElement).css("background-color",'#f5f5f5');
        }
        if($scope.apiHit){
            if($($event.target.parentElement).hasClass('parent')){
                  $($event.target.parentElement).removeClass('parent');
                   $($event.target.parentElement).css("background-color",'#ffffff');
                  angular.element($('#'+row)).remove();
            }
            else{
                $($event.target.parentElement).addClass('parent');

                 var childEle = '<tr class="child" id="'+row+'"><td class="child" colspan="7"><ul data-dtr-index="7">';
                  for(var i=0;i<$scope.hidenData[row].length;i++){
                     childEle = childEle+'<li data-dtr-index="'+$scope.hidenData[row][i].index+'"><span class="dtr-title">'+$scope.hidenData[row][i].title+'</span><span class="dtr-data">'+$scope.hidenData[row][i].value+'</span></li>';
                  }
                childEle = childEle+'</ul></td></tr>';
                angular.element($event.target.parentElement).after(childEle);
                $($event.target.parentElement).css("background-color",'#f5f5f5');
            }
        }
    }

}

function scoreCardCtrl($scope, $rootScope, $location, $http, $cookies, $cookieStore,$window,$state,$timeout, $uibModal) {
    this.analysedData = [
        {   "key":"analysedData",
            "values": [[6,5],[7,11],[8,6],[9,11],[10,30],[11,10],[12,13],[13,4],[14,3],[15,3],[16,6]]
        }];

    this.activeCardData = [
        {   "key":"activeCardData",
            "values": [[6,1],[7,5],[8,2],[9,3],[10,2],[11,1],[12,0],[13,2],[14,8],[15,0],[16,0]]
        }];

    this.interviewCardData = [
        {   "key":"interviewCardData",
            "values": [[4,1],[8,3],[12,1],[16,5],[20,2],[24,3],[28,2]]
        }];

    this.fourthCardData = [
        {   "key":"fourthCardData",
            "values": [[3,0],[8,1],[13,0],[18,2],[28,8],[38,0],[56,0]]
        }];

    $scope.xAxisTicksFunction = function(){
        console.log('xAxisTicksFunction');
        console.log(d3.svg.axis().ticks(d3.time.minutes, 5));
        return function(d){
            return d3.svg.axis().ticks(d3.time.minutes, 5);
        }
    };

    $scope.xAxisTickFormatFunction = function(){
        console.log('xAxisTicksFunction');
        return function(d){
            return d3.time.format('%H:%M')(moment.unix(d).toDate());
        }
    };

    $scope.colorFunction = function() {
        return function(d, i) {
            return 'rgb(255, 255, 255)'
        };
    }

    $scope.resetModal = function(){
        var doneButton = document.getElementById('done');
        doneButton.classList.add('disabled');
        doneButton.classList.add('talent-modal-done');
        doneButton.classList.remove('talent-modal-add');
        doneButton.style['pointer-events'] = 'none';
        document.getElementById('backgroundImg').style.display= '';
    }

}

function uploadFileCtrl($scope, $rootScope, $location, $http, $cookies, $cookieStore,$window,$state,$timeout){
    $scope.validMimeTypes=['application/vnd.openxmlformats-officedocument.wordprocessingml.document' , 'application/msword', 'application/pdf'];
    $rootScope.attachedFilesData=[];
    $scope.FilesList =[];
    $scope.countError = false;
    $scope.fileCountExceededMsg = '';
    $scope.isDisabled = true;
    $scope.noFile = false;
    $scope.completedFiles = [];

      $scope.filesExits= function() {
      var fileContainers = document.getElementsByClassName('dz-preview');
       for(var i=0;i<fileContainers.length;i++){
            if(fileContainers[i].classList.contains('dz-error') || !fileContainers[i].classList.contains('dz-complete')){
                return true;
            }

        }
          return false;
      }

    $scope.closePopup = function(){
     var file = $scope.filesExits();
        if(file){
            $('#add-talent').modal('hide');
            $('#delete-popup').modal('show');
        }else{
            $scope.removeCompletedFiles();
            $('#add-talent').modal('hide');
        }
    }

    $scope.closeForcefully = function(){
        $scope.removeCompletedFiles();
        $('#delete-popup').modal('hide');
    }

    $scope.done = function(){
        $('#add-talent').modal('hide');
        $('#successBox').css('display','block');
        $scope.removeCompletedFiles();
        setTimeout(
        function () {
            $('#successBox').css('display','none');
        }, 2000);
    }

    $scope.reopen = function(){
        $('#delete-popup').modal('hide');
        $('#add-talent').modal('show');
    }

    var dropzoneId = "dropzone";

    window.addEventListener("dragenter", function(e) {
      if (e.target.id != dropzoneId) {
        e.preventDefault();
        e.dataTransfer.effectAllowed = "none";
        e.dataTransfer.dropEffect = "none";
      }
    }, false);

    window.addEventListener("dragover", function(e) {
      if (e.target.id != dropzoneId) {
        e.preventDefault();
        e.dataTransfer.effectAllowed = "none";
        e.dataTransfer.dropEffect = "none";
      }
    });

    window.addEventListener("drop", function(e) {
      if (e.target.id != dropzoneId) {
        e.preventDefault();
        e.dataTransfer.effectAllowed = "none";
        e.dataTransfer.dropEffect = "none";
      }
    });

}


function sideNavCtrl($scope, $rootScope, $location, $http, $cookies, $cookieStore, $window, $state, $timeout){
     this.detectmob = function($event){
        if( navigator.userAgent.match(/Android/i)
        || navigator.userAgent.match(/webOS/i)
        || navigator.userAgent.match(/iPhone/i)
        || navigator.userAgent.match(/iPod/i)
        || navigator.userAgent.match(/BlackBerry/i)
        || navigator.userAgent.match(/Windows Phone/i)
         ){
            openSideMenu();
         }
    }

    function openSideMenu(){
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

    $scope.setActive = function($event){
        $event.stopPropagation();
        var childEle = $('.nav-first-level').children('.ch');
        angular.forEach(childEle, function(li) {
          if(!li.contains($event.target)){
             if($event.currentTarget.id != "project" && $('.nav-second-level').hasClass('in')){
                 $('.nav-second-level').removeClass('in');
                  $('.nav-second-level').css('display','');
               }
               angular.element(li).removeClass('active');
             }
        });

        if($event.type == "touchstart"){
            if($($event.currentTarget).hasClass('active')){
                $($event.currentTarget).removeClass('active');
               }
            else{
                $($event.currentTarget).addClass('active');
                   if($event.currentTarget.id == "project"){
                     $('.nav-second-level').addClass('in');
                      $('.nav-second-level').css('display','block');
                 }
            }
        }else if($event.type == "click"){
            if($(this).hasClass('active')){
                $(this).removeClass('active');
            }
            else{
               $(this).addClass('active');
               }
        }
    }

    $scope.stateSelected = function(){
        if($scope.stateArray.indexOf($state.current.name)> -1 && !$rootScope.isDevice){
          $('#project').addClass('active');
           $('.nav-second-level').addClass('in');
             $('.nav-second-level').css('display','block');
           return true;
        }
        if($scope.stateArray.indexOf($state.current.name)> -1 && $rootScope.isDevice){
            $('#project').addClass('highlight');
             return true;
        }
      return false;
    }

}

function talentCtrl($scope, $rootScope, $location, $http, $cookies, $cookieStore,$window,$state,$timeout, talentApis , $uibModal){
     $scope.exportOptions = [{name:'Export Data',value:'Export Data'},{name:'Copy',value:'Copy'},{name:'CSV',value:'CSV'},{name:'Excel',value:'Excel'},{name:'PDF',value:'PDF'},{name:'Print',value:'Print'}]; // select drop-down options
     $scope.recordOptions = [{name:'10',value:'10'},{name:'20',value:'20'},{name:'30',value:'30'},{name:'40',value:'40'},{name:'50',value:'50'}]// select drop-down options
     $scope.exportType = $scope.exportOptions[0];
     $scope.recordCount = $scope.recordOptions[0];
     $scope.talentList = [];
     $scope.recruiter ={};
     $rootScope.talentDetails = {};
     $scope.selectedCandidate = {};
     $scope.choosenCandidates = [];
     $scope.currentTalentId = '';
     $scope.projectDD = $rootScope.projectListView[0];
     $scope.talentCountStart = 1;
     $scope.talentCountEnd = 0;
     $scope.totalTalentCount = 0;
     $scope.rating = 0;
     $scope.isEmailEditable = false;
     $scope.isEmailAdd = false;
     $scope.isContactEditable = false;
     $scope.isContactAdd = false;
     $scope.recruiterNameInput = '';
     $scope.isName = false;

     $scope.$on('ngRepeatFinished', function(ngRepeatFinishedEvent) {    // table responsiveness initialization after data render
          $(".select-arrow").selectbox();
          $('#export').change(function() {
                var selectedValue = $('#export :selected').text();
                $scope.exportType = selectedValue;
            });
          $('#recordCount').change(function() {
                var selectedValue = $('#recordCount :selected').text();
                $scope.recordCount = selectedValue;
                $scope.getTalents($scope.recordCount);
            });
          $('#projectListD').change(function() {
            var selectedValue = $('#projectListD :selected').text();
            $scope.projectDD = selectedValue;
            console.log($scope.projectDD);
            });
        // var oldie = $.browser.msie && $.browser.version < 9;

       });

      angular.element(document).ready(function () {
            $scope.getTalents();
       });

    $scope.getSelectedRating = function (rating) {
        console.log(rating);
        console.log($rootScope.talentDetails.id);
        if(rating){
            var requestObject = {
            'id':$rootScope.talentDetails.id,   // password field value
            'rating': rating
             };
         talentApis.updateRatings(requestObject).then(function(response){
            if(response.message == "success") {
              console.log(response);
              }else{
                console.log('error');
            }
         });
       }
    }

      $scope.changeState = function(){
        $scope.choosenCandidates =[];
        $('#selectall').prop('checked',false);
        $('#assignToProject').removeClass('add-talent');
        $('#assignToProject').addClass('disabled-talent');
       var currentState = $state.current.name;
        if(currentState == 'talent.talent-search.talent-search-card'){
          $('.bar-view').removeClass('active');
          $('.table-view').addClass('active');
          $state.go('talent.talent-search.talent-search-list','');
        }

        if(currentState == 'talent.talent-search.talent-search-list'){
          $('.bar-view').addClass('active');
          $('.table-view').removeClass('active');
          $state.go('talent.talent-search.talent-search-card','');
        }
      }

      $scope.getTalents = function(recordCount){             // function to fetch top 6 projects
        if(recordCount){
          var count = recordCount;
        }else{
          var count = $scope.recordCount.value;
        }
        var requestObject = {
        'token': $rootScope.globals.currentUser.token,       // username field value
        'recruiter': $rootScope.globals.currentUser.user_email,   // password field value
        'count': count
         };
         talentApis.getAllTalents(requestObject).then(function(response){
            if(response.message == "success") {
              $scope.talentList = response.talent_list;
              $scope.recruiter.recruiterName = response.display_name;
              $scope.totalTalentCount = response.count;
              $scope.talentCountEnd = response.talent_list.length;
              }else{
                console.log('error');
            }
         });
      }

      $scope.updateRecruiterName = function(name){             // function to fetch top 6 projects
       console.log(name);
       if(name){
            $scope.recruiter.recruiterName = name;
            $('#nameUpdate').addClass('disabled');
            $('#nameUpdate').css('pointer-events','none');
            var requestObject = {
            'recruiter': $rootScope.globals.currentUser.user_email,   // password field value
            'display_name': $scope.recruiter.recruiterName
             };
             talentApis.updateRecruiterName(requestObject).then(function(response){
                if(response.message == "success") {
                  console.log(response);
                 $('#edit-recruiter').modal('hide');
                 $('#nameSuccess').css('display','block');
                 setTimeout(
                        function () {
                            $('#nameSuccess').css('display','none');
                        }, 2000);
                  }else{
                    console.log('error');
                }
             });
         }else{
            $('#name-required').removeClass('ng-hide');
             $scope.isName = true;
         }
      }

      $scope.selectExportType = function(exportType){
      console.log('asdasdasdasd');
        console.log(exportType.value);
      }

      $scope.calcTotal = function(filtered){
         var sum = 0;
         for(var i = 0 ; i<filtered.length ; i++){
            sum = sum + Math.round(filtered[i].years_of_experience * 100)/100;
            sum = sum + Math.round(filtered[i].career_gap * 100)/100;
         }
         return sum;
     };

     $scope.loadProfileData = function(id, talent){
        if(Object.keys($rootScope.talentDetails).length == 0){
             $rootScope.talentDetails = talent;
        }
        var requestObject = {
        'token': $rootScope.globals.currentUser.token,       // username field value
        'recruiter': $rootScope.globals.currentUser.user_email,   // password field value
        'id': id
         };
         talentApis.getCandidateProfile(requestObject).then(function(response){
              $rootScope.talentDetails = response;

         });

     }

    $scope.showDetails = function(talent){
      $scope.selectedCandidate = talent;
      $('#more-comp').modal('show');

    }

    $scope.showRecruiterPopup = function(talent){
      $scope.selectedCandidate = talent;
      $('#recruiter-modal').modal('show');

    }

    $scope.editRecruiter = function(){
        $scope.isName = false;
        $('#recruiter-modal').modal('hide');
        $('#edit-recruiter').modal('show');
    }

    $scope.openProjectList = function(id, callFrom){
        if(id){
          $scope.currentTalentId = id;
        }
        else{
          $scope.currentTalentId = '';
        }
        $('#add-project').modal('show');
    }

    $scope.addToProject = function(projectDD){
        var selectedProjectId ;
        var talent = [];

        if($scope.projectDD != ('Select Project' || 'Search Project')){
              for(var i=0;i<$rootScope.allProjectList.length;i++)
               {
                 if($rootScope.allProjectList[i].project_name == $scope.projectDD)
                    {
                      selectedProjectId = $rootScope.allProjectList[i].id;
                      break;
                    }
               }
        }
         if($scope.currentTalentId != ''){
             talent.push($scope.currentTalentId);

         }else if($scope.choosenCandidates.length > 0){
            for(var k=0;k< $scope.choosenCandidates.length; k++)
                {
                    talent.push($scope.choosenCandidates[k]);
                }

         }

        if(selectedProjectId && talent.length > 0){
            $('#add-talent').addClass('disabled');
            $('#add-talent').css('pointer-events','none');
            var formData = new FormData();
             formData.append('token', $rootScope.globals.currentUser.token);
             formData.append('recruiter', $rootScope.globals.currentUser.user_email);
             formData.append('project_id', selectedProjectId);
             formData.append('talent_id[]',talent);
             talentApis.addTalentsToProject(formData, requestCallback);
             function requestCallback(response) {
                  response = JSON.parse(response);
                  console.log(response);
                  $('#add-project').modal('hide');
                  $('#projectSuccess').css('display','block');
                  setTimeout(function () {
                        $('#projectSuccess').css('display','none');
                    }, 2000);
                }
         }
    }


    $scope.updateSelection = function(id, position, talentList) {

           if ($scope.choosenCandidates.indexOf(id) == -1 )
                $scope.choosenCandidates.push(id);
            else
                $scope.choosenCandidates.splice($scope.choosenCandidates.indexOf(id), 1);

       if($scope.choosenCandidates.length > 0){
            $('#assignToProject').removeClass('disabled-talent');
            $('#assignToProject').addClass('add-talent');
            $('#talent-delete').css('pointer-events','');
       }else{
            $('#assignToProject').removeClass('add-talent');
            $('#assignToProject').addClass('disabled-talent');
            $('#talent-delete').css('pointer-events','none');
       }
                console.log($scope.choosenCandidates);
    }

    $scope.selectAll = function() {
      var state = $('#selectall').prop('checked');
      if(state){
         $scope.choosenCandidates =[];
         for(var i=0;i<$scope.talentList.length;i++){
                  $('#check_'+$scope.talentList[i].id).prop('checked',true);
                  $scope.choosenCandidates.push($scope.talentList[i].id);
            }
      }
      else{
         for(var i=0;i<$scope.talentList.length;i++){
                  $('#check_'+$scope.talentList[i].id).prop('checked',false);
                  $scope.choosenCandidates.splice($scope.choosenCandidates.indexOf($scope.talentList[i].id), 1);
            }
      }
       if($scope.choosenCandidates.length > 0){
            $('#assignToProject').removeClass('disabled-talent');
            $('#assignToProject').addClass('add-talent');
            $('#talent-delete').css('pointer-events','');
       }else{
            $('#assignToProject').removeClass('add-talent');
            $('#assignToProject').addClass('disabled-talent');
            $('#talent-delete').css('pointer-events','none');
       }
    }

    $scope.deleteTalents = function(){
        $('#delete-talent-popup').modal('show');
    }

    $scope.deleteTalentsConfirm = function(){
        var talent = [];
         if($scope.choosenCandidates.length > 0){
            for(var k=0;k< $scope.choosenCandidates.length; k++)
                {
                    talent.push($scope.choosenCandidates[k]);
                }

         }

        if(talent.length > 0){
            $('#confirm').addClass('disabled');
            $('#confirm').css('pointer-events','none');
            var requestObject = {
            'recruiter': $rootScope.globals.currentUser.user_email,   // password field value
            'talent': talent[0],
            'inactive':'True'
             };
             talentApis.deleteTalents(requestObject).then(function(response){
                if(response.message == "success") {
                 $('#delete-talent-popup').modal('hide');
                 $('#deleteSuccess').css('display','block');
                 setTimeout(
                        function () {
                            $('#deleteSuccess').css('display','none');
                        }, 20000);
                  }else{
                    console.log('error');
                }
             });
         }
    }

    $scope.showEdit = function(){
      $scope.isEmailAdd = false;
      if(!$scope.isEmailEditable){
         $scope.isEmailEditable = true;
      }else if($scope.isEmailEditable){
        $scope.isEmailEditable = false;
      }
    }

    $scope.showAdd = function(){
      $scope.isEmailEditable = false;
      if(!$scope.isEmailAdd){
         $scope.isEmailAdd = true;
      }else if($scope.isEmailAdd){
        $scope.isEmailAdd = false;
      }
    }

    $scope.showContactEdit = function(){
      $scope.isContactAdd = false;
      if(!$scope.isContactEditable){
         $scope.isContactEditable = true;
      }else if($scope.isContactEditable){
        $scope.isContactEditable = false;
      }
    }

    $scope.showContactAdd = function(){
      $scope.isContactEditable = false;
      if(!$scope.isContactAdd){
         $scope.isContactAdd = true;
      }else if($scope.isContactAdd){
        $scope.isContactAdd = false;
      }
    }

    $scope.reverse = false;
   $scope.sortBy = function(propertyName) {                   // filed sorting functionality in all project view
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


}


angular
    .module('brightStaffer')
    .controller('MainCtrl', MainCtrl)
    .controller('loginCtrl', loginCtrl)
    .controller('signupCtrl', signupCtrl)
    .controller('forgotCtrl', forgotCtrl)
    .controller('resetPwCtrl', resetPwCtrl)
    .controller('topnavCtrl', topnavCtrl)
    .controller('createProjectCtrl', createProjectCtrl)
    .controller('tableCtrl', tableCtrl)
    .controller('scoreCardCtrl',scoreCardCtrl)
    .controller('uploadFileCtrl', uploadFileCtrl)
    .controller('talentCtrl', talentCtrl)
    .controller('sideNavCtrl', sideNavCtrl);
