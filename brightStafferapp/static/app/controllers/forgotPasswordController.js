'use strict';

mainApp.config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('[[').endSymbol(']]');
})

mainApp.controller('forgotPasswordController',
	[
		'$scope',
		function($scope, $filter, $location, $rootScope, appService) {

		}
	]);