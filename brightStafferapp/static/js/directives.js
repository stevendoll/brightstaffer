/**
 * INSPINIA - Responsive Admin Theme
 *
 */


/**
 * pageTitle - Directive for set Page title - mata title
 */
function pageTitle($rootScope, $timeout) {
    return {
        link: function(scope, element) {
            var listener = function(event, toState, toParams, fromState, fromParams) {
                // Default title - load on Dashboard 1
                var title = 'BrightStaffer';
                // Create your own title pattern
                if (toState.data && toState.data.pageTitle) title = 'Sona . ' + toState.data.pageTitle;
                $timeout(function() {
                    element.text(title);
                });
            };
            $rootScope.$on('$stateChangeStart', listener);
        }
    }
}

function validPasswordC() {
    return {
        require: 'ngModel',
        scope: {
            reference: '=validPasswordC'

        },
        link: function(scope, elm, attrs, ctrl) {
            ctrl.$parsers.unshift(function(viewValue, $scope) {
                var noMatch = viewValue != scope.reference
                ctrl.$setValidity('noMatch', !noMatch);
                return (noMatch) ? noMatch : !noMatch;
            });

            scope.$watch("confirmPassword", function(value) {
                ctrl.$setValidity('noMatch', value === ctrl.$viewValue);
            });
        }
    }
}


function autoCapitaliseFirstLetter($timeout) {
  return {
    require: 'ngModel',
    link: function (scope, element, attrs, modelCtrl) {

        modelCtrl.$parsers.push(function (inputValue) {

            var transformedInput = (!!inputValue) ? inputValue.charAt(0).toUpperCase() + inputValue.substr(1).toLowerCase() : '';

            if (transformedInput != inputValue) {
                modelCtrl.$setViewValue(transformedInput);
                modelCtrl.$render();
            }

            return transformedInput;
        });
      }
    }
}

function removeMe($rootScope) {
      return {
            link:function(scope,element,attrs)
            {
                element.bind("click",function() {
                console.log(element[0]);
                var skillName = element[0].id.split('_')[1];
                console.log(skillName);
                console.log(element.parent())
                    element.parent().remove();
                    element.remove();
                    var index = $rootScope.jobDescriptionResult.concept.indexOf(skillName);
                    console.log(index);
                    if(index > -1){
                       $rootScope.jobDescriptionResult.concept.splice(index,1);
                       scope.updateSkillSet();
                    }
                });
            }
      }

}


function limitTo(){
    return {
        restrict: "A",
        link: function(scope, elem, attrs) {
            var limit = parseInt(attrs.limitTo);
            angular.element(elem).on("keypress", function(e) {

                if (this.value.length == limit){
                    e.preventDefault();
                        if(this.name == 'project_name')
                           scope.isProjMaxlength = true;
                        if(this.name == 'company_name')
                           scope.isComMaxlength = true;
                        if(this.name == 'location')
                            scope.isLocationMaxlength = true;
                }
            });
        }
    }
}


/**
 *
 * Pass all functions into module
 */
angular
    .module('brightStaffer')
    .directive('pageTitle', pageTitle)
    .directive('validPasswordC', validPasswordC)
    .directive('removeMe', removeMe)
    .directive('autoCapitaliseFirstLetter', autoCapitaliseFirstLetter)
    .directive('limitTo', limitTo);
