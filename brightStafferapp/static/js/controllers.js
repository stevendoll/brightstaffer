function MainCtrl($scope, $rootScope, $location, $http, $cookies, $cookieStore, getTopSixProjects, getAllProjects, paginationData, $window, $state, $timeout, $stateParams) { /*global controller */
    $rootScope.topSixProjectList = []; // top six project list array
    $rootScope.allProjectList = []; // all project array
    $rootScope.totalProjectCount = 0;
    $rootScope.apiHiCounter = 0;
    $rootScope.recruiter = {};
    $rootScope.projectCountStart = 1;
    $rootScope.projectCountEnd = 0;
    $rootScope.paginationCounter = 1;
    $scope.stateArray = ['projects', 'create.step1', 'create.step2', 'create.step3', 'create.step4'];
    $rootScope.isDevice = false;
    $rootScope.projectListView = [];
    $rootScope.StagesProjectList = [];
    $rootScope.talentAllStages = [];
    $scope.showLoader = false;


    $rootScope.showLoader = function (show) {
        $scope.showLoader = show;
    }

    $rootScope.getTopSixProjects = function () { // function to fetch top 6 projects
        var requestObject = {
            'token': $rootScope.globals.currentUser.token, // username field value
            'recruiter': $rootScope.globals.currentUser.user_email // password field value
        };
        getTopSixProjects.topSix(requestObject).then(function (response) {
            if (response.message == "success") {
                $rootScope.topSixProjectList = response.top_project;

            } else {
                console.log('error');
            }
        });
    }

    $rootScope.showAllProjects = function () {
        $rootScope.paginationCounter = 1;
        var count = 10;
        if ($rootScope.countList) {
            count = $rootScope.countList.value;
        }
        $('html, body').animate({
            scrollTop: 0
        }, 'fast');
        var requestObject = {
            'token': $rootScope.globals.currentUser.token, // username field value
            'recruiter': $rootScope.globals.currentUser.user_email,
            'count': count // password filed value
        };
        getAllProjects.allProjects(requestObject).then(function (response) {
            if (response.message == "success") {
                var nextButton = document.getElementById('Table_next');
                nextButton = angular.element(nextButton);
                var prevButton = document.getElementById('Table_previous');
                prevButton = angular.element(prevButton);
                $rootScope.totalProjectCount = response.count;
                $rootScope.allProjectList = response.published_projects;
                $rootScope.projectListView = [];
                $rootScope.StagesProjectList = [];
                for (var i = 0; i < $rootScope.allProjectList.length; i++) {
                    var project = {
                        name: '#' + $rootScope.allProjectList[i].project_name,
                        value: $rootScope.allProjectList[i].id
                    };
                    $rootScope.projectListView.push(project);
                    $rootScope.StagesProjectList.push(project);
                }
                $rootScope.projectListView = _.uniq($rootScope.projectListView, 'name');
                $rootScope.StagesProjectList = _.uniq($rootScope.StagesProjectList, 'name');
                // console.log($rootScope.projectListView);
                sessionStorage.removeItem('projectList');

                sessionStorage.projectList = JSON.stringify($rootScope.projectListView);
                sessionStorage.stageProjectList = JSON.stringify($rootScope.StagesProjectList);

                //}
                $rootScope.projectCountEnd = response.published_projects.length;
                $rootScope.projectNext = response.next;
                $rootScope.projectPrevious = response.previous;
                if ($rootScope.projectNext != null) {
                    nextButton.removeClass('disabled');
                    nextButton.parent().removeClass('disabled');
                }
                if ($rootScope.projectPrevious != null) {
                    prevButton.removeClass('disabled');
                    prevButton.parent().removeClass('disabled');
                }
            } else {
                console.log('error');
            }
        });
    }

    this.removePopupBox = function () {
        $('#breakPopup').css('display', 'none');
        $rootScope.isSuccess = false;
    }

    $scope.fetchProjects = function () {
        $rootScope.globals.currentUser = $cookieStore.get('userData');
        if ($rootScope.globals.currentUser && $rootScope.globals.currentUser.token && $rootScope.globals.currentUser.user_email) {
            $scope.getTopSixProjects();
            $rootScope.showAllProjects();
        }
    }
    $scope.fetchProjects();
    //    $scope.init();

};

function loginCtrl($scope, $rootScope, $state, $http, $cookies, $cookieStore, $timeout, loginService) { /* login controller responsible for login functionality */
    $scope.showErr = false;
    $scope.isDisabled = false;
    $scope.emailPattern = /^[a-z]+[a-z0-9._]+@[a-z]+\.[a-z.]{2,5}$/; //email validation pattern
    $scope.data = {
        user_name: '',
        user_password: ''
    };
    /**Create function for user login **/
    this.userLogin = function () {
        $scope.showErr = false;
        $rootScope.checkReqValidation('loginForm');
        var requestObject = {
            'username': $scope.data.user_name, // username field value
            'password': $scope.data.user_password // password filed value
        };
        if ($scope.loginForm.$valid) {
            $scope.isDisabled = true;
            loginService.userLogin(requestObject).then(function (response) {
                if (response.message == "success") {
                    var userData = {};
                    userData.first_name = response.first_name;
                    userData.last_name = response.last_name;
                    //$rootScope.recruiter.recruiterName = response.first_name+ ' '+response.last_name;
                    userData.token = response.user_token;
                    userData.user_email = response.user_name;
                    $rootScope.globals.currentUser = userData; // storing the logged in user data for further communication on site
                    $rootScope.getTopSixProjects();
                    $rootScope.showAllProjects();
                    $cookieStore.put('userData', userData);
                    $state.go('dashboard', ""); // after successful log in redirection to dashboard view
                } else {
                    $scope.showErr = true;
                    $scope.isDisabled = true;
                }
            });

        }
    }

    this.hideMessages = function ($event) { /*Hide error messages when user interact with fieds*/
        if ($event.keyCode !== 13) {
            $scope.showErr = false;
            $scope.isDisabled = false;
            $("#loginForm input").each(function () {
                var spanClass = $(this).next('span').attr('class');
                if ($(this).val().length <= 0 && ($(this).next('span').hasClass('error'))) {
                    $(this).next('span').removeClass('error').text("");
                } else if ($(this).val().length > 0 && ($(this).next('span').hasClass('error'))) {
                    $(this).next('span').removeClass('error').text("");
                }
            });
        }
    }
}


