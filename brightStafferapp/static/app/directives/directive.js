mainApp.directive('validPasswordC', function() {
    return {
        require: 'ngModel',
        scope: {
            reference: '=validPasswordC'

        },
        link: function(scope, elm, attrs, ctrl) {
            ctrl.$parsers.unshift(function(viewValue, $scope) {
                console.log(viewValue)
                console.log(scope.reference)
                var noMatch = viewValue != scope.reference
                ctrl.$setValidity('noMatch', !noMatch);
                return (noMatch) ? noMatch : !noMatch;
            });

            scope.$watch("data.confirmPassword", function(value) {
                ctrl.$setValidity('noMatch', value === ctrl.$viewValue);
            });
        }
    }
});
