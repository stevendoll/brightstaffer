//$cookies.get('JWT') == null ? null : $cookies.get('JWT');

function config($stateProvider, $urlRouterProvider, $ocLazyLoadProvider, $interpolateProvider) {
    $interpolateProvider.startSymbol('[[').endSymbol(']]');

    $urlRouterProvider.otherwise("/login");
    $ocLazyLoadProvider.config({
        // Set to true if you want to see what and when is dynamically loaded
        debug: true
    });

    $stateProvider
        .state('dashboard', {
            url: "/dashboard",
            templateUrl: static_url +'views/common/content.html',
            data: { pageTitle: 'Dashboard' , specialClass: 'no-skin-config',requireAuthentication: true}
        })
        .state('login', {
            url: "/login",
            templateUrl:  static_url + "views/login.html",
            data: { pageTitle: 'Login.', specialClass: 'logn-bg-color', requireAuthentication: false }
        })
        .state('forgot', {
            url: "/forgot",
            templateUrl:  static_url + "views/forgot.html",
            data: { pageTitle: 'Forgot Password.', specialClass: 'logn-bg-color', requireAuthentication: false }

        })
        .state('register', {
            url: "/register",
            templateUrl:  static_url + "views/register.html",
            data: { pageTitle: 'Register.', specialClass: 'logn-bg-color' , requireAuthentication: false}
        })
        .state('create', {
            abstract: true,
            templateUrl: static_url +'views/create.html',
            data: { pageTitle: 'Create Project' , requireAuthentication: true}
        })
        .state('create.step1', {
            url: "/create",
            templateUrl: static_url +'views/common/create-step1.html',
            data: { pageTitle: 'Create Project' , requireAuthentication: true}
        })
        .state('create.step2', {
            url: "/create",
            templateUrl: static_url +'views/common/create-step2.html',
            data: { pageTitle: 'Create Project' , requireAuthentication: true}
        })
        .state('create.step3', {
            url: "/create",
            templateUrl: static_url +'views/common/create-step3.html',
            data: { pageTitle: 'Create Project' , requireAuthentication: true}
        })
        .state('create.step4', {
            url: "/create",
            templateUrl: static_url +'views/common/create-step4.html',
            data: { pageTitle: 'Create Project' , requireAuthentication: true}
        })
        .state('projects', {
            url: "/projects",
            templateUrl: static_url +'views/common/project-list.html',
            data: { pageTitle: 'All Projects' , requireAuthentication: true},
            resolve: {
                loadPlugin: function ($ocLazyLoad) {
                    return $ocLazyLoad.load([
                        {
                            files: [static_url +'css/plugins/dataTables/datatables.min.css',static_url +'css/animate.css',static_url +'css/style.css',static_url +'css/sona.css']
                        }
                    ]);
                }
            }
        })
        .state('development', {
            url: "/development",
            templateUrl: static_url +'views/common/development.html',
            data: { pageTitle: 'Under Dev' ,specialClass: 'development-bg', requireAuthentication: true}
        })

}

angular
    .module('brightStaffer')
    .config(config)
    .run(function($rootScope, $state, $location, $timeout, $cookies, $cookieStore) {
    $rootScope.isDevice = false;
    $rootScope.$state = $state;
    $rootScope.globals ={};
   // console.log('load');
    $rootScope.checkReqValidation = function(formName){
      $('#'+formName+ ' input').each(function(){ /*Show error on blank field when user submit*/
                    var spanClass = $(this).next('span').attr('class');
                    if($(this).val().length <= 0){
                        $(this).next('span').css('display','block');
                        $(this).next('span').addClass('error').text("Required.");
                    }else if($(this).val().length > 0 && ($(this).next('span').hasClass('error'))){
                        $(this).next('span').removeClass('error').text("");
                    }
            });

    }


    $rootScope.$on('$stateChangeSuccess', function (event, toState, toParams, fromState, fromParams) {
      if(fromState.name == 'create.step4' && toState.name == 'dashboard'){
              $('#publishBox').css('display','block');
            $timeout( function(){
                $('#publishBox').css('display','none');
                    } , 3000);
        }
		$rootScope.title = toState.data.pageTitle;

	});
    $rootScope.$on('$stateChangeStart', function (event, toState, toParams, fromState, fromParams) {
        var shouldLogin = toState.data.requireAuthentication !== undefined
            && toState.data.requireAuthentication;
         if($cookieStore.get('userData'))
            {
             $rootScope.globals.currentUser = $cookieStore.get('userData');
            }else if($rootScope.globals.currentUser){
              $cookieStore.put('userData', $rootScope.globals.currentUser)
            }
        // NOT authenticated - wants any private stuff
        if(shouldLogin || fromState.name === "") {
            var token =  $rootScope.globals.currentUser == null ? null : $rootScope.globals.currentUser;
            if (token == null) {
                if(toState.name === 'login')
                    return;
                $state.go('login');
                event.preventDefault();
            } else {
                $('.nav-second-level').parent().removeClass('active');
                 $('.nav-second-level').removeClass('in');
                 $('.nav-second-level').css('height','0px');
                if(toState.name === toState.name)
                    return;
                $state.go(toState.name);
                event.preventDefault();
            }
          }
        });
    });
