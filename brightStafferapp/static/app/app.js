// constant api url
mainApp.constant('REQUEST_URL', 'http://127.0.0.1:8080/');
mainApp.config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('[[').endSymbol(']]');
})
mainApp.config(['$routeProvider',
    function($routeProvider) {
        $routeProvider.
            when('/login', {
                title:'Login.',
                templateUrl: static_url + 'app/html/login.html',
                controller: 'loginController',
                page:'login'
            }).
            when('/forgot', {
                title:'Forgot Password.',
                templateUrl: static_url + 'app/html/forgot_Password.html',
                controller: 'forgotPasswordController',
                page:'forgot'
            }).
            when('/account', {
                title:'Create an Account.',
                templateUrl: static_url + 'app/html/register.html',
                controller: 'signupController',
                page:'signup'
            }).
            when('/resetPassword', {
                title:'Reset Password.',
                templateUrl: static_url + 'app/html/resetPassword.html',
                controller: '',
                page:'resetPassword'
            }).
            otherwise({
                redirectTo: '/login'
            });
    }]);

mainApp.run(['$rootScope', '$location', '$http', '$window','$resource','REQUEST_URL', function ($rootScope, $location, $http, $window,$resource,REQUEST_URL) {
	$rootScope.location = $location;
	$rootScope.Utils = {
		keys : Object.keys
	}
	$rootScope.$on('$routeChangeSuccess', function (event, current, previous) {
		$rootScope.title = current.$$route.title;
		document.title = current.$$route.title;

	});
}]);