function signupCtrl($scope, $rootScope, $state, $http, $window, $timeout, $cookies, $cookieStore, signupService) { /* signup controller responsible for signup form functionality */
    $scope.userRegistration = {};
    $scope.isDisabled = false;
    $scope.errorMessage = '';
    $scope.success = false;
    $scope.passwordStrength = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/; // password validation pattern
    $scope.emailPattern = /^[a-z]+[a-z0-9._]+@[a-z]+\.[a-z.]{2,5}$/;
    // email pattern
    $scope.user_Signup = function () { /* signup function submitting user details to API*/
        $scope.errorMessage = '';
        $rootScope.checkReqValidation('signupForm');
        var requestObject = {
            'firstName': $scope.userRegistration.first_name,
            'lastName': $scope.userRegistration.last_name,
            'userEmail': $scope.userRegistration.user_email,
            'password': $scope.userRegistration.password
        };
        if ($scope.signupForm.$valid) {
            $scope.isDisabled = true;
            signupService.userSignup(requestObject).then(function (response) {
                if (response.message == "success") {
                    $scope.signupForm.$setPristine();
                    $scope.userRegistration = {};
                    var userData = {};
                    userData.first_name = response.first_name;
                    userData.last_name = response.last_name;
                    userData.token = response.user_token;
                    userData.user_email = response.user_name;
                    $rootScope.globals.currentUser = userData;
                    $cookieStore.put('userData', userData);
                    $state.go('dashboard', "");
                } else {
                    $scope.errorMessage = "User with this email already exists!";
                    $scope.isDisabled = false;
                }
            });
        }
    }

    $scope.hideMessages = function ($event) { /*Hide error messages when user interact with fieds*/
        if ($event.keyCode !== 13) {
            $("#signupForm input").each(function () {
                var spanClass = $(this).next('span').attr('class');
                if ($(this).val().length <= 0 && ($(this).next('span').hasClass('error'))) {
                    $(this).next('span').removeClass('error').text("");
                } else if ($(this).val().length > 0 && ($(this).next('span').hasClass('error'))) {
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
    $scope.forgotPassword = function () {
        $scope.errorMessage = '';
        var value = document.getElementById('emailInput').value;
        if (!value)
            $scope.isRequired = true;

        var requestObject = {
            'email': $scope.user_email
        };
        if ($scope.forgotForm.$valid) {
            $scope.isRequired = false;
            $scope.isDisabled = true;
            forgotService.forgotPassword(requestObject).then(function (response) {
                if (response.message == "success") {
                    $scope.user_email = '';
                    $scope.isDisabled = false;
                    $scope.errorMessage = 'Link to reset password is sent on your mail! Please check.';
                } else {
                    $scope.errorMessage = 'No account with this email id.';
                    $scope.isDisabled = false;
                }
            });
        }
    }
}


function resetPwCtrl($scope, $rootScope, $state, $http, $window, $stateParams, $location, resetPasswordService) {
    var token = $window.location.href.split('reset_password_confirm/')[1].replace('/', '');
    $scope.isDisabled = false;
    $scope.successMsg = false;
    $scope.failMessage = false;
    $scope.success = false;
    $scope.data = {};
    $scope.passwordStrength = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;
    $scope.changePassword = function () {
        $scope.isDisabled = true;
        var requestObject = {
            'token': token,
            'password': $scope.data.password
        };
        resetPasswordService.resetPassword(requestObject).then(function (response) {
            if (response.message == "success") {
                $scope.data = {};
                $scope.successMsg = true;
                $scope.success = true;
            } else {
                $scope.data = {};
                $scope.failMessage = true;
            }
        });
    }

    $scope.changePath = function () {
        var path = 'http://' + $window.location.host + '/#/login';
        $window.location.href = path;
    }
}

function topnavCtrl($scope, $rootScope, $state, $http, $window, $stateParams, $cookies, $cookieStore, $location, searchApis, talentApis, searchData) {
    $rootScope.search = {};
    $rootScope.topSearch = false;
    this.logout = function () {
        $cookieStore.remove('userData');
        $rootScope.globals = {};
        $state.go('login', '');
    }
    $rootScope.candidatePages = [];
    $rootScope.globalSearch = true;
    $scope.getSearchData = function (onReload, globalSearch) {
        if (globalSearch) {
            $rootScope.globalSearch = true;
            if ($rootScope.candidatePagination.page == 1) {} else {
                $rootScope.candidatePagination.page = 1;
                return;
            }

        }
        var currentState = $state.current.name;
        var allowedArray = ["talent.talent-profile", "talent.talent-search", "talent.talent-search.talent-search-card", "talent.talent-search.talent-search-list", "talent.create-profile"];
        if (allowedArray.indexOf(currentState) > -1) {

            if (!onReload && (currentState == "talent.talent-profile" || currentState == "talent.create-profile")) {
                $state.go('talent.talent-search.talent-search-card');
            }
            $('#selectall').prop('checked', false);

            $rootScope.filterReset();

            var requestObject = {
                'keyword': $rootScope.search.searchKeywords || '',
                page: $rootScope.candidatePagination.page,
                count: $rootScope.candidatePagination.count
            };
            searchApis.talentSearch(requestObject).then(function (response) {
                $rootScope.Filter = false;
                $rootScope.topSearch = true;
                $rootScope.talentList = [];
                if (response.results.length > 0) {
                    for (var i = 0; i < response.results.length; i++) {
                        $rootScope.talentList.push(response.results[i]);
                    }
                }
                $rootScope.totalTalentCount = response.count;
                $rootScope.talentCountEnd = $rootScope.talentList.length;
                $rootScope.candidatePages = [];
                for (var i = 0; i < Math.ceil($rootScope.totalTalentCount / $rootScope.candidatePagination.count); i++) {
                    $rootScope.candidatePages.push({
                        i: true
                    });
                }
                $rootScope.createCareerHistoryData($rootScope.talentList);
            });
        }
    }

    //    $scope.getSearchData(true);

    $rootScope.getCandidateData = function (check) {
        console.log('fetching candidate data');
        if (check == 'sideNav') {
            $scope.recordCount = 10;
            $rootScope.candidatePagination = {
                page: 1,
                count: parseInt($scope.recordCount)
            }
            $rootScope.search.searchKeywords = '';
            //$rootScope.filterReset();
            $rootScope.isFilterChecked = false;
            $('.talent-search-icon').removeClass('active');
            $('html, body').animate({
                scrollTop: 0
            }, 'fast');
            $scope.getSearchData();
        } else {
            $scope.getSearchData(check);
        }
    }

    $rootScope.$on('fetchCandidateData', $rootScope.getCandidateData);
}


function createProjectCtrl($scope, $rootScope, $state, $http, $window, $stateParams, $cookies, $cookieStore, $location, $timeout, jobPostService, alchemyAnalysis, updateConcepts, publishProject) {
    $scope.projectForm = {
        project_name: '',
        company_name: '',
        location: '',
        description: ''
    };
    $rootScope.globals.currentProject_id = '';
    $scope.isProjMaxlength = false;
    $scope.isComMaxlength = false;
    $scope.isLocationMaxlength = false;
    $scope.isProjectnmValid = false;
    $scope.isProjectnmExists = false;
    $scope.isLastStepVisited = false;
    $scope.isError = false;
    $scope.isDescriptionError = false;
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
    this.projectNamePattern = /((^[ A-Za-z0-9_@./#-]*)|(^[a-zA-Z]+[_@./#-]*)|(^[0-9]+[a-z]+)|(^[a-z]+[0-9]+))+[0-9a-z]+$/i; // /^[a-z0-9]+$/i;

    $scope.checkMessage = function () { /*Hide error messages when user interact with fieds*/
        $scope.isDescriptionRequired = false;
        $("#createProjectForm input").each(function () {
            var spanClass = $(this).next('span').attr('class');
            if ($(this).val().length <= 0 && ($(this).next('span').hasClass('error'))) {
                $(this).next('span').removeClass('error').text("");
            } else if ($(this).val().length > 0 && ($(this).next('span').hasClass('error'))) {
                $(this).next('span').removeClass('error').text("");
            }
        });
    }


    $scope.takeNext = function (currentState, prevTabId, currentTabId) { // next button view change functionality
        $scope.isProjectnmValid = false;
        $scope.isDescriptionRequired = false;
        $("#createProjectForm input").each(function () { /*Show error on blank field when user submit*/
            var spanClass = $(this).next('span').attr('class');
            if ($(this).val().length <= 0) {
                $(this).next('span').css('display', 'block');
                $(this).next('span').addClass('error').text("Required.");
            } else if ($(this).val().length > 0 && ($(this).next('span').hasClass('error'))) {
                $(this).next('span').removeClass('error').text("");
            }
        });
        if ($scope.projectForm.project_name && $scope.projectForm.company_name && $scope.projectForm.location && !$scope.patternError) {
            var backButton = angular.element(document.querySelector('#previous'));
            backButton.removeClass('disabled');
            var mainUl = angular.element(document.querySelector('#projectBtns'));
            if (mainUl.hasClass('twobtn')) {
                mainUl.removeClass('twobtn');
            }
            backButton.children(':first').removeClass('disable');
            if ($("#tablist").find(".current").length > 0) {
                $("#tablist").find(".current").addClass("done");
                $("#tablist").find(".current").removeClass("current");
            }
            var currentTab = angular.element(document.querySelector(currentTabId));
            if (currentTab.hasClass('done')) {
                currentTab.removeClass('done');
            }
            currentTab.removeClass('disabled');
            currentTab.addClass('current');
            $scope.isSecondStepVisited = true;
            $state.go('create.step2', '');
        }

    }

    $scope.takeToStepThree = function (currentState, prevTabId, currentTabId) {
        if (!$scope.projectForm.description) {
            $scope.isDescriptionRequired = true;
        } else if ($scope.projectForm.description) {
            /*if (!$rootScope.jobDescriptionResult) {
                $(".loader").css('display', 'block');
            }*/

            if ($("#tablist").find(".current").length > 0) {
                $("#tablist").find(".current").addClass("done");
                $("#tablist").find(".current").removeClass("current");
            }
            var currentTab = angular.element(document.querySelector(currentTabId));
            if (currentTab.hasClass('done')) {
                currentTab.removeClass('done');
            }
            var mainUl = angular.element(document.querySelector('#projectBtns'));
            if (mainUl.hasClass('twobtn')) {
                mainUl.removeClass('twobtn');
            }
            currentTab.removeClass('disabled');
            currentTab.addClass('current');
            $scope.isthirdStepVisited = true;
            $state.go('create.step3', '');
        }
    }

    $scope.takeToStepFour = function (currentState, prevTabId, currentTabId) {
        if ($rootScope.jobDescriptionResult.concept.length > 0) {
            var nextButton = angular.element(document.querySelector('#next'));
            nextButton.css('display', 'none');
            var mainUl = angular.element(document.querySelector('#projectBtns'));
            mainUl.addClass('twobtn');
            var publishButton = angular.element(document.querySelector('#publish'));
            publishButton.removeClass('disabled');
            publishButton.children(':first').removeClass('disable');
            if ($("#tablist").find(".current").length > 0) {
                $("#tablist").find(".current").addClass("done");
                $("#tablist").find(".current").removeClass("current");
            }
            var currentTab = angular.element(document.querySelector(currentTabId));
            if (currentTab.hasClass('done')) {
                currentTab.removeClass('done');
            }
            currentTab.removeClass('disabled');
            currentTab.addClass('current');
            $scope.isLastStepVisited = true;
            $state.go('create.step4', '');
        } else if ($rootScope.jobDescriptionResult.concept.length == 0) {
            $scope.isDescriptionError = true;
            $scope.apiErrorMsg = 'Required.';
        }
    }

    this.activateTab = function ($event) {
        var elementId = $event.target.id;
        var currentState = $state.current.name;
        var currentTabId;
        var prevTabId;
        var nextButton = angular.element(document.querySelector('#next'));
        nextButton.css('display', 'block');
        var publishButton = angular.element(document.querySelector('#publish'));
        publishButton.addClass('disabled');
        publishButton.children(':first').addClass('disable');
        if ($scope.isFirstStepVisited && elementId == 'form-p-0') {
            if ($("#tablist").find(".current").length > 0) {
                $("#tablist").find(".current").addClass("done");
                $("#tablist").find(".current").removeClass("current");
            }
            if ($('#form-t-0').hasClass('done')) {
                $('#form-t-0').removeClass('done');
            }
            $('#form-t-0').addClass('current');
            var prevButton = angular.element(document.querySelector('#previous'));
            prevButton.addClass('disabled');
            prevButton.children(':first').addClass('disable');
            $state.go('create.step1', '');
        }
        if ($scope.isSecondStepVisited && elementId == 'form-p-1') {
            angular.element($event.target).removeAttr('style');
            currentTabId = '#form-t-1';
            prevTabId = '';
            $scope.takeNext(currentState, prevTabId, currentTabId);
        }
        if ($scope.isthirdStepVisited && elementId == 'form-p-2') {
            angular.element($event.target).removeAttr('style');
            currentTabId = '#form-t-2';
            prevTabId = '';
            var backButton = angular.element(document.querySelector('#previous'));
            backButton.removeClass('disabled');
            backButton.children(':first').removeClass('disable');
            $scope.takeToStepThree(currentState, prevTabId, currentTabId);
        }
        if ($scope.isLastStepVisited && elementId == 'form-p-3') {
            angular.element($event.target).removeAttr('style');
            currentTabId = '#form-t-3';
            prevTabId = '';
            var backButton = angular.element(document.querySelector('#previous'));
            backButton.removeClass('disabled');
            backButton.children(':first').removeClass('disable');
            $scope.takeToStepFour(currentState, prevTabId, currentTabId);
        }
    }


    $scope.SwitchFuction = function () { // generic function which call different stepwise function
        var currentState = $state.current.name;
        var prevTabId;
        var currentTabId;
        switch (currentState) {
            case 'create.step1':
                prevTabId = '#form-t-0';
                currentTabId = '#form-t-1';
                $scope.takeNext(currentState, prevTabId, currentTabId);
                break;
            case 'create.step2':
                $scope.updateJobDescription($scope.projectForm.description);
                prevTabId = '#form-t-1';
                currentTabId = '#form-t-2';
                $scope.takeToStepThree(currentState, prevTabId, currentTabId);
                break;
            case 'create.step3':
                prevTabId = '#form-t-2';
                currentTabId = '#form-t-3';
                $scope.isDescriptionError = false;
                $scope.takeToStepFour(currentState, prevTabId, currentTabId);
                break;
        }

    }

    $scope.takeBack = function (currentState, prevTabId, currentTabId) {
        var prevTab = angular.element(document.querySelector(prevTabId));
        var publishButton = angular.element(document.querySelector('#publish'));
        publishButton.addClass('disabled');
        publishButton.children(':first').addClass('disable');
        prevTab.addClass('current');
        prevTab.removeClass('done');
        var currentTab = angular.element(document.querySelector(currentTabId));
        currentTab.addClass('done');
        if (currentState == "create.step2") {
            $scope.isDescriptionRequired = false;
            var prevButton = angular.element(document.querySelector('#previous'));
            prevButton.addClass('disabled');
            prevButton.children(':first').addClass('disable');
            $state.go('create.step1', '');
        } else if (currentState == "create.step3") {
            $scope.isError = false;
            $scope.apiErrorMsg = '';
            $state.go('create.step2', '');
        } else if (currentState == "create.step4") {
            var nextButton = angular.element(document.querySelector('#next'));
            nextButton.css('display', 'block');
            var mainUl = angular.element(document.querySelector('#projectBtns'));
            if (mainUl.hasClass('twobtn')) {
                mainUl.removeClass('twobtn');
            }
            $state.go('create.step3', '');
        }
    }

    $scope.goToBack = function () {
        var currentState = $state.current.name;
        switch (currentState) {
            case 'create.step2':
                prevTabId = '#form-t-0';
                currentTabId = '#form-t-1';
                $scope.takeBack(currentState, prevTabId, currentTabId);
                break;
            case 'create.step3':
                prevTabId = '#form-t-1';
                currentTabId = '#form-t-2';
                $scope.takeBack(currentState, prevTabId, currentTabId);
                break;
            case 'create.step4':
                prevTabId = '#form-t-2';
                currentTabId = '#form-t-3';
                $scope.takeBack(currentState, prevTabId, currentTabId);
                break;
        }

    }


    $scope.removeValidationMsg = function ($event) {
        $scope.isProjectnmValid = false;
        $scope.isProjectnmExists = false;
    }

    $scope.checkProjectName = function ($event) {
        if ($event.target.name == "company_name" || "location") { // if projectName is blank prompt for it
            $scope.checkMessage();
            var element = angular.element(document.querySelector('#project_name'));
            if (element && !element[0].value) {
                $scope.isProjectnmValid = true;
                element[0].focus();
                $event.preventDefault();
            }
        }
    }

    $scope.updateProjectName = function ($event) {
        if ($event.target.value != '') {
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
            jobPostService.jobPost(requestObject).then(function (response) {
                if (response.message == "success") {
                    if ($rootScope.globals.currentProject_id == '')
                        $rootScope.globals.currentProject_id = response.project_id;
                    var ProjectData = [];
                    var valueObj = {
                        'key': 'project_id',
                        'value': $rootScope.globals.currentProject_id
                    };
                    ProjectData.push(valueObj);
                    valueObj = {
                        'key': 'project_name',
                        'value': projectName
                    };
                    ProjectData.push(valueObj);
                    $cookies.put('currentProjectId', JSON.stringify(ProjectData));
                } else {
                    if (response.errorstring) {
                        $scope.isProjectnmExists = true;
                    }
                }
            });
        }
    }

    $scope.validateLocation = function (value) {
        $scope.patternError = false;
        var zip = /^(?!0{5})\d{5}$/;
        var city = /^[ A-Za-z-,]*$/;
        if (!isNaN(value) && value) {
            if (!zip.test(value)) {
                $scope.patternError = true;
                $scope.locationPatternMsg = 'Enter 5 digit zipcode!';
            }
        } else if (value) {
            if (!city.test(value)) {
                $scope.patternError = true;
                $scope.locationPatternMsg = 'Enter valid city name!';
            }
        }
    }

    $scope.saveData = function (name, value) {
        if (value) {
            $timeout(saveUpdates(name, value), 2000); // 2000 = 2 second
        }

    }

    var saveUpdates = function (name, value) {
        var is_published = false;
        var token = $rootScope.globals.currentUser.token;
        var recruiter = $rootScope.globals.currentUser.user_email;
        var requestObject = {};
        requestObject["id"] = $rootScope.globals.currentProject_id;
        requestObject[name] = value;
        requestObject["token"] = token;
        requestObject["recruiter"] = recruiter;
        requestObject["is_published"] = is_published;
        jobPostService.jobPost(requestObject).then(function (response) {
            if (response.message == "success") {
                if ($scope.timeout) {
                    $timeout.cancel($scope.timeout)
                }
            } else {
                $scope.timeout = $timeout(saveUpdates(name, value), 3000);
            }
        }, function (error) {
            if (error) {
                $scope.timeout = $timeout(saveUpdates(name, value), 1000);
            }
        });
    }

    $scope.updateJobDescription = function (value) {
        if (value) {
            $rootScope.jobDescriptionResult = '';
            $scope.isDescriptionError = false;
            $scope.apiErrorMsg = '';
            var is_published = false;
            var token = $rootScope.globals.currentUser.token;
            var recruiter = $rootScope.globals.currentUser.user_email;
            var requestObject = {};
            requestObject["id"] = $rootScope.globals.currentProject_id;
            requestObject['description'] = value;
            requestObject["token"] = token;
            requestObject["recruiter"] = recruiter;
            requestObject["is_published"] = is_published;
            alchemyAnalysis.alchemyAPI(requestObject).then(function (response) {
                if (response.message == "success") {
                    $rootScope.jobDescriptionResult = response;
                    if ($rootScope.jobDescriptionResult.concept.length == 0) {
                        $scope.isDescriptionError = true;
                        $scope.apiErrorMsg = "There is no relevant keywords in your description.";
                    }

                    //$(".loader").css('display', 'none');

                } else {
                    if (response.errorstring) {
                        if ($rootScope.jobDescriptionResult == '') {
                            $rootScope.jobDescriptionResult = {};
                            $rootScope.jobDescriptionResult.concept = [];
                        }
                        $scope.isDescriptionError = true;
                        $scope.apiErrorMsg = "Description text data is not valid.";
                    }
                    //$(".loader").css('display', 'none');
                    console.log('error');
                }
            });
        }

    }

    var validateSkillName = function (skillName) {
        var re = /(^[a-zA-Z_. -][a-zA-Z0-9_. -]{1,50})+$/;
        return re.test(skillName);
    }

    $scope.updateSkillView = function ($event) {
        $scope.isDescriptionError = false;
        $scope.apiErrorMsg = '';
        if ($event.target.value) {
            var skill = $event.target.value;
            if (skill.length < 2) {
                $scope.isDescriptionError = true;
                $scope.apiErrorMsg = 'Please provide atleast 2 character!';
            } else if (!validateSkillName(skill)) {
                $scope.isDescriptionError = true;
                $scope.apiErrorMsg = 'Input should contain first letter as character and allowed special characters are (. - _).';
            } else {
                var newSkill = $event.target.value;
                var index = $rootScope.jobDescriptionResult.concept.indexOf(newSkill);

                if (index == -1) {
                    $rootScope.jobDescriptionResult.concept.push(newSkill);
                } else {
                    $scope.isDescriptionError = true;
                    $scope.apiErrorMsg = 'Already exists!';
                }
                $event.target.value = '';
                $scope.updateSkillSet();
            }
        }
    }

    $scope.updateSkillSet = function () {
        var is_published = false;
        var token = $rootScope.globals.currentUser.token;
        var recruiter = $rootScope.globals.currentUser.user_email;
        var requestObject = {};
        requestObject["id"] = $rootScope.globals.currentProject_id;
        requestObject["concept"] = $rootScope.jobDescriptionResult.concept;
        requestObject["token"] = token;
        requestObject["recruiter"] = recruiter;
        requestObject["is_published"] = is_published;
        updateConcepts.conceptsAPI(requestObject).then(function (response) {
            if (response.message == "success") {
                console.log(response);
            } else {
                console.log('error');
            }
        });

    }

    $scope.publishProject = function () {
        if ($state.current.name == 'create.step4') {
            $scope.isSuccess = false;
            $scope.publishMsg = '';
            $scope.isPublish = false;
            $(".loader").css('display', 'block');
            var is_published = true;
            $scope.isPublish = false;
            var token = $rootScope.globals.currentUser.token;
            var recruiter = $rootScope.globals.currentUser.user_email;
            var requestObject = {};
            requestObject["id"] = $rootScope.globals.currentProject_id;
            requestObject["token"] = token;
            requestObject["recruiter"] = recruiter;
            requestObject["is_published"] = is_published;
            publishProject.publish(requestObject).then(function (response) {
                if (response.message == "success") {
                    $(".loader").css('display', 'none');
                    // $scope.publishMsg = "Project created successfully.";
                    $scope.isPublish = true;
                    $state.go('dashboard', '');
                } else {
                    $(".loader").css('display', 'none');
                    $scope.isSuccess = true;
                    $scope.publishMsg = "Please try again.";
                    $('#breakPopup').css('display', 'block');
                    console.log('error');
                }
            });
            $timeout(function () {
                if ($scope.isPublish == false) {
                    $(".loader").css('display', 'none');
                    $scope.isSuccess = true;
                    $scope.publishMsg = "Please try again.";
                    $('#breakPopup').css('display', 'block');
                }
            }, 30000); //timeout after three minutes
        }
    }

    $scope.gotoTop = function () {
        $('html, body').animate({
            scrollTop: 0
        }, 'fast');
    }
}


function tableCtrl($scope, $rootScope, $location, $http, $cookies, $cookieStore, getTopSixProjects, getAllProjects, paginationData, $window, $state, $timeout, tableService) { /*global controller */
    $scope.options = [{
        name: '10',
        value: 10
    }, {
        name: '25',
        value: 25
    }, {
        name: '50',
        value: 50
    }, {
        name: '100',
        value: 100
    }]; // select drop-down options
    $rootScope.countList = $scope.options[0];
    $scope.hidenData = {};
    $scope.popupMsg = '';
    $scope.apiHit = false;

    this.setButton = function () {
        var nextButton = angular.element(document.querySelector('#Table_next'));
        var prevButton = angular.element(document.querySelector('#Table_previous'));
        if ($rootScope.projectNext != null) {
            nextButton.removeClass('disabled');
            nextButton.parent().removeClass('disabled');
        }
        if ($rootScope.projectPrevious != null) {
            prevButton.removeClass('disabled');
            prevButton.parent().removeClass('disabled');
        }
    }

    this.getValue = function (countList) { //record count change functionality in all project list view
        var nextButton = angular.element(document.querySelector('#Table_next'));
        var prevButton = angular.element(document.querySelector('#Table_previous'));
        $(".loader").css('display', 'block');
        var requestObject = {
            'token': $rootScope.globals.currentUser.token, // username field value
            'recruiter': $rootScope.globals.currentUser.user_email, // password filed value
            'count': countList.value
        };
        getAllProjects.allProjects(requestObject).then(function (response) {
            $scope.apiHit = true;
            if (response.message == "success") {
                if (response.published_projects.length > 0)
                    $rootScope.allProjectList = response.published_projects;

                $rootScope.projectCountEnd = response.published_projects.length;
                $rootScope.projectNext = response.next;
                $rootScope.projectPrevious = response.previous;
                if ($rootScope.projectNext == null) {
                    nextButton.addClass('disabled');
                    nextButton.parent().addClass('disabled');
                } else {
                    if (nextButton.hasClass('disabled')) {
                        nextButton.removeClass('disabled');
                        nextButton.parent().removeClass('disabled');
                    }

                }
                if ($rootScope.projectPrevious == null) {
                    prevButton.addClass('disabled');
                    prevButton.parent().addClass('disabled');
                }
                $(".loader").css('display', 'none');
            } else {
                console.log('error');
                $(".loader").css('display', 'none');
                if (response.success == false) {
                    $rootScope.isSuccess = true;
                    $scope.popupMsg = "No data available.";
                    $('#breakPopup').css('display', 'block');
                }
            }
        });
    }

    $scope.getSelectedProjectIds = function (ids) {
        var ids = ""
        $('.proj-checkbox').each(function () {
            if ($(this).is(':checked')) {
                ids = ids + $(this).val() + ',';
            }
        });
        ids = ids.substr(0, ids.length - 1);
        return ids;
    }

    $scope.deleteProjects = function () {
        var ids = $scope.getSelectedProjectIds();
        var data = {
            project: ids
        };
        tableService.deleteProjects(data, function (response) {
            $rootScope.showAllProjects();
        });
    }

    this.changePage = function ($event) { // pagination with previous and next button event handler
        $rootScope.isSuccess = false;
        var url = '';
        $scope.popupMsg = '';
        var nextButton = angular.element(document.querySelector('#Table_next'));
        var prevButton = angular.element(document.querySelector('#Table_previous'));
        if ($event.target.name == "next") {
            $rootScope.paginationCounter++;
            $('#countDropdown').css('display', 'none');
            url = $rootScope.projectNext;
        } else if ($event.target.name == "prev") {
            if ($rootScope.paginationCounter > 1) {
                $rootScope.paginationCounter--;
                if ($rootScope.paginationCounter == 1) {
                    $('#countDropdown').css('display', '');
                }
            }
            url = $rootScope.projectPrevious;
        }
        $(".loader").css('display', 'block');
        var requestObject = {
            'url': url
        };
        paginationData.paginationApi(requestObject).then(function (response) {
            $scope.apiHit = true;
            if (response.message == "success") {
                if (response.published_projects.length > 0)
                    $rootScope.allProjectList = response.published_projects;
                $rootScope.projectNext = response.next;
                $rootScope.projectPrevious = response.previous;
                if ($event.target.name == "next") {
                    $rootScope.projectCountStart = $rootScope.projectCountEnd + 1;
                    $rootScope.projectCountEnd = $rootScope.projectCountEnd + response.published_projects.length;
                } else if ($event.target.name == "prev") {
                    $rootScope.projectCountStart = $rootScope.projectCountStart - response.published_projects.length;
                    if ($rootScope.projectCountStart <= 0)
                        $rootScope.projectCountStart = 1;
                    $rootScope.projectCountEnd = $rootScope.projectCountStart + response.published_projects.length - 1;
                    if ($rootScope.projectCountEnd < 10)
                        $rootScope.projectCountEnd = 10;
                }
                if ($rootScope.projectNext == null) {
                    nextButton.addClass('disabled');
                    nextButton.parent().addClass('disabled');
                } else {
                    if (nextButton.hasClass('disabled')) {
                        nextButton.removeClass('disabled');
                        nextButton.parent().removeClass('disabled');
                    }
                }
                if ($rootScope.projectPrevious == null) {
                    prevButton.addClass('disabled');
                    prevButton.parent().addClass('disabled');
                } else {
                    if (prevButton.hasClass('disabled')) {
                        prevButton.removeClass('disabled');
                        prevButton.parent().removeClass('disabled');
                    }
                }
                $(".loader").css('display', 'none');
            } else {
                $(".loader").css('display', 'none');
                if (response.success == false) {
                    if ($event.target.name == "next") {
                        nextButton.addClass('disabled');
                        $rootScope.paginationCounter--;
                        if ($rootScope.paginationCounter == 1) {
                            prevButton.addClass('disabled');
                        }
                        $scope.tableNext = false;
                    }
                    $rootScope.isSuccess = true;
                    $scope.popupMsg = "No data available.";
                    $('#breakPopup').css('display', 'block');

                }
            }
        });
    }

    $scope.$on('ngRepeatFinished', function (ngRepeatFinishedEvent) { // table responsiveness initialization after data render
        $timeout(function () {
            tableInitialise();
        }, 1000);
        if (navigator.userAgent.match(/iPhone/i)) {
            $('.buttons-excel').css('display', 'none');
        }
    });

    var update_size = function () {
        $('.dataTables').css({
            width: $('.dataTables').parent().width()
        });
        if ($scope.apiHit) {
            tableInitialise();
        }
    };

    $(window).resize(function () { // on window resize table resize for responsiveness
        clearTimeout(window.refresh_size);
        window.refresh_size = setTimeout(function () {
            update_size();
        }, 250);
    });

    var tableInitialise = function () {
        $scope.hidenData = {};
        var table = $('.dataTables').DataTable({
            responsive: true,
            retrieve: true,
            paging: true,
            autoWidth: false,
            buttons: [
                {
                    extend: 'copy',
                    className: 'btn btn-default btn-sm',
                    title: 'Copy'
                }, {
                    extend: 'csv',
                    className: 'btn btn-default btn-sm',
                    title: 'CSV'
                }, {
                    extend: 'excel',
                    className: 'btn btn-default btn-sm',
                    title: 'Excel'
                }, {
                    extend: 'pdf',
                    className: 'btn btn-default btn-sm',
                    title: 'PDF'
                }, {
                    extend: 'print',
                    className: 'btn btn-default btn-sm',
                    title: 'Print',
                    customize: function ($window) {
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
    var showHideColumn = function () { // on table responsiveness show and hide column value
        var tableHead = document.getElementsByTagName('th');
        var displayRows = $(".dataTables").find("tbody>tr");
        angular.forEach(tableHead, function (th) {
            var columnIndex = th.cellIndex;
            if (th.style['display'] == "none") {
                for (var currentRow = 0; currentRow < displayRows.length; currentRow++) {
                    if ($scope.hidenData[currentRow]) {
                        $scope.hidenData[currentRow] = $scope.hidenData[currentRow];
                    } else {
                        $scope.hidenData[currentRow] = [];
                    }
                    var data = {};
                    data["title"] = th.innerText;
                    data["index"] = columnIndex;
                    if (currentRow != 0 && currentRow % 2 == 0) {
                        $(displayRows[currentRow]).addClass('even');
                    } else {
                        $(displayRows[currentRow]).addClass('odd');
                    }
                    $(displayRows[currentRow]).find("td:eq(0)").addClass("sorting_1");
                    $(displayRows[currentRow]).find("td:eq(" + columnIndex + ")").css('display', 'none');
                    data["value"] = $(displayRows[currentRow]).find("td:eq(" + columnIndex + ")").text();
                    $scope.hidenData[currentRow].push(data);
                }
            } else {
                for (var currentRow = 0; currentRow < displayRows.length; currentRow++) {
                    $(displayRows[currentRow]).find("td:eq(0)").addClass("sorting_1");
                    $(displayRows[currentRow]).find("td:eq(" + columnIndex + ")").css('display', '');
                }

            }
        });
    }

    $scope.showChild = function ($event, row) {
        if ($($event.target.parentElement).hasClass('parent')) {
            $($event.target.parentElement).css("background-color", '#ffffff');
        } else {
            $($event.target.parentElement).css("background-color", '#f5f5f5');
        }
        if ($scope.apiHit) {
            if ($($event.target.parentElement).hasClass('parent')) {
                $($event.target.parentElement).removeClass('parent');
                $($event.target.parentElement).css("background-color", '#ffffff');
                angular.element($('#' + row)).remove();
            } else {
                $($event.target.parentElement).addClass('parent');

                var childEle = '<tr class="child" id="' + row + '"><td class="child" colspan="7"><ul data-dtr-index="7">';
                for (var i = 0; i < $scope.hidenData[row].length; i++) {
                    childEle = childEle + '<li data-dtr-index="' + $scope.hidenData[row][i].index + '"><span class="dtr-title">' + $scope.hidenData[row][i].title + '</span><span class="dtr-data">' + $scope.hidenData[row][i].value + '</span></li>';
                }
                childEle = childEle + '</ul></td></tr>';
                angular.element($event.target.parentElement).after(childEle);
                $($event.target.parentElement).css("background-color", '#f5f5f5');
            }
        }
    }

}

function scoreCardCtrl($scope, $rootScope, $location, $http, $cookies, $cookieStore, $window, $state, $timeout) {
    this.analysedData = [
        {
            "key": "analysedData",
            "values": [[6, 5], [7, 11], [8, 6], [9, 11], [10, 30], [11, 10], [12, 13], [13, 4], [14, 3], [15, 3], [16, 6]]
        }];

    this.activeCardData = [
        {
            "key": "activeCardData",
            "values": [[6, 1], [7, 5], [8, 2], [9, 3], [10, 2], [11, 1], [12, 0], [13, 2], [14, 8], [15, 0], [16, 0]]
        }];

    this.interviewCardData = [
        {
            "key": "interviewCardData",
            "values": [[4, 1], [8, 3], [12, 1], [16, 5], [20, 2], [24, 3], [28, 2]]
        }];

    this.fourthCardData = [
        {
            "key": "fourthCardData",
            "values": [[3, 0], [8, 1], [13, 0], [18, 2], [28, 8], [38, 0], [56, 0]]
        }];

    $scope.xAxisTicksFunction = function () {

        return function (d) {
            return d3.svg.axis().ticks(d3.time.minutes, 5);
        }
    };

    $scope.xAxisTickFormatFunction = function () {
        return function (d) {
            return d3.time.format('%H:%M')(moment.unix(d).toDate());
        }
    };

    $scope.colorFunction = function () {
        return function (d, i) {
            return 'rgb(255, 255, 255)'
        };
    }

    $rootScope.dirOptions = {};
    $scope.callDirFunc = function () {
        $scope.dirOptions.clearFiles();
    };

    $scope.resetModal = function () {
        $scope.dirOptions.clearFiles();
        var doneButton = document.getElementById('done');
        doneButton.classList.add('disabled');
        doneButton.classList.add('talent-modal-done');
        doneButton.classList.remove('talent-modal-add');
        doneButton.style['pointer-events'] = 'none';
        document.getElementById('backgroundImg').style.display = '';
    }

}

function uploadFileCtrl($scope, $rootScope, $location, $http, $cookies, $cookieStore, $window, $state, $timeout, createTalentFormService) {
    $scope.validMimeTypes = ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword', 'application/pdf'];
    $rootScope.attachedFilesData = [];
    $scope.FilesList = [];
    $scope.countError = false;
    $scope.fileCountExceededMsg = '';
    $scope.isDisabled = true;
    $scope.noFile = false;
    $scope.completedFiles = [];
    $scope.filesArr = [];

    $scope.filesExits = function () {
        var fileContainers = document.getElementsByClassName('dz-preview');
        for (var i = 0; i < fileContainers.length; i++) {
            if (fileContainers[i].classList.contains('dz-error') || !fileContainers[i].classList.contains('dz-complete')) {
                return true;
            }

        }
        return false;
    }
    //    $rootScope.dirOptions = {};
    //    $scope.callDirFunc = function () {
    //        $scope.dirOptions.clearFiles();
    //    };
    $scope.closePopup = function () {
        var file = $scope.filesExits();
        if (file) {
            $('#add-talent').modal('hide');
            $('#delete-popup').modal('show');
        } else {
            $scope.removeCompletedFiles();
            $('#add-talent').modal('hide');
        }
    }

    $scope.closeForcefully = function () {
        $state.go('dashboard', '');
        $scope.removeCompletedFiles();
        $('#delete-popup').modal('hide');
    }

    $scope.done = function () {
        $('#add-talent').modal('hide');
        $('#successBox').css('display', 'block');
        $scope.removeCompletedFiles();
        setTimeout(
            function () {
                $('#successBox').css('display', 'none');
                //            $state.go('talent.talent-search.talent-search-card', '');
            }, 2000);
    }

    $scope.reopen = function () {
        $('#delete-popup').modal('hide');
        $('#add-talent').modal('show');
    }

    var dropzoneIds = ['dropzone', 'dropzone_backgroundImg'];

    window.addEventListener("dragenter", function (e) {
        if (dropzoneIds.indexOf(e.target.id) == -1) {
            console.log('drag enter: ' + e.target.id)
            e.preventDefault();
            e.dataTransfer.effectAllowed = "none";
            e.dataTransfer.dropEffect = "none";
        }
    }, false);

    window.addEventListener("dragover", function (e) {
        if (dropzoneIds.indexOf(e.target.id) == -1) {
            console.log('drag over: ' + e.target.id)
            e.preventDefault();
            e.dataTransfer.effectAllowed = "none";
            e.dataTransfer.dropEffect = "none";
        }
    });

    window.addEventListener("drop", function (e) {
        console.log('drop: ' + e.target.id)
        if (dropzoneIds.indexOf(e.target.id) == -1) {
            e.preventDefault();
            e.dataTransfer.effectAllowed = "none";
            e.dataTransfer.dropEffect = "none";
        }
    });

    $scope.openCreateProfile = function () {
        createTalentFormService.setTalentDetails({});
        $('#add-talent').modal('hide');
        $state.go('talent.create-profile');
    }
}


function sideNavCtrl($scope, $rootScope, $location, $http, $cookies, $cookieStore, $window, $state, $timeout) {
    this.detectmob = function ($event) {
        if (navigator.userAgent.match(/Android/i) || navigator.userAgent.match(/webOS/i) || navigator.userAgent.match(/iPhone/i) || navigator.userAgent.match(/iPod/i) || navigator.userAgent.match(/BlackBerry/i) || navigator.userAgent.match(/Windows Phone/i)) {
            openSideMenu();
        }
    }

    function openSideMenu() {
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

    $scope.setActive = function ($event) {
        $event.stopPropagation();
        var childEle = $('.nav-first-level').children('.ch');
        angular.forEach(childEle, function (li) {
            if (!li.contains($event.target)) {
                if ($event.currentTarget.id != "project" && $('.nav-second-level').hasClass('in')) {
                    $('.nav-second-level').removeClass('in');
                    $('.nav-second-level').css('display', '');
                }
                angular.element(li).removeClass('active');
            }
        });

        if ($event.type == "touchstart") {
            if ($($event.currentTarget).hasClass('active')) {
                $($event.currentTarget).removeClass('active');
            } else {
                $($event.currentTarget).addClass('active');
                if ($event.currentTarget.id == "project") {
                    $('.nav-second-level').addClass('in');
                    $('.nav-second-level').css('display', 'block');
                }
            }
        } else if ($event.type == "click") {
            if ($(this).hasClass('active')) {
                $(this).removeClass('active');
            } else {
                $(this).addClass('active');
            }
        }
    }

    $scope.stateSelected = function () {
        if ($scope.stateArray.indexOf($state.current.name) > -1 && !$rootScope.isDevice) {
            $('#project').addClass('active');
            $('.nav-second-level').addClass('in');
            $('.nav-second-level').css('display', 'block');
            return true;
        }
        if ($scope.stateArray.indexOf($state.current.name) > -1 && $rootScope.isDevice) {
            $('#project').addClass('highlight');
            return true;
        }
        return false;
    }

}

function talentCtrl($scope, $rootScope, $location, $http, $cookies, $cookieStore, $window, $state, $timeout, talentApis, searchData, $cookieStore, createTalentFormService, $filter) {

    $scope.priceSlider = {
        value: 0,
        options: {
            floor: 0,
            ceil: 100,
            showSelectionBar: true
        }
    }

    $scope.exportOptions = [{
        name: 'Export Data',
        value: 'Export Data'
    }, {
        name: 'Copy',
        value: 'Copy'
    }, {
        name: 'CSV',
        value: 'CSV'
    }, {
        name: 'Excel',
        value: 'Excel'
    }, {
        name: 'PDF',
        value: 'PDF'
    }, {
        name: 'Print',
        value: 'Print'
    }]; // select drop-down options
    $scope.recordOptions = [{
        name: '10',
        value: '10'
        }, {
        name: '20',
        value: '20'
        }, {
        name: '30',
        value: '30'
        }, {
        name: '40',
        value: '40'
        }, {
        name: '50',
        value: '50'
        }] // select drop-down options
    $scope.exportType = $scope.exportOptions[0];
    //    $scope.recordCount = $scope.recordOptions[0];
    $scope.recordCount = "10";
    $scope.namePattern = /^[a-zA-Z\s]*$/;
    $rootScope.talentList = [];

    $scope.stagesName = {
        'Replied': 'fa-mail-reply',
        'Contacted': 'fa-phone',
        'Under Review': 'fa-file-text',
        'Interested': 'fa-thumbs-up',
        'Not Interested': 'fa-thumbs-down',
        'Scheduled for Interview': 'fa-briefcase',
        'Offer': 'fa-file-text-o',
        'Interviewing': 'fa-group',
        'Hired': 'fa-check',
        'Rejected': 'fa-user-times'
    };
    //$rootScope.talentDetails = ;
    $scope.selectedCandidate = {};
    $rootScope.selectedCandidateProfile = '';
    $scope.choosenCandidates = [];
    $scope.currentTalentId = '';
    //$scope.projectDD = $rootScope.projectListView[0];
    $rootScope.talentCountStart = 1;
    $rootScope.talentCountEnd = 0;
    $rootScope.totalTalentCount = 0;
    $scope.rating = 0;
    $scope.isEmailEditable = false;
    $scope.isEmailAdd = false;
    $scope.isContactEditable = false;
    $scope.isContactAdd = false;
    $scope.data = {};
    $rootScope.recruiter.recruiterName = $rootScope.globals.currentUser.first_name + ' ' + $rootScope.globals.currentUser.last_name;
    $scope.isName = false;
    $scope.isEmail = false;
    $scope.isContact = false;
    $scope.emailPattern = /^[a-z]+[a-z0-9._]+@[a-z]+\.[a-z.]{2,5}$/; //email validation pattern
    $scope.phonePattern = /^(?!0+$)\d{10,}$/;
    $scope.candidateInfo = {};
    $scope.data = {};
    //$scope.projectSelect ;
    $scope.tFilter = {
        stage: "0"
    };
    var stagesTemp = [];
    $scope.stage = {
        stage: '',
        project: '',
        date: '',
        detail: '',
        notes: '',
        isStage: false,
        stagesCard: $rootScope.talentAllStages ? $rootScope.talentAllStages : stagesTemp
    };
    $scope.isStage = false;
    $scope.isProject = false;
    $scope.isDate = false;
    $scope.isDetail = false;
    $scope.isNotes = false;
    $scope.filterValue = {
        //stage:'Select Stage',
        project: '',
        match: $scope.priceSlider.value + '%',
        rating: '',
        lastContacted: '',
        analysed: '',
        company: '',
        concepts: '',
        recruiter_name: '',
        ordering: '',
        active: ''
    };
    $rootScope.Filter = false;
    /*edit talent details*/

    /* create talent code */
    $scope.notification = {
        show: false,
        status: 'wow',
        message: ''
    };
    $scope.talentData = {};
    $scope.showNotification = function (success, message) {
        $timeout(function () {
            $scope.notification.show = true;
            $scope.notification.status = success ? 'Success' : 'Error';
            $scope.notification.message = message;
        });
        $timeout(function () {
            $scope.notification.show = false;
        }, 3000);
    }

    $scope.disableUploadBtn = false;
    $scope.todayDate = new Date();
    $scope.imageFileName = '';
    $scope.talentFileobj = {};

    //    $rootScope.editTalentDetail = function (data) {
    //        $timeout(function(d){
    //            a.talentData = d;
    //            console.log($scope.talentData)
    //        }, 3000, true, data);
    //        
    //    };

    $scope.$watch('talentFileobj.name', function (newVal, oldVal) {
        if ($scope.talentFileobj.name) {
            $scope.uploadTalentFile();
        }
    });

    $scope.onFileLoad = function (e) {
        var file = e.files[0];
        $scope.talentFileobj = e.files[0];
        $timeout(function () {
            $scope.$apply();
        });
        e.value = "";
        //        $scope.uploadTalentFile();
    };

    $scope.removeFile = function () {
        $scope.talentFileobj = {};
        //        $scope.talentData.topConcepts = [{}];
        createTalentFormService.setTalentDetails({});
        $scope.initTalenData();
    }

    $scope.uploadTalentFile = function () {
        $scope.disableUploadBtn = true;
        createTalentFormService.uploadTalentFile($scope.talentFileobj, function (response) {
            $(".top-concepts-panel").css('display', 'block');
            if (typeof (response) == "string")
                response = JSON.parse(response);
            if (response.success) {
                //                $scope.talentData = response.results;
                for (var key in response.results) {
                    $scope.talentData[key] = response.results[key];
                }
            } else {
                $scope.showNotification(false, response.errorstring || 'Error in fetching data from pdf');
                $window.scrollTo(0, 0);
                $scope.disableUploadBtn = false;
            }
            console.log(response);
        });
    }

    var d = new Date().getFullYear();
    $scope.yearArr = [];
    for (var i = 80; i >= 0; i--) {
        $scope.yearArr[i] = d - i;
    }

    $scope.talentDataValidation = {
        phone: true
    };
    $scope.initTalenData = function () {
        var details = createTalentFormService.getTalentDetails();
        if (Object.keys(details).length) {
            $scope.talentData = details;
            return;
        }

        $scope.talentData = {
            profile_image: '',
            industryFocus: {
                name: '',
                percentage: ''
            },
            currentOrganization: [{
                name: '',
                from: '',
                to: 'Present'
        }],
            pastOrganization: [{
                name: '',
                from: '',
                to: ''
        }],
            education: [{
                name: '',
                from: '',
                to: ''
        }],
            topConcepts: [],
            careerHistory: {
                total: '',
                history: [{}]
            }
        };
    }
    $scope.initTalenData();
    $scope.addEducation = function () {
        $scope.talentData.education.push({
            name: '',
            from: '',
            to: ''
        });
    }
    $scope.addSkill = function () {
        $scope.talentData.topConcepts.unshift({});
    }
    $scope.addTalentCareerHistory = function () {
        $scope.talentData.careerHistory.history.push({});
    }
    $scope.addTalentPast = function () {
        $scope.talentData.pastOrganization.push({
            name: '',
            from: '',
            to: ''
        });
    }

    $scope.addCurrentOrganization = function () {
        $scope.talentData.currentOrganization.push({
            name: '',
            from: '',
            to: ''
        });
    }

    $scope.removeIndexFromArr = function (arr, index) {
        arr.splice(index, 1);
    }
    $scope.checkPhoneNumberLength = function (number, maxLength) {
        var phone = angular.copy(number);
        phone = phone.replace(/-/g, '');
        if (phone && phone.length && phone.length < maxLength || phone.length > maxLength) {
            $scope.talentDataValidation.phone = false;
        } else {
            $scope.talentDataValidation.phone = true;
        }
    }

    $scope.removeTopConcepts = function (arr, index) {
        //        arr.splice(index, 1);
        //            return;
        if (!$scope.talentData.id) {
            arr.splice(index, 1);
            return;
        }

        var removeObj = arr[index];

        if (!removeObj.id) {
            arr.splice(index, 1);
            return;
        }

        createTalentFormService.removeTopConcepts({
            id: removeObj.id,
            talent_id: $scope.talentData.id
        }, function (response) {
            if (response.success) {
                arr.splice(index, 1);
                if (!arr.length) {
                    $("#view-all-concepts").modal('hide');
                }
            } else {
                $('#view-all-concepts').modal('hide');
                $scope.showNotification(false, response.errorstring || 'Error in removing concept.');
                $window.scrollTo(0, 0);
            }
        });
    }

    $scope.removeCurrentOrganization = function (arr, index) {
        if (!$scope.talentData.id) {
            arr.splice(index, 1);
            return;
        }

        var removeObj = arr[index];

        if (!removeObj.id) {
            arr.splice(index, 1);
            return;
        }

        createTalentFormService.removePastOrganization({
            id: removeObj.id,
            talent_id: $scope.talentData.id
        }, function (response) {
            if (response.success) {
                arr.splice(index, 1);
            } else {
                $scope.showNotification(false, response.errorstring || 'Error in removing current organisation.');
            }
        });
    }

    $scope.removePastOrganization = function (arr, index) {
        if (!$scope.talentData.id) {
            arr.splice(index, 1);
            return;
        }

        var removeObj = arr[index];

        if (!removeObj.id) {
            arr.splice(index, 1);
            return;
        }

        createTalentFormService.removePastOrganization({
            id: removeObj.id,
            talent_id: $scope.talentData.id
        }, function (response) {
            if (response.success) {
                arr.splice(index, 1);
            } else {
                $scope.showNotification(false, response.errorstring || 'Error in removing past organisation.');
            }
        });
    }

    $scope.removeTalentEducation = function (arr, index) {
        if (!$scope.talentData.id) {
            arr.splice(index, 1);
            return;
        }
        var removeObj = arr[index];
        if (!removeObj.id) {
            arr.splice(index, 1);
            return;
        }
        createTalentFormService.removeTalentEducation({
            id: removeObj.id,
            talent_id: $scope.talentData.id
        }, function (response) {
            if (response.success) {
                arr.splice(index, 1);
            } else {
                $scope.showNotification(false, response.errorstring || 'Error in education.');
            }
        });
    }


    $scope.fetchLinkedinData = function () {
        if (!$scope.talentData.linkedinProfileUrl) return;
        var param = {
            url: $scope.talentData.linkedinProfileUrl
        }
        if ($scope.talentData.id) {
            param.id = $scope.talentData.id
        }

        //        $scope.talentData.profile_image = '';
        //        $scope.talentData.firstName = '';
        //        $scope.talentData.lastName = '';
        //        $scope.talentData.email = '';
        //        $scope.talentData.phone = '';
        //        $scope.talentData.city = '';
        //        $scope.talentData.state = '';
        //        $scope.talentData.country = '';
        //        $scope.talentData.industryFocus = '';
        //        $scope.talentData.currentOrganization = [{
        //            name: ''
        //            , from: ''
        //            , to: 'Present'
        //        }];
        //        $scope.talentData.pastOrganization = [{
        //            name: ''
        //            , from: ''
        //            , to: ''
        //        }];
        //        $scope.talentData.education = [{
        //            name: ''
        //            , from: ''
        //            , to: ''
        //        }];
        //        $scope.talentData.careerHistory = {
        //            total: ''
        //            , history: [{}]
        //        };

        talentApis.addLinkedinUrl(param, function (response) {
            console.log(response);
            if (response.success) {
                // delete response.results.linkedinProfileUrl;
                //                for (var key in response.results) {
                for (var key in response.results) {
                    $scope.talentData[key] = response.results[key];
                }
                $('#linkedinUrl').blur();
            } else {
                $scope.showNotification(false, response.errorstring);
                $window.scrollTo(0, 0);
            }
        })
    }

    $scope.createTalent = function (data, onEdit) {
        if (data.phone && data.phone.length < 10) return;
        var valid = true;
        if (data.topConcepts) {
            data.topConcepts.forEach(function (concept) {
                if (concept.percentage > 100) {
                    valid = false;
                }
            })
        }

        if (!valid) return;

        data.id ? data.request_by = 'edit' : data.request_by = "create";

        createTalentFormService.createTalent(data, function (response) {
            if (response.success) {
                if (onEdit) {
                    for (var i = 0; i < $rootScope.talentList.length; i++) {
                        if (response.talent_updated_data.id == $rootScope.talentList[i].id) {
                            $rootScope.talentList[i] = response.talent_updated_data;
                        }
                    }
                    $('#edit-profile').modal('hide');
                    $scope.showNotification(true, 'Talent profile has been updated successfully.');
                    //$rootScope.getCandidateData();
                } else {
                    $scope.initTalenData();
                    //                    $scope.showNotification(true, 'Talent profile has been created successfully.');
                    $state.go('talent.talent-search.talent-search-card');
                    $rootScope.getCandidateData();
                }
                createTalentFormService.setTalentDetails({});
            } else {
                if (onEdit) {
                    $('#edit-profile').modal('hide');
                }
                $scope.showNotification(false, response.errorstring);
            }
            $window.scrollTo(0, 0);
        });
    }

    /* linkedin url add */
    $scope.linkedinUrlPattern = /^(?:(?:(?:https?|ftp):)?\/\/)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:[/?#]\S*)?$/i;
    $scope.candidate = {};
    $scope.openLinkedinPopup = function (event, selectedTalentId) {
        event.preventDefault();
        event.stopPropagation();
        $scope.candidate.linkedinProfileUrl = '';
        $scope.candidate.id = selectedTalentId;
        $('#add-url').modal('show');
    }

    $scope.addLinkedUrl = function () {
        console.log($scope.candidate.id);
        var url = $scope.candidate.linkedinProfileUrl;
        if (url) {
            var requestObject = {
                'id': $scope.candidate.id, // password field value
                'url': url
            };
            talentApis.addLinkedinUrlCard(requestObject, function (response) {
                $('#add-url').modal('hide');
                //                $('html, body').animate({
                //                    scrollTop: 0
                //                }, 'fast');
                if (response.success) {
                    //$scope.showNotification(true, 'Linkedin URL added successfully.');
                    $scope.candidate = {};
                    $rootScope.getCandidateData();
                } else {
                    console.log('error');
                    $scope.showNotification(false, response.errorstring);
                    $window.scrollTo(0, 0);
                }
            });
        }

    }

    /*end of linkedin url code*/

    $scope.gotoState = function (state) {
        $scope.initTalenData();
        $rootScope.getCandidateData();
        $state.go(state);
    }
    $scope.numberonly = function (obj, key, isPercentage) {
        if (typeof (obj[key]) == "string")
            obj[key] = obj[key].replace(/\D+/g, '');

        if (obj[key] > 100)
            obj[key] = 100;
    }

    $scope.contactFormat = function (obj, key) {
        if (obj[key] && obj[key] != "string") {
            obj[key] = obj[key].replace(/(^0$)|[^0-9]/g, "");
        }
        var regexPhoneNumber = /^(1-?)?(\([2-9]\d{2}\)|[2-9]\d{2})-?[2-9]\d{2}-?\d{4}$/;
        if (obj[key] && obj[key].match(regexPhoneNumber)) {
            obj[key] = obj[key].toString();
            obj[key] = obj[key].substr(0, 3) + '-' + obj[key].substr(3);
            obj[key] = obj[key].substr(0, 7) + '-' + obj[key].substr(7);
        } else if (typeof (obj[key]) == "string") {
            obj[key] = obj[key].replace(/\D+/g, '');
        }
    }
    /* create talent code ends */

    $scope.$watch('priceSlider.value', function (n, o) {
        $scope.filterValue.match = n + '%';
    })

    $scope.hideMessages = function (formName) { /*Hide error messages when user interact with fieds*/
        $('#name-required').addClass('ng-hide');
        $scope.isName = false;
        $('#' + formName + 'input').each(function () {
            var spanClass = $(this).next('span').attr('class');
            if ($(this).val().length <= 0 && ($(this).next('span').hasClass('error'))) {
                $(this).next('span').removeClass('error').text("");
            } else if ($(this).val().length > 0 && ($(this).next('span').hasClass('error'))) {
                $(this).next('span').removeClass('error').text("");
            }
        });
    }

    $scope.$on('ngRepeatFinished', function (ngRepeatFinishedEvent) { // table responsiveness initialization after data render
        $(".select-arrow").selectbox();
        $('#export').change(function () {
            $rootScope.isFilterChecked = false;
            var selectedValue = $('#export :selected').text();
            $scope.exportType = selectedValue;
        });
        $('#filter_form input').on('change', function () {
            $scope.filterValue.ordering = $('input[name=ordering]:checked', '#filter_form').val();
            $scope.filterValue.active = $('input[name=active]:checked', '#filter_form').val();
        });
        $('#projectListD').change(function () {
            /*var selectedValue = $('#projectListD').val();
            $scope.projectDD = selectedValue;
            console.log($scope.projectDD);*/
            $scope.projectRequired = false;
            $('#proj_required').addClass('ng-hide');
        });
        // var oldie = $.browser.msie && $.browser.version < 9;

    });

    $scope.calcIntegerVal = function (a, b) {
        return parseInt(a / b);
    }

    $scope.$watch('candidatePagination.page + candidatePagination.count', function () {
        //        if ($rootScope.getCandidateData)
        //            $rootScope.getCandidateData(true);

        if ($rootScope.globalSearch) {
            if ($rootScope.getCandidateData)
                $rootScope.getCandidateData(true);
        } else {
            if ($scope.filterData)
                $scope.filterData();
        }
    });

    //    $scope.changePage = function (add, pageNo) {
    //
    //        if (pageNo) {
    //            if ($scope.candidatePagination.page == pageNo) {
    //                return;
    //            }
    //            $scope.candidatePagination.page = pageNo;
    //            $rootScope.getCandidateData();
    //            return;
    //        }
    //
    //        if (add) {
    //            if (Math.ceil($rootScope.totalTalentCount / $scope.candidatePagination.count) == $scope.candidatePagination.page) {
    //                return;
    //            }
    //            $scope.candidatePagination.page += 1;
    //        } else {
    //            if ($scope.candidatePagination.page == 1) return;
    //            $scope.candidatePagination.page -= 1;
    //        }
    //        //        $rootScope.$emit('fetchCandidateData');
    //        $rootScope.getCandidateData();
    //    }


    angular.element(document).ready(function () {
        //        $scope.getTalents();
        //        if ($rootScope.getCandidateData) {
        //            $rootScope.getCandidateData();
        //        }else{
        //            console.log("FAILED to fetch candidate data");
        //        }

        //        $rootScope.$emit('fetchCandidateData');

    });



    $scope.getSelectedRating = function (rating) {
        //console.log(rating);
        // console.log($rootScope.talentDetails.id);
        console.log(rating);
        /*       if(rating >=1){
                   $scope.stars = [];
                   $scope.stars.push({
                               filled: true
                           });
               }*/
        if (rating >= 0) {
            var requestObject = {
                'id': $rootScope.talentDetails.id, // password field value
                'rating': rating
            };
            talentApis.updateRatings(requestObject).then(function (response) {
                if (response.message == "success") {
                    console.log('success');
                    $rootScope.talentDetails.rating = rating;
                    sessionStorage.talentDetails = JSON.stringify($rootScope.talentDetails);
                } else {
                    console.log('error');
                }
            });
        }
    }

    $scope.filterChanged = 0;
    $rootScope.candidatePagination = {
        page: 1,
        count: parseInt($scope.recordCount)
    }
    $scope.getcandidateData = function () {
        //        $rootScope.getCandidateData();
        //        $rootScope.$emit('fetchCandidateData');
        $rootScope.getCandidateData()
    }
    $scope.changeState = function () {

        $rootScope.candidatePagination.page = 1;

        $scope.choosenCandidates = [];
        $rootScope.isFilterChecked = false;
        $('.talent-search-icon').removeClass('active');
        $('#selectall').prop('checked', false);
        $('#assignToProject').removeClass('add-talent');
        $('#assignToProject').addClass('disabled-talent');
        var currentState = $state.current.name;
        if (currentState == 'talent.talent-search.talent-search-card') {
            $('.bar-view').removeClass('active');
            $('.table-view').addClass('active');
            $state.go('talent.talent-search.talent-search-list', '');
        }

        if (currentState == 'talent.talent-search.talent-search-list') {
            $('.bar-view').addClass('active');
            $('.table-view').removeClass('active');
            $state.go('talent.talent-search.talent-search-card', '');
        }
    }
    $scope.stageIdToBeDeleted = null;
    $scope.setScopeVariable = function (variable, value) {
        $scope[variable] = value;
    }
    $scope.deleteStage = function (id) {
        if (!id) return;
        talentApis.delteStage({
            stage_id: id,
            talent_id: $rootScope.talentDetails.id
        }, function (response) {
            console.log(response);
            if (response.success) {
                //$scope.showNotification(true, 'Stage has been successfully removed');

                $scope.talentDetails = response.result;
                $rootScope.talentAllStages = response.result.talent_stages;

                $scope.loadProfileData($rootScope.talentDetails.id, $rootScope.talentDetails, 'deleteStage');
                $rootScope.talentAllStages = response.result.talent_stages;
                $scope.stage.stagesCard = response.result.talent_stages;
                sessionStorage.removeItem('talentAllStages');
                sessionStorage.talentAllStages = JSON.stringify($scope.stage.stagesCard);
            } else {
                $scope.showNotification(false, response.errorstring || 'Some problem occured');
            }
            $('#delteStageModal').modal('hide');
            $window.scroll(0, 0);

        });
    }
    /*  edit-stage code start */
    function convertToIso(date) {
        var d = date.split('/');
        d = d[1] + '/' + d[0] + '/' + d[2];
        d = new Date(d);
        //d = d.toISOString();
        return d;
    }
    $scope.editStageModal = function (selectedStage) {
        console.log(selectedStage);
        initDatePicker('editStageDate');
        $scope.selectedStage = {};
        $scope.selectedStage.stage = selectedStage.stage;
        $scope.selectedStage.project = selectedStage.project;
        $scope.selectedStage.create_date = convertToIso(selectedStage.create_date);
        $scope.selectedStage.details = selectedStage.details;
        $scope.selectedStage.notes = selectedStage.notes;
        $scope.selectedStage.stage_id = selectedStage.id;
        $('#edit-stage').modal('show');
    }

    $scope.saveProjectStage = function () {
        console.log($scope.selectedStage);
        $scope.selectedStage.create_date = $rootScope.formatDate($('#editStageDate').val());
        //            $scope.selectedStage.create_date = $rootScope.formatDate($scope.selectedStage.create_date);
        var requestObj = $scope.selectedStage;
        requestObj.talent_id = $rootScope.talentDetails.id;
        talentApis.editStage(requestObj, function (response) {
            if (response.message == 'success') {

                $scope.talentDetails = response.result;

                $rootScope.talentAllStages = response.result.talent_stages;
                $scope.stage.stagesCard = response.result.talent_stages;
                sessionStorage.removeItem('talentAllStages');
                sessionStorage.talentAllStages = JSON.stringify($scope.stage.stagesCard);
                $('#edit-stage').modal('hide');
                $scope.showNotification(true, 'Stage has been updated Successfully.');
            } else if (response.success == false) {
                $('#edit-stage').modal('hide');
                $scope.showNotification(true, 'Stage has been updated Successfully.');
            }
            $window.scrollTo(0, 0);
        });
    }
    /* edit-stage code end */

    $scope.getTalents = function (recordCount) { // function to fetch top 6 projects

        $rootScope.candidatePagination.page = 1;
        $rootScope.candidatePagination.count = parseInt(recordCount);
        //        $scope.getcandidateData();

        //        if (recordCount) {
        //            var count = recordCount;
        //        } else {
        //            var count = $scope.recordCount.value;
        //        }
        //        var requestObject = {
        //            'token': $rootScope.globals.currentUser.token, // username field value
        //            'recruiter': $rootScope.globals.currentUser.user_email, // password field value
        //            'count': count
        //        };
        //        talentApis.getAllTalents(requestObject).then(function (response) {
        //            if (response.message == "success") {
        //                $rootScope.talentList = response.talent_list;
        //                $scope.recruiter.recruiterName = response.display_name;
        //                $rootScope.totalTalentCount = response.count;
        //                $rootScope.talentCountEnd = response.talent_list.length;
        //            } else {
        //                console.log('error');
        //            }
        //        });
    }

    $scope.updateRecruiterName = function (name) { // function to fetch top 6 projects
        //console.log(name);
        if (name) {
            $rootScope.recruiter.recruiterName = name;
            //            $('#nameUpdate').addClass('disabled');
            //            $('#nameUpdate').css('pointer-events', 'none');
            var requestObject = {
                'recruiter': $rootScope.globals.currentUser.user_email, // password field value
                'display_name': $rootScope.recruiter.recruiterName
            };
            talentApis.updateRecruiterName(requestObject).then(function (response) {
                if (response.message == "success") {
                    //console.log(response);
                    $('html, body').animate({
                        scrollTop: 0
                    }, 'fast');
                    $('#edit-recruiter').modal('hide');
                    $('#nameSuccess').css('display', 'block');
                    setTimeout(
                        function () {
                            $('#nameSuccess').css('display', 'none');
                        }, 1000);
                } else {
                    console.log('error');
                }
            });
        } else {
            $('#name-required').removeClass('ng-hide');
            $scope.isName = true;
        }
    }

    $scope.selectExportType = function (exportType) {
        //console.log('asdasdasdasd');
        console.log(exportType.value);
    }

    $scope.calcTotal = function (filtered, name) {
        var sum = 0;
        for (var i = 0; i < filtered.length; i++) {
            sum = sum + Math.round(filtered[i].years_of_experience * 100) / 100;
            sum = sum + Math.round(filtered[i].career_gap * 100) / 100;
        }
        return sum;
    };

    $scope.loadProfileData = function (id, talent, callFrom) {
        $rootScope.isFilterChecked = false;
        if (talent && id) {
            $rootScope.talentDetails = talent;
        }
        var requestObject = {
            'token': $rootScope.globals.currentUser.token, // username field value
            'recruiter': $rootScope.globals.currentUser.user_email, // password field value
            'id': id
        };
        talentApis.getCandidateProfile(requestObject).then(function (response) {
            //$state.go('talent.talent-profile','');
            //$('html, body').animate({ scrollTop: 0 }, 'fast');
            if (callFrom == 'deleteStage') {
                $window.scroll(0, 0);
                $scope.showNotification(true, 'Stage has been successfully removed');
            }
            var a = [response];
            $rootScope.createCareerHistoryData(a);

            $rootScope.talentDetails = a[0];
            sessionStorage.talentDetails = JSON.stringify($rootScope.talentDetails);
            getTalentStages(id);
        });

    }

    function getTalentStages(id) {
        $rootScope.talentAllStages = [];
        var requestObject = {
            'token': $rootScope.globals.currentUser.token, // username field value
            'recruiter': $rootScope.globals.currentUser.user_email, // password field value
            'talent_id': id
        };
        talentApis.getTalentAllStages(requestObject).then(function (response) {
            $state.go('talent.talent-profile', '');
            $rootScope.talentAllStages = response.result;
            $scope.stage.stagesCard = '';
            $scope.stage.stagesCard = response.result;
            $('html, body').animate({
                scrollTop: 0
            }, 'fast');
            sessionStorage.removeItem('talentAllStages');
            sessionStorage.talentAllStages = JSON.stringify($rootScope.talentAllStages);
        });

    }


    $scope.showDetails = function (talent) {
        $scope.selectedCandidate = talent;
        $('#more-comp').modal('show');

    }

    $scope.showRecruiterPopup = function (talent) {
        $scope.selectedCandidate = talent;
        $('#recruiter-modal').modal('show');

    }
    $scope.isName = false;
    $scope.editRecruiter = function () {
        $scope.isName = false;
        $scope.data.recruiterNameInput = $rootScope.recruiter.recruiterName;
        //        $('#nameUpdate').removeClass('disabled');
        //        $('#nameUpdate').css('pointer-events', '');
        $('#recruiter-modal').modal('hide');
        $('#edit-recruiter').modal('show');
    }

    $scope.closeUpdateRecruiter = function () {
        //$scope.data.recruiterNameInput = '';
        $('#edit-recruiter').modal('hide');

    }

    $scope.openProjectList = function (id, callFrom) {
        $scope.data.projectName = '';
        $scope.projectRequired = false;
        if (id) {
            $scope.currentTalentId = id;
        } else {
            $scope.currentTalentId = '';
        }
        $('#add-talent-btn').removeClass('disabled');
        $('#add-talent-btn').css('pointer-events', '');
        $('.selectpicker').selectpicker();
        //if (callFrom == 'profile') {
        //$('.dropdown-toggle').attr('title','Select Project');
        //$('.filter-option').text('Select Project');
        //$('.inner').find('li').removeAttr('class');
        // $('.dropdown-menu').val('');

        //}
        $("#projectListD").val('').selectpicker('refresh');
        $scope.data.projectRequired = false;
        $('#proj_required').addClass('ng-hide');
        $('#add-project').modal('show');
    }

    $scope.addToProject = function (projectDD, callFrom) {
        if (!projectDD) {
            $scope.data.projectRequired = true;
            return;
        }
        var selectedProjectId;
        console.log($scope.data.projectName);
        var talent = [];
        if (projectDD == undefined) {
            $scope.projectRequired = true;
            $('#proj_required').removeClass('ng-hide');
            return;
        }
        if (typeof (projectDD) != 'object' && projectDD != undefined) {
            for (var i = 0; i < $rootScope.allProjectList.length; i++) {
                if ($rootScope.allProjectList[i].project_name == projectDD.split('#')[1]) {
                    selectedProjectId = $rootScope.allProjectList[i].id;
                    break;
                }
            }
        }
        if ($scope.currentTalentId != '') {
            talent.push($scope.currentTalentId);

        } else if ($scope.choosenCandidates.length > 0) {
            for (var k = 0; k < $scope.choosenCandidates.length; k++) {
                talent.push($scope.choosenCandidates[k]);
            }

        }

        if (selectedProjectId && talent.length > 0) {
            $('#add-talent-btn').addClass('disabled');
            $('#add-talent-btn').css('pointer-events', 'none');
            var requestObject = {
                'recruiter': $rootScope.globals.currentUser.user_email, // password field value
                'token': $rootScope.globals.currentUser.token,
                'project_id': selectedProjectId,
                'talent': talent
            };
            talentApis.addTalentsToProject(requestObject).then(function (response) {
                //console.log(response);
                if (!callFrom) {
                    //                    $rootScope.$emit('fetchCandidateData');
                    $rootScope.getCandidateData();
                    //                    $rootScope.talentList = response;
                    $scope.choosenCandidates == [];
                    $('#selectall').prop('checked', false);
                    $('#assignToProject').removeClass('add-talent');
                    $('#assignToProject').addClass('disabled-talent');
                    $('#assignToProject').css('pointer-events', 'none');
                    $('#talent-delete').css('pointer-events', 'none');

                    $('#talent-delete').css('background-color', '');
                    $('#add-project').modal('hide');
                    //                    $('html, body').animate({
                    //                        scrollTop: 0
                    //                    }, 'fast');
                    $('#projectSuccess').css('display', 'block');
                    setTimeout(function () {
                        $('#projectSuccess').css('display', 'none');
                    }, 2000);
                } else if (callFrom == 'profile') {
                    $('#add-project').modal('hide');
                    $('html, body').animate({
                        scrollTop: 0
                    }, 'fast');
                    $('#projectSuccess').css('display', 'block');
                    setTimeout(function () {
                        $('#projectSuccess').css('display', 'none');
                    }, 2000);
                    for (var i = 0; i < response.length; i++) {
                        if (response[i].id == $scope.currentTalentId) {
                            $rootScope.talentDetails = response[i];
                            sessionStorage.talentDetails = JSON.stringify($rootScope.talentDetails);
                        }
                    }
                    $('.selectpicker').selectpicker();

                }
            });


        }
    }


    $scope.updateSelection = function (id, position, talentList) {

        if ($scope.choosenCandidates.indexOf(id) == -1) {
            $scope.choosenCandidates.push(id);
            if ($scope.choosenCandidates.length == $rootScope.talentList.length)
                $('#selectall').prop('checked', true);
        } else {
            $('#selectall').prop('checked', false);
            $scope.choosenCandidates.splice($scope.choosenCandidates.indexOf(id), 1);
        }
        if ($scope.choosenCandidates.length > 0) {
            $('#assignToProject').removeClass('disabled-talent');
            $('#assignToProject').addClass('add-talent');
            $('#assignToProject').css('pointer-events', '');
            $('#talent-delete').css('pointer-events', '');

            $('#talent-delete').css('background-color', '#e7eaec');
        } else {
            $('#assignToProject').removeClass('add-talent');
            $('#assignToProject').addClass('disabled-talent');
            $('#talent-delete').css('pointer-events', 'none');

            $('#talent-delete').css('background-color', '');
            $('#assignToProject').css('pointer-events', 'none');
        }
        //console.log($scope.choosenCandidates);
    }

    $scope.selectAll = function () {
        var state = $('#selectall').prop('checked');
        if (state) {
            $scope.choosenCandidates = [];
            for (var i = 0; i < $rootScope.talentList.length; i++) {
                $('#check_' + $rootScope.talentList[i].id).prop('checked', true);
                $scope.choosenCandidates.push($rootScope.talentList[i].id);
            }
        } else {
            for (var i = 0; i < $rootScope.talentList.length; i++) {
                $('#check_' + $rootScope.talentList[i].id).prop('checked', false);
                $scope.choosenCandidates.splice($scope.choosenCandidates.indexOf($rootScope.talentList[i].id), 1);
            }
        }
        if ($scope.choosenCandidates.length > 0) {
            $('#assignToProject').removeClass('disabled-talent');
            $('#assignToProject').addClass('add-talent');
            $('#assignToProject').css('pointer-events', '');
            $('#talent-delete').css('pointer-events', '');

            $('#talent-delete').css('background-color', '#e7eaec');
        } else {
            $('#assignToProject').removeClass('add-talent');
            $('#assignToProject').addClass('disabled-talent');
            $('#talent-delete').css('pointer-events', 'none');
            $('#assignToProject').css('pointer-events', 'none');

            $('#talent-delete').css('background-color', '');
        }
    }

    $scope.deleteTalents = function () {
        $rootScope.isFilterChecked = false;
        $('#delete-talent-popup').modal('show');
    }

    $scope.deleteTalentsConfirm = function () {
        var talent = [];
        if ($scope.choosenCandidates.length > 0) {
            for (var k = 0; k < $scope.choosenCandidates.length; k++) {
                talent.push($scope.choosenCandidates[k]);
            }

        }

        if (talent.length > 0) {
            //$('#confirm').addClass('disabled');
            //$('#confirm').css('pointer-events', 'none');
            var requestObject = {
                'recruiter': $rootScope.globals.currentUser.user_email, // password field value
                'talent': talent,
                'is_active': 'False'
            };
            //$('#delete-talent-popup').modal('hide');
            talentApis.deleteTalents(requestObject).then(function (response) {
                if (response) {
                    $rootScope.search.searchKeywords = '';
                    $('.talent-search-icon').removeClass('active');
                    $rootScope.isFilterChecked = false;
                    $rootScope.filterReset();
                    $rootScope.getCandidateData();
                    //                    $rootScope.talentList = response;
                    //                    var count = talent.length
                    //                    $rootScope.totalTalentCount = $rootScope.totalTalentCount - count;
                    //                    $rootScope.talentCountEnd = response.length;
                    $('#selectall').prop('checked', false);
                    $('#assignToProject').removeClass('add-talent');
                    $('#assignToProject').addClass('disabled-talent');
                    $('#assignToProject').css('pointer-events', 'none');
                    $('#talent-delete').css('pointer-events', 'none');

                    $('#talent-delete').css('background-color', '');
                    $('#delete-talent-popup').modal('hide');
                    $('html, body').animate({
                        scrollTop: 0
                    }, 'fast');
                    $('#deleteSuccess').css('display', 'block');
                    setTimeout(
                        function () {
                            $('#deleteSuccess').css('display', 'none');
                        }, 2000);
                } else {
                    console.log('error');
                }
            });
        }
    }

    $scope.showEdit = function (talentEmail) {
        $scope.isEmailAdd = false;
        $scope.isContactEditable = false;
        $scope.isContactAdd = false;
        if (!$scope.isEmailEditable) {
            $scope.candidateInfo.candidateEmail = talentEmail[0].email;
            $scope.isEmailEditable = true;
        } else if ($scope.isEmailEditable) {
            $scope.isEmailEditable = false;
        }
    }

    $scope.showAdd = function () {
        console.log($scope.addEmailForm);
        $scope.isEmailEditable = false;
        $scope.isContactEditable = false;
        $scope.isContactAdd = false;
        if (!$scope.isEmailAdd) {
            $scope.isEmailAdd = true;
        } else if ($scope.isEmailAdd) {
            $scope.isEmailAdd = false;
        }
    }

    $scope.showContactEdit = function (talentContact) {
        $scope.isContactAdd = false;
        $scope.isEmailEditable = false;
        $scope.isEmailAdd = false;
        if (!$scope.isContactEditable) {
            $scope.candidateInfo.candidateContact = talentContact[0].contact;
            $scope.isContactEditable = true;
        } else if ($scope.isContactEditable) {
            $scope.isContactEditable = false;
        }
    }

    $scope.showContactAdd = function () {
        $scope.isContactEditable = false;
        $scope.isEmailEditable = false;
        $scope.isEmailAdd = false;
        if (!$scope.isContactAdd) {
            $scope.isContactAdd = true;
        } else if ($scope.isContactAdd) {
            $scope.isContactAdd = false;
        }
    }

    $scope.talentSorted = '';
    $scope.tListsorted = true;
    $scope.sortArrayByDate = function (arr, arrKey, key) {
        var sorted = false;
        if (key == $scope.talentSorted && $scope.tListsorted) {
            arr = arr.reverse();
        } else if (key == $scope.talentSorted && !$scope.tListsorted) {
            return;
        } else {
            $scope.talentSorted = key;
            arr.sort(function (a, b) {

                var str1 = 0,
                    str2 = 0;

                if (a[arrKey].length && a[arrKey][0][key]) {
                    var d = a[arrKey][0][key].replace(/^(\d{1,2}\/)(\d{1,2}\/)(\d{4})$/, "$2$1$3");
                    str1 = new Date(d).getTime();
                }

                if (b[arrKey].length && b[arrKey][0][key]) {
                    var d = b[arrKey][0][key].replace(/^(\d{1,2}\/)(\d{1,2}\/)(\d{4})$/, "$2$1$3");
                    str2 = new Date(d).getTime()
                }
                if (str1 - str2 != 0) {
                    sorted = true;
                }

                return str1 - str2;
            });
            sorted ? $scope.tListsorted = true : $scope.tListsorted = false;
        }
    }

    $scope.sortAnalysedDate = function (arr, arrKey, key) {
        var sorted = false;
        if (key == $scope.talentSorted && $scope.tListsorted) {
            arr = arr.reverse();
        } else if (key == $scope.talentSorted && !$scope.tListsorted) {
            return;
        } else {
            $scope.talentSorted = key;
            arr.sort(function (a, b) {

                var str1 = a.create_date.split(' ')[0].replace(/^(\d{1,2}\/)(\d{1,2}\/)(\d{4})$/, "$2$1$3");
                var str2 = b.create_date.split(' ')[0].replace(/^(\d{1,2}\/)(\d{1,2}\/)(\d{4})$/, "$2$1$3");;

                str1 = new Date(str1).getTime();
                str2 = new Date(str2).getTime();

                if (a[arrKey].length && a[arrKey][0][key]) {
                    var d = a[arrKey][0][key].replace(/^(\d{1,2}\/)(\d{1,2}\/)(\d{4})$/, "$2$1$3");
                    str1 = new Date(d).getTime();
                }

                if (b[arrKey].length && b[arrKey][0][key]) {
                    var d = b[arrKey][0][key].replace(/^(\d{1,2}\/)(\d{1,2}\/)(\d{4})$/, "$2$1$3");
                    str2 = new Date(d).getTime()
                }

                if (str1 != str2) {
                    sorted = true;
                }

                return str1 - str2;
            });
            sorted ? $scope.tListsorted = true : $scope.tListsorted = false;
        }
    }

    $scope.sortjsonArray = function (arr, arrKey, key, lastIndex) {
        var index1 = 0,
            index2 = 0,
            sorted = false;
        if (key == $scope.talentSorted && $scope.tListsorted) {
            arr = arr.reverse();
        } else if (key == $scope.talentSorted && !$scope.tListsorted) {
            return;
        } else {
            $scope.talentSorted = key;
            arr.sort(function (a, b) {

                var str1 = null,
                    str2 = null;

                if (!a[arrKey].length) {
                    str1 = '';
                };

                if (!b[arrKey].length) {
                    str2 = '';
                };
                if (lastIndex) {
                    index1 = a[arrKey].length ? a[arrKey].length - 1 : 0;
                    index2 = b[arrKey].length ? b[arrKey].length - 1 : 0;
                }
                str1 = str1 == null ? a[arrKey][index1][key] ? a[arrKey][index1][key].toLowerCase() : '' : str1;
                str2 = str2 == null ? b[arrKey][index2][key] ? b[arrKey][index2][key].toLowerCase() : '' : str2;

                if (str1 != str2) {
                    sorted = true;
                }

                if (str1 < str2) return 1;
                if (str1 > str2) return -1;
                return 0;
            });
            sorted ? $scope.tListsorted = true : $scope.tListsorted = false;
        }
    }

    $scope.setAndGetSortedArr = function (arr, key, isNumericVal) {
        if (key == $scope.talentSorted && $scope.tListsorted) {
            arr = arr.reverse();
        } else if (key == $scope.talentSorted && !$scope.tListsorted) {
            return;
        } else {
            $scope.talentSorted = key;
            if (isNumericVal) {
                $scope.sortNumericArr(arr, key);
            } else {
                $scope.sortArr(arr, key);
            }
        }
    }

    $scope.sortNumericArr = function (arr, key) {
        var sorted = false;
        arr.sort(function (a, b) {
            var result = parseFloat(a[key]) - parseFloat(b[key]);
            if (result != 0) {
                sorted = true;
            }
            return result;
        });
        sorted ? $scope.tListsorted = true : $scope.tListsorted = false;
    }

    $scope.sortArr = function (arr, key) {
        var sorted = false;
        arr.sort(function (a, b) {
            if (a[key].toLowerCase() != b[key].toLowerCase()) {
                sorted = true;
            }
            if (a[key].toLowerCase() < b[key].toLowerCase()) return 1;
            if (a[key].toLowerCase() > b[key].toLowerCase()) return -1;
            return 0;
        });
        sorted ? $scope.tListsorted = true : $scope.tListsorted = false;
    }

    $scope.reverse = false;
    $scope.sortBy = function (propertyName) { // filed sorting functionality in all project view
        $scope.reverse = ($scope.propertyName === propertyName) ? !$scope.reverse : false;
        $scope.propertyName = propertyName;
        if ($scope.reverse == false) {
            if ($("#headRow").find(".sorting_asc").length > 0) {
                $("#headRow").find(".sorting_asc").removeClass("sorting_asc");
            }
            $('#' + propertyName).addClass('sorting_asc');
        } else if ($scope.reverse == true) {
            if ($("#headRow").find(".sorting_desc").length > 0) {
                $("#headRow").find(".sorting_desc").removeClass("sorting_desc");
            }
            $('#' + propertyName).addClass('sorting_desc');
        }
    }

    $scope.allConcepts = function (talentConcepts) {
        if (talentConcepts.length > 6) {
            $scope.talentData = talentConcepts;
            $('#all-concept').modal('show');
        }
    }

    $scope.allMetrics = function (talentCareer) {
        if (talentCareer.length > 3) {
            $scope.talentCareer = talentCareer;
            $('#all-metrics').modal('show');
        }
    }

    $scope.openContactInfo = function () {
        /*$scope.candidateEmail = '';
        $scope.candidateEmailAdd = '';
        $scope.candidateContact = '';
        $scope.candidateContactAdd = '';*/

        // form valid true
        if ($scope.add_email) {
            $scope.add_email.talentAddEmail.blur = false;
        }
        // form valid end
        $scope.isEmailEditable = false;
        $scope.isEmailAdd = false;
        $scope.isContactEditable = false;
        $scope.isContactAdd = false;
        $scope.isEmail = false;
        $scope.isContact = false;
        $('#update_email').removeClass('disabled');
        $('#add_email').removeClass('disabled');
        $('#update_contact').removeClass('disabled');
        $('#add_contact').removeClass('disabled');
        $('#update_contact').css('pointer-events', '');
        $('#update_email').css('pointer-events', '');
        $('#add_contact').css('pointer-events', '');
        $('#add_email').css('pointer-events', '');

        $('#contact-info').modal('show');

    }

    $scope.closeCandidateInfo = function () {
        $scope.candidateInfo = {};
        $scope.isEmailEditable = false;
        $scope.isEmailAdd = false;
        $scope.isContactEditable = false;
        $scope.isContactAdd = false;
        $scope.isEmail = false;
        $scope.isContact = false;
        $('#update_email').removeClass('disabled');
        $('#add_email').removeClass('disabled');
        $('#update_contact').removeClass('disabled');
        $('#add_contact').removeClass('disabled');
        $('#update_contact').css('pointer-events', '');
        $('#update_email').css('pointer-events', '');
        $('#add_contact').css('pointer-events', '');
        $('#add_email').css('pointer-events', '');
        $('#contact-info').modal('hide');
    }

    $scope.cancelPopup = function () {
        $scope.isEmailEditable = false;
        $scope.isEmailAdd = false;
        $scope.isContactEditable = false;
        $scope.isContactAdd = false;
        $scope.isEmail = false;
        $scope.isContact = false;
    }


    $scope.updateTalentEmail = function (id, oldEmail, candidateEmail) {
        // console.log(candidateEmail);
        if (candidateEmail) {
            $('#update_email').addClass('disabled');
            $('#update_email').css('pointer-events', 'none');
            var formData = new FormData();
            formData.append('token', $rootScope.globals.currentUser.token);
            formData.append('recruiter', $rootScope.globals.currentUser.user_email);
            formData.append('talent_id', id);
            formData.append('email', oldEmail);
            formData.append('updated_email', candidateEmail);
            talentApis.addEmail(formData, requestCallback);

            function requestCallback(response) {
                response = JSON.parse(response);
                if (response.message == "success") {
                    //console.log(response);

                    $scope.closeCandidateInfo();
                    //candidateEmail ='';
                    $rootScope.talentDetails.talent_email[0].email = candidateEmail;
                    sessionStorage.talentDetails = JSON.stringify($rootScope.talentDetails);
                    //                    $('#emailUpdated').css('display', 'block');
                    //                    setTimeout(function () {
                    //                        $('#emailUpdated').css('display', 'none');
                    //                    }, 3000);
                    $scope.showNotification(true, "Talent email is updated.");
                } else if (response.success == false) {
                    $scope.candidateEmail = '';
                    $scope.closeCandidateInfo();
                    $scope.showNotification(false, response.errorstring);
                    $scope.$apply();
                }
            }
        } else {
            $scope.isEmail = true;
        }
    }

    $scope.addEmail = function (id, oldEmail, candidateEmailAdd) {
        if (candidateEmailAdd) {
            $('#add_email').addClass('disabled');
            $('#add_email').css('pointer-events', 'none');
            var formData = new FormData();
            formData.append('token', $rootScope.globals.currentUser.token);
            formData.append('recruiter', $rootScope.globals.currentUser.user_email);
            formData.append('talent_id', id);
            formData.append('email', candidateEmailAdd);
            talentApis.addEmail(formData, requestCallback);

            function requestCallback(response) {
                response = JSON.parse(response);
                if (response.message == "success") {
                    if (!$rootScope.talentDetails.talent_email || !$rootScope.talentDetails.talent_email.length) {
                        $rootScope.talentDetails.talent_email = [{}];
                    }
                    $rootScope.talentDetails.talent_email[0].email = candidateEmailAdd;
                    sessionStorage.talentDetails = JSON.stringify($rootScope.talentDetails);
                    // console.log(response);
                    $scope.candidateEmailAdd = '';
                    $scope.closeCandidateInfo();
                    //candidateEmailAdd ='';

                    //                    $('#emailSuccess').css('display', 'block');
                    //                    setTimeout(function () {
                    //                        $('#emailSuccess').css('display', 'none');
                    //                    }, 3000);

                    $scope.showNotification(true, 'Email has been added.');
                } else if (response.success == false) {
                    $scope.candidateEmailAdd = '';
                    $scope.closeCandidateInfo();
                    //                    $('#emailError').css('display', 'block');
                    //                    setTimeout(function () {
                    //                        $('#emailError').css('display', 'none');
                    //                    }, 2000);
                    $scope.showNotification(false, response.errorstring);
                }
            }
        } else {
            $scope.isEmail = true;
        }
    }

    $scope.addContact = function (id, oldContact, candidateContactAdd) {
        //console.log(candidateContactAdd);
        if (candidateContactAdd) {
            $('#add_contact').addClass('disabled');
            $('#add_contact').css('pointer-events', 'none');
            var formData = new FormData();
            formData.append('token', $rootScope.globals.currentUser.token);
            formData.append('recruiter', $rootScope.globals.currentUser.user_email);
            formData.append('talent_id', id);
            formData.append('contact', candidateContactAdd);
            //            $rootScope.showLoader(true);
            talentApis.talentContact(formData, requestCallback);

            function requestCallback(response) {
                response = JSON.parse(response);

                if (!$rootScope.talentDetails.talent_contact || !$rootScope.talentDetails.talent_contact.length) {
                    $rootScope.talentDetails.talent_contact = [{}];
                }
                $rootScope.talentDetails.talent_contact[0].contact = candidateContactAdd;
                sessionStorage.talentDetails = JSON.stringify($rootScope.talentDetails);
                //console.log(response);
                $scope.closeCandidateInfo();
                // candidateContact ='';
                //                $('#contactSuccess').css('display', 'block');
                //                setTimeout(function () {
                //                    $('#contactSuccess').css('display', 'none');
                //                }, 2000);
                $rootScope.showLoader(false);

                if (response.success) {
                    $scope.showNotification(true, "Talent contact has been added.");
                } else {
                    $scope.showNotification(false, response.errorstring);
                }
            }
        } else {
            $scope.isContact = true;
        }
    }

    $scope.updateContact = function (id, oldContact, candidateContactAdd) {
        //console.log(candidateContactAdd);
        if (candidateContactAdd) {
            $('#update_contact').addClass('disabled');
            $('#update_contact').css('pointer-events', 'none');
            var formData = new FormData();
            formData.append('token', $rootScope.globals.currentUser.token);
            formData.append('recruiter', $rootScope.globals.currentUser.user_email);
            formData.append('talent_id', id);
            formData.append('contact', oldContact);
            formData.append('updated_contact', candidateContactAdd);
            talentApis.talentContact(formData, requestCallback);

            function requestCallback(response) {
                response = JSON.parse(response);
                // console.log(response);

                $scope.closeCandidateInfo();
                $rootScope.talentDetails.talent_contact[0].contact = candidateContactAdd;
                sessionStorage.talentDetails = JSON.stringify($rootScope.talentDetails);
                if (response.success) {
                    $scope.showNotification(true, "Talent contact has been updated successfully.");
                    //                    $('#contactUpdated').css('display', 'block');
                    //                    setTimeout(function () {
                    //                        $('#contactUpdated').css('display', 'none');
                    //                    }, 2000);

                } else {
                    $scope.showNotification(false, response.errorstring);
                    //                    $('#contactError').css('display', 'block');
                    //                    setTimeout(function () {
                    //                        $('#contactError').css('display', 'none');
                    //                    }, 2000);             
                }
            }
        } else {
            $scope.isContact = true;
        }
    }

    $scope.resetModal = function () {
        var doneButton = document.getElementById('done');
        doneButton.classList.add('disabled');
        doneButton.classList.add('talent-modal-done');
        doneButton.classList.remove('talent-modal-add');
        doneButton.style['pointer-events'] = 'none';
        document.getElementById('backgroundImg').style.display = '';
        //$('#add-talent').modal('show');
    }

    $scope.activePageNumber;
    $scope.initPagination = function () {
        var pageItem = $(".pagination li").not(".prev,.next");
        var prev = $(".pagination li.prev");
        var next = $(".pagination li.next");

        pageItem.click(function () {
            //console.log(this.id);
            pageItem.removeClass("active");
            $(this).not(".prev,.next").addClass("active");
            $scope.activePageNumber = $('.pagination li.active').attr('id');
        });

        next.click(function () {
            //console.log($('li.active').removeClass('active').next().);
            $('li.active').removeClass('active').next().addClass('active');
            $scope.activePageNumber = $('.pagination li.active').attr('id');
        });

        prev.click(function () {
            //console.log($('li.active').removeClass('active').prev());
            $('li.active').removeClass('active').prev().addClass('active');
            $scope.activePageNumber = $('.pagination li.active').attr('id');
        });
        //console.log($scope.activePageNumber)
    }

    function initDatePicker(id) {
        $("#" + id).datepicker({
            dateFormat: 'M d, yy',
            changeYear: true,
            yearRange: '1900:' + new Date().getFullYear(),
            yearRange: '1900:' + new Date().getFullYear(),
            maxDate: new Date()
        });
    }

    $scope.openAddStagePopup = function (id) {
        $('#addStageDate').val('')
        $scope.stage = {
            stage: '',
            project: '',
            date: '',
            detail: '',
            notes: '',
            isStage: false,
            stagesCard: $rootScope.talentAllStages ? $rootScope.talentAllStages : stagesTemp
        };
        $('.select-date').val('');
        $('#add-stage-date').val('');
        //$('#datepicker').datepicker({});
        $scope.isStage = false;
        $scope.isProject = false;
        $scope.isDate = false;
        $scope.isDetail = false;
        $scope.isNotes = false;

        $('#projectListD2').change(function () {
            $scope.hideValidation();
            var sbId = $('#projectListD2').attr('sb');
            var selectedValue = $('#sbSelector_' + sbId).text();
            if (selectedValue != 'Select Project')
                $scope.stage.project = selectedValue;
            // console.log($scope.stage.project);
        });
        $('#stageSelect').change(function () {
            $scope.hideValidation();
            var sbId = $('#stageSelect').attr('sb');
            var selectedValue = $('#sbSelector_' + sbId).text();
            if (selectedValue != 'Select Stage')
                $scope.stage.stage = selectedValue;
            // console.log($scope.stage.stage);
        });
        initDatePicker('addStageDate');
        $('#add-stage').modal('show');
    }
    //$scope.stage.stagesArray = [];
    function convertDate(inputFormat) {
        function pad(s) {
            return (s < 10) ? '0' + s : s;
        }
        var d = new Date(inputFormat);
        return [pad(d.getDate()), pad(d.getMonth() + 1), d.getFullYear()].join('/');
    }

    function checkReqValidationForStage(form) {
        /*Show error on blank field when user submit*/
        for (var key in $scope.stage) {
            if ($scope.stage[key] == '') {
                if (key == 'stage')
                    $scope.isStage = true;
                if (key == 'project')
                    $scope.isProject = true;
                if (key == 'date')
                    $scope.isDate = true;
                if (key == 'detail')
                    $scope.isDetail = true;
                if (key == 'notes')
                    $scope.isNotes = true;
            } else if ($scope.stage[key] != '') {
                if (key == 'stage')
                    $scope.isStage = false;
                if (key == 'project')
                    $scope.isProject = false;
                if (key == 'date')
                    $scope.isDate = false;
                if (key == 'detail')
                    $scope.isDetail = false;
                if (key == 'notes')
                    $scope.isNotes = false;
            }
        }
    }

    $scope.hideValidation = function ($event) {
        var max = 50;
        if ($event) {
            if (($event.target.value.length > max) && ($event.target.name == "details"))
                $scope.detailMax = true;
            else if (($event.target.value.length < max) && ($event.target.name == "details"))
                $scope.detailMax = false;
            if (($event.target.value.length > max) && ($event.target.name == "notes"))
                $scope.noteMax = true;
            else if (($event.target.value.length < max) && ($event.target.name == "notes"))
                $scope.noteMax = false;

            $scope.isStage = false;
            $scope.isProject = false;
            $scope.isDate = false;
            $scope.isDetail = false;
            $scope.isNotes = false;

        } else {
            $scope.isStage = false;
            $scope.isProject = false;
            $scope.isDate = false;
            $scope.isDetail = false;
            $scope.isNotes = false;
            $scope.$apply();
        }
    }

    $scope.closeStageModal = function () {
        var sbId = $('#stageSelect').attr('sb');
        var selectedValue = $('#sbSelector_' + sbId).text('Select Stage');
        $scope.stage.stage = selectedValue;
        var sbId = $('#projectListD2').attr('sb');
        var selectedValue = $('#sbSelector_' + sbId).text('Select Project');
        $scope.stage.project = selectedValue;
        $('.select-date').datepicker({
            dateFormat: "dd/mm/yyyy",
            changeMonth: true,
            changeYear: true
        }).val('');
        $('#add-stage').modal('hide');
        //$.datepicker._clearDate(this);
    }

    $rootScope.formatDate = function (date) {
        if (!date) {
            return date;
        }
        var d = new Date(date);
        if (d == 'Invalid Date') return date;
        var month = '' + (d.getMonth() + 1),
            day = '' + d.getDate(),
            year = d.getFullYear();

        if (month.length < 2) month = '0' + month;
        if (day.length < 2) day = '0' + day;

        return [day, month, year].join('/');
    }

    $scope.setDateValidation = function () {
        var date = $('#add-stage-date').val();
        $scope.isDate = date ? false : true;
    }
    $scope.addProjectCheckValidation = function (stage, removeValidation) {
        stage.date = stage.date ? stage.date : $('#addStageDate').val();
        if (removeValidation) {
            $scope.isStage = false;
            $scope.isProject = false;
            $scope.isDate = false;
            $scope.isDetail = false;
            $scope.isNotes = false;
        } else {
            $scope.isStage = stage.stage ? false : true;
            $scope.isProject = stage.project ? false : true;
            $scope.isDate = stage.date ? false : true;
            $scope.isDetail = $scope.stage.detail ? false : true;
            $scope.isNotes = stage.notes ? false : true;
        }
    }
    /* $scope.notification = {
          show:false,
          message:''
     };*/

    $scope.addProjectStage = function (stage) {
        stage.date = stage.date ? stage.date : $('#addStageDate').val();
        var selectedProjectId;
        console.log($scope.stage);
        if (typeof ($scope.stage.project) == 'object' || $scope.stage.project == 'Select Project') {
            $scope.stage.project = '';
        }

        if (typeof ($scope.stage.stage) == 'object' || $scope.stage.stage == 'Select Stage') {
            $scope.stage.stage = '';
        }
        //        var date = $('#add-stage-date').val();
        //
        //        if (date)
        $scope.stage.date = $rootScope.formatDate($scope.stage.date);

        //        $scope.addProjectCheckValidation($scope.stage);
        checkReqValidationForStage();
        if (!$scope.isStage && !$scope.isProject && !$scope.isDate && !$scope.isDetail && !$scope.isNotes) {

            for (var i = 0; i < $rootScope.allProjectList.length; i++) {
                if ($rootScope.allProjectList[i].project_name == $scope.stage.project.split('#')[1]) {
                    selectedProjectId = $rootScope.allProjectList[i].id;
                    break;
                }
            }
            if (selectedProjectId) {

                var formData = new FormData();
                formData.append('project_id', selectedProjectId);
                formData.append('talent_id', $rootScope.talentDetails.id);
                formData.append('stage', $scope.stage.stage);
                formData.append('details', $scope.stage.detail);
                formData.append('date', $scope.stage.date);
                formData.append('notes', $scope.stage.notes);
                talentApis.addTalentStages(formData, requestCallback);

                function requestCallback(response) {
                    response = JSON.parse(response);
                    if (response.message == "success") {
                        $('#add-stage').modal('hide');
                        $scope.showNotification(true, 'Stage has been added Successfully.');
                        $scope.stage.stage = '';

                        $scope.stage.project = '';
                        $scope.stage.detail = '';
                        $scope.stage.notes = '';
                        $scope.stage.date = '';
                        $scope.stage.isStage = false;

                        //                            $scope.stage.stagesCard.push(response);
                        $scope.talentDetails = response.result;
                        //                       $rootScope.talentDetails = response.result;
                        sessionStorage.talentDetails = JSON.stringify($rootScope.talentDetails);
                        //                        $scope.stage.stagesCard.unshift(response);

                        $rootScope.talentAllStages = response.result.talent_stages;
                        $scope.stage.stagesCard = response.result.talent_stages;
                        sessionStorage.removeItem('talentAllStages');
                        sessionStorage.talentAllStages = JSON.stringify($scope.stage.stagesCard);


                        $scope.stage.stagesCard = response.result.talent_stages;
                        $scope.$apply();
                        var sbId = $('#stageSelect').attr('sb');
                        var selectedValue = $('#sbSelector_' + sbId).text('Select Stage');
                        $scope.stage.stage = selectedValue;
                        var sbId = $('#projectListD2').attr('sb');
                        var selectedValue = $('#sbSelector_' + sbId).text('Select Project');
                        $scope.stage.project = selectedValue;

                        $('.select-date').datepicker({
                            dateFormat: "dd/mm/yyyy",
                            changeMonth: true,
                            changeYear: true
                        }).val('');
                        //                        sessionStorage.talentAllStages = JSON.stringify($scope.stage.stagesCard);
                    }
                    $window.scrollTo(0, 0);
                }
            }
        }
    }

    function openDatePicker($event) {
        //        var element = $event.target;
        //        $(element).datepicker({
        //            format: "dd/mm/yyyy"
        //        , }).on('change', function () {
        //            $('.datepicker').hide();
        //        });
        //        $(element).mousedown(function () {
        //            $('.datepicker').toggle();
        //        });
    }

    function initDatepicker(id) {
        $("#" + id).datepicker({
            dateFormat: 'M d, yy',
            changeYear: true,
            yearRange: '1900:' + new Date().getFullYear(),
            yearRange: '1900:' + new Date().getFullYear(),
            maxDate: new Date()
        });
    }

    $scope.initDatePickers = function () {
        initDatepicker('filter-from');
        initDatepicker('filter-to');
    }

    $scope.filterOpen = function () {
        if (!$rootScope.isFilterChecked) {
            $rootScope.isFilterChecked = true;
            $('.talent-search-icon').addClass('active');
            $('.selectpicker').selectpicker();
            /*$('#projectSelect').multiselect({
                 includeSelectAllOption: true,
                 enableFiltering:true
            });*/
            $("#rate_filter li.filled").removeClass('filled');
            //            $('#filterStage').change(function () {
            //                var selectedValue = $('#filterStage :selected').text();
            //                if (selectedValue != 'Select Stage')
            //                    $scope.filterValue.stage = selectedValue;
            //                // console.log($scope.filterValue.stage);
            //            });
        } else if ($rootScope.isFilterChecked) {
            $rootScope.isFilterChecked = false;
            $('.talent-search-icon').removeClass('active');
        }
    }

    $scope.advanceSearchOpen = function () {
        if (!$scope.isAdvanceSearch) {
            $('.advance-search').addClass('active');
            $scope.isAdvanceSearch = true;
        } else if ($scope.isAdvanceSearch) {
            $('.advance-search').removeClass('active');
            $scope.isAdvanceSearch = false;
        }
    }

    $scope.getfilterRating = function (rating) {
        $scope.filterValue.rating = rating;
        //console.log($scope.filterValue);
    }

    $scope.getFilterData = function () {
        $rootScope.globalSearch = false;
        if ($rootScope.candidatePagination.page == 1) {
            $scope.filterData();
        } else {
            $rootScope.candidatePagination.page = 1;
        }
    }

    $scope.filterData = function () {

        //        $rootScope.candidatePagination.page = 1;


        //        var analysedDate = $('#analysed').val();
        //        var lastContacted = $('#lastContacted').val();


        var selectedProjectId = '';

        //            $scope.filterValue.analysed = analysedDate;
        //        $scope.filterValue.analysed = $scope.filterValue.analysed ? $rootScope.formatDate($scope.filterValue.analysed) : '';
        $scope.filterValue.analysed = $('#filter-from').val() ? $rootScope.formatDate($('#filter-from').val()) : '';


        //            $scope.filterValue.lastContacted = lastContacted;
        //        $scope.filterValue.lastContacted = $scope.filterValue.lastContacted ? $rootScope.formatDate($scope.filterValue.lastContacted) : '';
        $scope.filterValue.lastContacted = $('#filter-to').val() ? $rootScope.formatDate($('#filter-to').val()) : '';

        $scope.filterValue.stage = $scope.tFilter.stage;
        if ($scope.filterValue.stage == 'Select Stage' || $scope.filterValue.stage == undefined || $scope.filterValue.stage == "0")
            $scope.filterValue.stage = '';
        if ($scope.filterValue.match.split('%')[0] == '0')
            $scope.filterValue.match = $scope.priceSlider.value + '%';
        else {
            $scope.filterValue.match = $scope.filterValue.match.split('%')[0] || $scope.priceSlider.value + '%';
        }
        if ($scope.filterValue.project == 'Select Project' || $scope.filterValue.project == undefined)
            $scope.filterValue.project = '';

        //        if ($scope.filterValue.ordering == 'true') {
        //            $scope.filterValue.ordering = 'desc';
        //        } else if ($scope.filterValue.ordering == 'false') {
        //            $scope.filterValue.ordering = 'asc';
        //        } else {
        //            $scope.filterValue.ordering = '';
        //        }

        if (!$scope.filterValue.ordering) {
            $scope.filterValue.ordering = '';
        }

        if (!$scope.filterValue.active) {
            $scope.filterValue.active = '';
        }

        if (typeof ($scope.filterValue.project) != 'object')
            for (var i = 0; i < $rootScope.allProjectList.length; i++) {
                if ($rootScope.allProjectList[i].project_name == $scope.filterValue.project.split('#')[1]) {
                    selectedProjectId = $rootScope.allProjectList[i].project_name;
                    break;
                }
            }

        var requestObject = {
            'company': $scope.filterValue.company,
            'rating': $scope.filterValue.rating,
            'project_match': $scope.filterValue.match,
            'recruiter': $scope.filterValue.recruiter_name,
            'concepts': $scope.filterValue.concepts,
            'projects': selectedProjectId,
            'stages': $scope.filterValue.stage,
            'contacted': $scope.filterValue.lastContacted,
            'date': $scope.filterValue.analysed,
            'active': $scope.filterValue.active,
            'ordering': $scope.filterValue.ordering,
            'term': ($rootScope.search && $rootScope.search.searchKeywords) ? $rootScope.search.searchKeywords : ''
        };
        requestObject.active = requestObject.active ? (requestObject.active == 'active' ? true : false) : '';
        requestObject.project_match = parseInt(requestObject.project_match.split('%')[0]) || '';

        requestObject.page = $rootScope.candidatePagination.page;
        //        requestObject.page = 1;
        requestObject.count = $rootScope.candidatePagination.count;

        console.log(requestObject);
        talentApis.filterTalentData(requestObject).then(function (response) {
            $rootScope.candidatePages = [];
            if (response.results.length > 0) {
                $rootScope.Filter = false;
                console.log(response.results);
                $rootScope.talentList = [];
                for (var i = 0; i < response.results.length; i++) {
                    $rootScope.talentList.push(response.results[i]);
                }
                var count = response.count;
                $rootScope.totalTalentCount = count;
                $rootScope.talentCountEnd = count;

                for (var i = 0; i < Math.ceil($rootScope.totalTalentCount / $rootScope.candidatePagination.count); i++) {
                    $rootScope.candidatePages.push({
                        i: true
                    });
                }

            } else if (response.results.length == 0) {
                $rootScope.talentList = [];
                $rootScope.Filter = true;
                $rootScope.totalTalentCount = 0;
                $rootScope.talentCountEnd = 0;
            }
            $rootScope.createCareerHistoryData($rootScope.talentList);
        });
    }

    $scope.convertIntoInt = function (val) {
        return parseInt(val);
    }

    $rootScope.createCareerHistoryData = function (arr) {

        //        var totalExp = calcTotal(arr);
        arr.forEach(function (talent) {
            if (talent.talent_company.length) {
                var currentComp = [];
                var arr = talent.talent_company.filter(function (company) {
                    if (company.is_current) {
                        currentComp.push(company);
                    }
                    return !company.is_current;
                });
                talent.pastCompanyLength = arr.length;
                talent.currentCompanyLength = currentComp.length;
                talent.talent_company = arr;
                if (currentComp.length) {
                    talent.talent_company = currentComp.concat(talent.talent_company);
                }
            }
            talent.talent_concepts = talent.talent_concepts.sort(function (a, b) {
                return parseFloat(a.match) - parseFloat(b.match);
            });
            talent.talent_concepts = talent.talent_concepts.reverse();
            var isEmptyDate = false;
            talent.total_experience = $scope.calcTotal(talent.talent_company);
            for (var i = 0; i < talent.talent_company.length; i++) {
                var obj = talent.talent_company[i];
                obj.career_gap = parseFloat(obj.career_gap);
                obj.years_of_experience = parseFloat(obj.years_of_experience);
                for (j = 0; j < i; j++) {
                    if (!obj.blank_gap)
                        obj.blank_gap = 0;

                    obj.blank_gap += talent.talent_company[j].career_gap;
                    obj.blank_gap += talent.talent_company[j].years_of_experience;
                }
                //                obj.career_gap = obj.career_gap.toFixed(2);
                //                obj.years_of_experience = obj.years_of_experience.toFixed(2);
                if (obj.blank_gap) {
                    //                    obj.blank_gap = obj.blank_gap.toFixed(2);   
                } else {
                    obj.blank_gap = 0;
                }

                obj.career_gap = parseFloat(obj.career_gap);
                obj.years_of_experience = parseFloat(obj.years_of_experience);
                obj.blank_gap = parseFloat(obj.blank_gap);

                if ((i != 0) && !obj.end_date || !obj.start_date) {
                    isEmptyDate = true;
                }
                if (isEmptyDate) {
                    obj.career_gap = 0;
                    obj.years_of_experience = 0;
                    obj.blank_gap = 0;
                }
            }
        });
        //        return arr;
    }

    $scope.updateTalent = function (data) {

    }
    $scope.openEditProfileForm = function (data) {
        // $scope.talentEditableData = talent;

        $scope.search.searchKeywords = '';

        var talent = angular.copy(data);

        var talentName = talent.talent_name.split(' ');
        var location = talent.current_location.split(',');
        $scope.talentEditableData = {
            currentOrganization: [],
            pastOrganization: [],
            education: [],
            topConcepts: [],
            email: talent.talent_email.length ? talent.talent_email[0].email : '',
            phone: talent.talent_contact.length ? talent.talent_contact[0].contact : '',
            profile_image: talent.image,
            linkedinProfileUrl: talent.linkedin_url,
            city: location[0] ? location[0].trim() : "",
            country: location[2] ? location[2].trim() : "",
            state: location[1] ? location[1].trim() : "",
            designation: talent.designation ? talent.designation.trim() : '',
            industryFocus: {
                name: talent.industry_focus ? talent.industry_focus.trim() : '',
                percentage: talent.industry_focus_percentage ? talent.industry_focus_percentage : ''
            },
            firstName: talentName[0] ? talentName[0].trim() : '',
            lastName: talentName[1] ? talentName[1].trim() : '',
            id: talent.id
        };

        talent.talent_concepts.forEach(function (concept) {
            $scope.talentEditableData.topConcepts.push({
                name: concept.concept,
                id: concept.id, //                match: concept.match
            });
        });

        //        if (talent.talent_company.length && talent.talent_company[0].is_current) {
        //            var organisation = {
        //                JobTitle: ''
        //                , name: ''
        //                , from: ''
        //                , to: ''
        //            };
        //            organisation.name = talent.talent_company[0].company ? talent.talent_company[0].company.trim() : '';
        //            organisation.JobTitle = talent.talent_company[0].designation ? talent.talent_company[0].designation.trim() : '';
        //            if (talent.talent_company[0].start_date) {
        //                var date = new Date(talent.talent_company[0].start_date);
        //                organisation.from = date.getFullYear().toString();
        //            }
        //            if (talent.talent_company[0].end_date) {
        //                var date = new Date(talent.talent_company[0].end_date);
        //                organisation.to = date.getFullYear().toString();
        //            }
        //            organisation.id = talent.talent_company[0].id;
        //            $scope.talentEditableData.currentOrganization.push(organisation);
        //        } else {
        //            $scope.talentEditableData.currentOrganization.push({
        //                JobTitle: ''
        //                , name: ''
        //                , from: ''
        //                , to: ''
        //            });
        //        }

        //        if (talent.talent_company.length) {
        //
        //            var index = 0;
        //            talent.talent_company[0].is_current ? index = 1 : 0
        //
        //            for (var i = index; i < talent.talent_company.length; i++) {
        //                var organisation = {
        //                    JobTitle: ''
        //                    , name: ''
        //                    , from: ''
        //                    , to: ''
        //                };
        //                organisation.name = talent.talent_company[i].company ? talent.talent_company[i].company.trim() : '';
        //                organisation.JobTitle = talent.talent_company[i].designation ? talent.talent_company[i].designation.trim() : '';
        //                if (talent.talent_company[i].start_date) {
        //                    var date = new Date(talent.talent_company[i].start_date);
        //                    organisation.from = date.getFullYear().toString();
        //                }
        //                if (talent.talent_company[i].end_date) {
        //                    var date = new Date(talent.talent_company[i].end_date);
        //                    organisation.to = date.getFullYear().toString();
        //                }
        //                organisation.id = talent.talent_company[i].id;
        //                $scope.talentEditableData.pastOrganization.push(organisation);
        //            }
        //        } else {
        //            $scope.talentEditableData.pastOrganization.push({
        //                JobTitle: ''
        //                , name: ''
        //                , from: ''
        //                , to: ''
        //            });
        //        }
        var isCurrentCompany = false,
            isPastCompany = false;
        if (talent.talent_company.length) {

            var index = 0;

            for (var i = index; i < talent.talent_company.length; i++) {
                var organisation = {
                    JobTitle: '',
                    name: '',
                    from: '',
                    to: ''
                };
                organisation.name = talent.talent_company[i].company ? talent.talent_company[i].company.trim() : '';
                organisation.JobTitle = talent.talent_company[i].designation ? talent.talent_company[i].designation.trim() : '';
                if (talent.talent_company[i].start_date) {
                    var date = new Date(talent.talent_company[i].start_date);
                    organisation.from = date.getFullYear().toString();
                }
                if (talent.talent_company[i].end_date) {
                    var date = new Date(talent.talent_company[i].end_date);
                    organisation.to = date.getFullYear().toString();
                }
                organisation.id = talent.talent_company[i].id;

                if (talent.talent_company[i].is_current) {
                    $scope.talentEditableData.currentOrganization.push(organisation);
                    isCurrentCompany = true;
                } else {
                    $scope.talentEditableData.pastOrganization.push(organisation);
                    isPastCompany = true
                }
            }
        }

        if (!isCurrentCompany) {
            $scope.talentEditableData.currentOrganization.push({
                JobTitle: '',
                name: '',
                from: '',
                to: ''
            });
        }
        if (!isPastCompany) {
            $scope.talentEditableData.pastOrganization.push({
                JobTitle: '',
                name: '',
                from: '',
                to: ''
            });
        }

        if (talent.talent_education.length) {
            for (var i = 0; i < talent.talent_education.length; i++) {
                var organisation = {
                    name: '',
                    from: '',
                    to: ''
                };
                organisation.name = talent.talent_education[i].education ? talent.talent_education[i].education.trim() : '';
                if (talent.talent_education[i].start_date) {
                    var date = new Date(talent.talent_education[i].start_date);
                    organisation.from = date.getFullYear().toString();
                }
                if (talent.talent_education[i].end_date) {
                    var date = new Date(talent.talent_education[i].end_date);
                    organisation.to = date.getFullYear().toString();
                }
                organisation.id = talent.talent_education[i].id;
                $scope.talentEditableData.education.push(organisation);
            }
        } else {
            $scope.talentEditableData.education.push({
                name: '',
                from: '',
                to: ''
            });
        }

        $state.go('talent.create-profile');
        createTalentFormService.setTalentDetails(angular.copy($scope.talentEditableData));

        //        $rootScope.editTalentDetail($scope.talentEditableData);
        //$('#edit-profile').modal('show');
    }

    $rootScope.filterReset = function () {
        $('#filter-from').val('');
        $('#filter-to').val('');
        $scope.priceSlider.value = 0;
        $scope.filterValue = {
            stage: '',
            project: '',
            match: $scope.priceSlider.value + '%',
            rating: '',
            lastContacted: '',
            analysed: '',
            company: '',
            concepts: '',
            recruiter_name: '',
            ordering: '',
            active: ''
        };
        $('#filterStage').val('').prop('selectedIndex', 0);
        var selectedValue = $('#filterStage :selected').text(); 
        var selectorId = $("#filterStage").attr('sb');
        $('#sbSelector_' + selectorId).text(selectedValue);
        $("#projectSelect").val('').selectpicker('refresh');
        // $("#ex3").slider("value", $("#ex3").slider("option", "min") );
        //        $('.filter-input-date').datepicker({
        //            dateFormat: "dd/mm/yyyy"
        //            , changeMonth: true
        //            , changeYear: true
        //        }).val('');
        //$("#ex3").slider('values', 0, 100);

        $("#rate_filter li.filled").removeClass('filled');
        $('.radio-none').attr('checked', false);

    }


    $scope.init = function () {

        //        $("#proj-stage-date-text").datepicker({
        //            dateFormat: 'M d, yy'
        //            , changeYear: true
        //            , yearRange: '1900:' + new Date().getFullYear()
        //            , yearRange: '1900:' + new Date().getFullYear()
        //            , maxDate: new Date()
        //            , beforeShow: function () {
        //                $('.dob-box').append($('#ui-datepicker-div'));
        //            }
        //        });
    }

    $scope.init();

}

function createTalentFormCtrl($scope, createTalentFormService) {
    $scope.talentData = {
        currentOrganization: {},
        pastOrganization: [{}],
        education: [{}],
        topConcepts: [{}]
    };

    $scope.addPastOrganization = function () {
        $scope.talentData.pastOrganization.push({});
    }
    $scope.addSkill = function () {
        $scope.talentData.topConcepts.push({});
    }

    $scope.removeIndexFromArr = function (arr, index) {
        arr.splice(index, 1);
    }

    $scope.createTalent = function (data) {
        console.log(data)
        //        createTalentFormService.createTalent(data, function(response){
        //            console.log(response)
        //        });
    }
}


angular
    .module('brightStaffer')
    .controller('MainCtrl', MainCtrl)
    .controller('talentCtrl', talentCtrl)
    .controller('loginCtrl', loginCtrl)
    .controller('signupCtrl', signupCtrl)
    .controller('forgotCtrl', forgotCtrl)
    .controller('resetPwCtrl', resetPwCtrl)
    .controller('createProjectCtrl', createProjectCtrl)
    .controller('tableCtrl', tableCtrl)
    .controller('scoreCardCtrl', scoreCardCtrl)
    .controller('uploadFileCtrl', uploadFileCtrl)
    .controller('sideNavCtrl', sideNavCtrl)
    .controller('topnavCtrl', topnavCtrl)
    .controller('createTalentFormCtrl', createTalentFormCtrl);
