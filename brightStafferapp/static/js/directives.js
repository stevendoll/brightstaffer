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

function onFinishRender($timeout) {
    return {
        restrict: 'A',
        link: function (scope, element, attr) {
            if (scope.$last === true) {
                $timeout(function () {
                    scope.$emit(attr.onFinishRender);
                });
            }
        }
    }
}


/**
 * sideNavigation - Directive for run metsiMenu on sidebar navigation
 */
function sideNavigation($timeout) {
    return {
         restrict: 'A',
            link: function(scope, ele, atts) {
                setTimeout(function(){
                 $(ele).metisMenu();
              }, 1);
            }
    };
}

/**
 * minimalizaSidebar - Directive for minimalize sidebar
*/
function minimalizaSidebar($timeout,$state) {
    return {
        restrict: 'A',
        template: '<a class="navbar-minimalize minimalize-ui btn btn-default" href="" ng-click="minimalize()"><i class="icon icon-unread"></i></a>',
        controller: function ($scope, $element) {
            $scope.minimalize = function () {
                $("body").toggleClass("mini-navbar");
                if (!$('body').hasClass('mini-navbar') || $('body').hasClass('body-small')) {
                    // Hide menu in order to smoothly turn on when maximize menu
                    $('.nav-second-level').parent().removeClass('active');
                    $('.nav-second-level').removeClass('in');
                    $('.nav-second-level').css('height','0px');
                    $('#side-menu').hide();
                    // For smoothly turn on menu
                    setTimeout(
                        function () {
                           if($state.current.name == "dashboard"){
                             $('#dashboard').addClass('highlight');
                           }
                                 $('#side-menu').fadeIn(400);
                        }, 200);
                } else if ($('body').hasClass('fixed-sidebar')){

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
    };
}


function clickOutside($document, $state) {
        return {
           restrict: 'A',
           scope: {
               clickOutside: '&'
           },
           link: function (scope, el, attr) {

               $document.on('click', function (e) {
                   if (el !== e.target && !el[0].contains(e.target)) {
                        scope.$apply(function () {
                            if($state.current.name == 'dashboard'){
                                 $(".nav li.active").removeClass('active');
                                 $('#dashboard').addClass('active');
                            }
                            if($state.current.name == 'projects'){
                                 $(".nav li.active").removeClass('active');
                                 $('#project').addClass('active');
                                 $('#allProject').addClass('active');
                            }
                            if($state.current.name == 'create'){
                                 $(".nav li.active").removeClass('active');
                                 $('#project').addClass('active');
                                 $('#createProject').addClass('active');
                            }

                            scope.$eval(scope.clickOutside);
                        });
                    }
               });
           }
        };

}


function onTouch($parse, $rootScope) {
  return {
        restrict: 'A',
        link: function(scope, elm, attrs) {
            var ontouchFn = $parse(attrs.onTouch);
             if( navigator.userAgent.match(/Android/i)
                 || navigator.userAgent.match(/webOS/i)
                 || navigator.userAgent.match(/iPhone/i)
                 || navigator.userAgent.match(/iPod/i)
                 || navigator.userAgent.match(/BlackBerry/i)
                 || navigator.userAgent.match(/Windows Phone/i)
                     ){
                     $rootScope.isDevice = true;
                    elm.bind('touchstart', function(evt) {
                       evt.stopPropagation();
                    });
                        $rootScope.eventType = 'touchend';
                     }else{
                        $rootScope.eventType = 'click';
                     }

            elm.bind($rootScope.eventType, function(evt) {
                scope.$apply(function(){
                 ontouchFn.call(scope.setActive(evt), evt.which);
                });
            });
        }
    };
}


function myDirective($rootScope) {
    return {
        restrict: 'A',
        scope: true,
        link: function (scope, element, attr) {
            element.bind('change', function (e) {
                e.preventDefault();
                e.stopPropagation();
                scope.countError = false;
                $('.msgbox').addClass('ng-hide');
                scope.noFile = false;
                $('#noFileMsg').addClass('ng-hide');
                if (element[0].files){
                    if (element[0].files.length > 0) {
                      scope.uploadFiles(element[0].files);
                      $('#filesInput1').val('');
                      $('#filesInput2').val('');
                    }
                }
                return false;
            });
        }
    };
}


function fileDropzone($rootScope) {
  return {
    restrict: 'A',
    link: function(scope, element, attrs) {

        element.on('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
        });
        element.on('dragenter', function(e) {
            e.preventDefault();
            e.stopPropagation();
        });
        element.on('drop', function(event) {
            event.preventDefault();
            event.stopPropagation();
            if (event != null) {
                  event.preventDefault();
                }
            scope.countError = false;
            scope.noFile = false;
            $('.msgbox').addClass('ng-hide');
            scope.NoFileMsg ='';
            $('#noFileMsg').addClass('ng-hide');
            var file = event.dataTransfer.files[0];
             scope.checkFileValidation(file);
             $('#add-talent').modal('hide');
             $('#add-files').modal('show');
        });
    }
  };
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
    .directive('limitTo', limitTo)
    .directive('onFinishRender', onFinishRender)
    .directive('sideNavigation', sideNavigation)
    .directive('minimalizaSidebar', minimalizaSidebar)
    .directive('clickOutside', clickOutside)
    .directive('onTouch', onTouch)
    .directive('myDirective', myDirective)
    .directive('fileDropzone', fileDropzone);
