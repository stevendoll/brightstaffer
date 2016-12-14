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
            data: { pageTitle: 'Login.', specialClass: 'gray-bg', requireAuthentication: false }
        })
        .state('forgot', {
            url: "/forgot",
            templateUrl:  static_url + "views/forgot.html",
            data: { pageTitle: 'Forgot Password.', specialClass: 'gray-bg', requireAuthentication: false }
        })
        .state('register', {
            url: "/register",
            templateUrl:  static_url + "views/register.html",
            data: { pageTitle: 'Register.', specialClass: 'gray-bg' , requireAuthentication: false}
        })
}

angular
    .module('brightStaffer')
    .config(config)
    .run(function($rootScope, $state, $location, $timeout) {
    $rootScope.globals = {};
    $rootScope.$state = $state;
    $rootScope.$on('$stateChangeSuccess', function (event, toState, toParams, fromState, fromParams) {
		$rootScope.title = toState.data.pageTitle;
	});
    $rootScope.$on('$stateChangeStart', function (event, toState, toParams, fromState, fromParams) {
        var shouldLogin = toState.data.requireAuthentication !== undefined
            && toState.data.requireAuthentication;

        // NOT authenticated - wants any private stuff
        if(shouldLogin || fromState.name === "") {
            var token = $rootScope.globals.currentUser == null ? null : $rootScope.globals.currentUser;
            if (token == null) {
                if(toState.name === 'login')
                    return;
                $state.go('login');
                event.preventDefault();
            } else {
                if(toState.name === toState.name)
                    return;
                $state.go(toState.name);
                event.preventDefault();
            }
          }
        });
    });
