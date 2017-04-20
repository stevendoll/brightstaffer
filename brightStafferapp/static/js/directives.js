/**
 * INSPINIA - Responsive Admin Theme
 *
 */


/**
 * pageTitle - Directive for set Page title - mata title
 */
function pageTitle($rootScope, $timeout) {
    return {
        link: function (scope, element) {
            var listener = function (event, toState, toParams, fromState, fromParams) {
                // Default title - load on Dashboard 1
                var title = 'BrightStaffer';
                // Create your own title pattern
                if (toState.data && toState.data.pageTitle) title = 'Sona . ' + toState.data.pageTitle;
                $timeout(function () {
                    element.text(title);
                });
            };
            $rootScope.$on('$stateChangeStart', listener);
        }
    }
}

function validPasswordC() {
    return {
        require: 'ngModel'
        , scope: {
            reference: '=validPasswordC'

        }
        , link: function (scope, elm, attrs, ctrl) {
            ctrl.$parsers.unshift(function (viewValue, $scope) {
                var noMatch = viewValue != scope.reference
                ctrl.$setValidity('noMatch', !noMatch);
                return (noMatch) ? noMatch : !noMatch;
            });

            scope.$watch("confirmPassword", function (value) {
                ctrl.$setValidity('noMatch', value === ctrl.$viewValue);
            });
        }
    }
}


function autoCapitaliseFirstLetter($timeout) {
    return {
        require: 'ngModel'
        , link: function (scope, element, attrs, modelCtrl) {

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
        link: function (scope, element, attrs) {
            element.bind("click", function () {
                console.log(element[0]);
                var skillName = element[0].id.split('_')[1];
                console.log(skillName);
                console.log(element.parent())
                element.parent().remove();
                element.remove();
                var index = $rootScope.jobDescriptionResult.concept.indexOf(skillName);
                console.log(index);
                if (index > -1) {
                    $rootScope.jobDescriptionResult.concept.splice(index, 1);
                    scope.updateSkillSet();
                }
            });
        }
    }

}


function limitTo() {
    return {
        restrict: "A"
        , link: function (scope, elem, attrs) {
            var limit = parseInt(attrs.limitTo);
            angular.element(elem).on("keypress", function (e) {

                if (this.value.length == limit) {
                    e.preventDefault();
                    if (this.name == 'project_name')
                        scope.isProjMaxlength = true;
                    if (this.name == 'company_name')
                        scope.isComMaxlength = true;
                    if (this.name == 'location')
                        scope.isLocationMaxlength = true;
                }
            });
        }
    }
}

function onFinishRender($timeout) {
    return {
        restrict: 'A'
        , link: function (scope, element, attr) {
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
        restrict: 'A'
        , link: function (scope, ele, atts) {
            setTimeout(function () {
                $(ele).metisMenu();
            }, 1);
        }
    };
}

/**
 * minimalizaSidebar - Directive for minimalize sidebar
 */
function minimalizaSidebar($timeout, $state) {
    return {
        restrict: 'A'
        , template: '<a class="navbar-minimalize minimalize-ui btn btn-default" href="" ng-click="minimalize()"><i class="icon icon-unread"></i></a>'
        , controller: function ($scope, $element) {
            $scope.minimalize = function () {
                $("body").toggleClass("mini-navbar");
                if (!$('body').hasClass('mini-navbar') || $('body').hasClass('body-small')) {
                    // Hide menu in order to smoothly turn on when maximize menu
                    $('.nav-second-level').parent().removeClass('active');
                    $('.nav-second-level').removeClass('in');
                    $('.nav-second-level').css('height', '0px');
                    $('#side-menu').hide();
                    // For smoothly turn on menu
                    setTimeout(
                        function () {
                            if ($state.current.name == "dashboard") {
                                $('#dashboard').addClass('highlight');
                            }
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
    };
}


function clickOutside($document, $state) {
    return {
        restrict: 'A'
        , scope: {
            clickOutside: '&'
        }
        , link: function (scope, el, attr) {

            $document.on('click', function (e) {
                if (el !== e.target && !el[0].contains(e.target)) {
                    scope.$apply(function () {
                        if ($state.current.name == 'dashboard') {
                            $(".nav li.active").removeClass('active');
                            $('#dashboard').addClass('active');
                        }
                        if ($state.current.name == 'projects') {
                            $(".nav li.active").removeClass('active');
                            $('#project').addClass('active');
                            $('#allProject').addClass('active');
                        }
                        if ($state.current.name == 'create') {
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
        restrict: 'A'
        , link: function (scope, elm, attrs) {
            var ontouchFn = $parse(attrs.onTouch);
            if (navigator.userAgent.match(/Android/i) || navigator.userAgent.match(/webOS/i) || navigator.userAgent.match(/iPhone/i) || navigator.userAgent.match(/iPod/i) || navigator.userAgent.match(/BlackBerry/i) || navigator.userAgent.match(/Windows Phone/i)) {
                $rootScope.isDevice = true;
                elm.bind('touchstart', function (evt) {
                    evt.stopPropagation();
                });
                $rootScope.eventType = 'touchend';
            } else {
                $rootScope.eventType = 'click';
            }

            elm.bind($rootScope.eventType, function (evt) {
                scope.$apply(function () {
                    ontouchFn.call(scope.setActive(evt), evt.which);
                });
            });
        }
    };
}


function myDirective($rootScope) {
    return {
        restrict: 'A'
        , scope: true
        , link: function (scope, element, attr) {
            element.bind('change', function (e) {
                e.preventDefault();
                e.stopPropagation();
                if (element[0].files) {
                    if (element[0].files.length > 0) {
                        $('#addfiles').val('');
                    }
                }
                return false;
            });
        }
    };
}


function dropZone($rootScope) {
    return {
        scope: {
            action: "@"
            , autoProcess: "="
            , callBack: "="
            , dataMax: "=?"
            , mimetypes: "="
            , options: '='
        }
        , link: function (scope, element, attrs) {
            var myDropZone = {};
            scope.init = function () {
                scope.completedFiles = [];
                console.log("Creating dropzone");
                $(".talent-panel").mCustomScrollbar();
                // Autoprocess the form
                if (scope.autoProcess != null && scope.autoProcess == "false") {
                    scope.autoProcess = false;
                } else {
                    scope.autoProcess = true;
                }

                // Max file size
                if (scope.dataMax == null) {
                    scope.dataMax = Dropzone.prototype.defaultOptions.maxFilesize;
                } else {
                    scope.dataMax = parseInt(scope.dataMax);
                }

                // Message for the uploading
                if (scope.message == null) {
                    scope.message = Dropzone.prototype.defaultOptions.dictDefaultMessage;
                }
                $('#fileUpload').val('');
                var recruiter = {
                    'recruiter': $rootScope.globals.currentUser.user_email
                };
                myDropZone = new Dropzone(element[0], {
                    url: scope.action
                    , maxFilesize: 5
                    , paramName: ["file", recruiter]
                    , acceptedFiles: scope.mimetypes
                    , maxThumbnailFilesize: '5'
                    , clickable: ["#backgroundImg", "#file-dropzone", "#fileUpload"]
                    , autoProcessQueue: scope.autoProcess
                    , complete: function (r) {
                        scope.completedFiles.push(r);
                    }
                });
            }

            scope.callBack = function () {
                var queFiles = myDropZone.getQueuedFiles();
                var activeFiles = myDropZone.getActiveFiles();
                for (var i = 0; i < scope.completedFiles.length; i++) {
                    myDropZone.removeFile(scope.completedFiles[i]);
                }
                for (var i = 0; i < queFiles.length; i++) {
                    myDropZone.removeFile(queFiles[i]);
                }
                for (var i = 0; i < activeFiles.length; i++) {
                    myDropZone.removeFile(activeFiles[i]);
                }
                scope.completedFiles = [];
            }

            if (scope.options) {
                angular.extend(scope.options, {
                    clearFiles: function () {
                        scope.callBack();
                    }
                });
            }
            scope.init();
        }
    }
}


function dropDown($timeout) {
    return {
        restrict: 'A'
        , link: function (scope, element, attrs) {
            $timeout(function () {
                $(element).selectbox();
                /*$(element).multiselect({
                  includeSelectAllOption: true,
                 // enableFiltering:true
                 });*/
            });
        }
    };
}

function starRating() {
    return {
        restrict: 'A'
        , template: '<ul class="rating">' +
            '<li ng-repeat="star in stars" ng-class="star" >' +
            '\u2605' +
            '</li>' +
            '</ul>'
        , scope: {
            ratingValue: '='
            , max: '='
            , onRatingSelected: '&'
        }
        , link: function (scope, elem, attrs) {

            var updateStars = function () {
                scope.stars = [];
                for (var i = 0; i < scope.max; i++) {
                    scope.stars.push({
                        filled: i < scope.ratingValue
                    });
                }
            };

            scope.toggle = function (index) {
                scope.ratingValue = index + 1;
                scope.onRatingSelected({
                    rating: index + 1
                });
            };

            scope.$watch('ratingValue', function (oldVal, newVal) {
                if (newVal) {
                    updateStars();
                }
            });
        }
    }
}

function starRating2() {
    return {
        restrict: 'A'
        , template: '<ul class="rating">' +
            '<li ng-repeat="star in stars" ng-class="star" ng-click="toggle($index)">' +
            '\u2605' +
            '</li>' +
            '</ul>'
        , scope: {
            ratingValue: '='
            , max: '='
            , onRatingSelected: '&'
        }
        , link: function (scope, elem, attrs) {

            var updateStars = function () {
                scope.stars = [];
                for (var i = 0; i < scope.max; i++) {
                    scope.stars.push({
                        filled: i < scope.ratingValue
                    });
                }
            };

            scope.toggle = function (index) {
               if(scope.ratingValue == 1 && index == 0){
                    scope.ratingValue = index;
                    $(".rating li.filled").removeClass('filled');
                }else{
                    scope.ratingValue = index + 1;
                    updateStars();
                  }
                scope.onRatingSelected({
                    rating: scope.ratingValue
                });
            /* scope.ratingValue = index + 1;
                scope.onRatingSelected({
                    rating: index + 1
                });*/
            };
            updateStars();
            scope.$watch('ratingValue', function (oldVal, newVal) {
                if (newVal) {
                    updateStars();
                }
            });
        }
    }
}

function tableScroll($timeout) {
    return {
        restrict: 'A'
        , link: function (scope, element, attrs) {
            $timeout(function () {
                $(".tabl-scrol").mCustomScrollbar({
                    scrollButtons: {
                        enable: true
                    }
                    , axis: "x", // horizontal scrollbar

                });
            });
        }
    };
}

function viewAllScroll($timeout) {
    return {
        restrict: 'A'
        , link: function (scope, element, attrs) {
            $timeout(function () {
                $(".modal-top-concept-scroll").mCustomScrollbar({
                    scrollButtons: {
                        enable: true
                    }
                    , axis: "y", // horizontal scrollbar
                    scrollInertia: 60,
                });
            });
        }
    };
}

$(".talent-panel").mCustomScrollbar();
function pieChart($timeout) {
    return {
        restrict: 'A'
        , link: function (scope, element, attrs) {
            $timeout(function () {
                $('.easy-pie-chart').each(function () {
                    $(this).easyPieChart({
                        barColor: $(this).data('color')
                        , trackColor: '#d7d7d7'
                        , scaleColor: false
                        , lineCap: 'butt'
                        , lineWidth: 6
                        , animate: 1000
                        , size: 60
                    }).css('color', $(this).data('color'));
                });
            });
        }
    }

}

function searchDropDown($timeout, $rootScope) {
    return {
        restrict: 'A'
        , link: function (scope, element, attrs) {
            $timeout(function () {
                $(element)
                    .on('click', '.dropdown-button', function () {
                        $('.dropdown-list').toggle();
                    })
                    .on('input', '.dropdown-search', function () {
                        var target = $(this);
                        var search = target.val().toLowerCase();

                        if (!search) {
                            $('li').show();
                            return false;
                        }

                        $('#projectDrop li').each(function () {
                            var text = $(this).text().toLowerCase();
                            var match = text.indexOf(search) > -1;
                            $(this).toggle(match);
                        });
                    })
                    .on('change', '[type="checkbox"]', function () {
                        var numChecked = $('[type="checkbox"]:checked').length;
                        $('.quantity').text(numChecked || 'Any');
                    });

                // JSON of States for demo purposes
                var usStates = JSON.parse(sessionStorage.projectList);

                // <li> template
                var stateTemplate = _.template(
                    '<li>' +
                    '<label for="<%= name %>"><%= name %></label>' +
                    '</li>'
                );

                // Populate list with states
                _.each(usStates, function (s) {
                    s.capName = _.startCase(s.name.toLowerCase());
                    $('#projectDrop').append(stateTemplate(s));
                });
            });
        }
    };
}

function sliderInit($timeout) {
    return {
        restrict: 'A'
        , link: function (scope, element, attrs) {
            $timeout(function () {
                /*$('#ex3').slider({
                formatter: function(value) {
                scope.filterValue.match = value + '%';
                    return 'Current value: ' + value;
                }
            });
*/
                var slider = new Slider('#ex3', {
                    min: 0
                    , max: 100
                    , step: 1
                    , values: [0, 100]
                    , formatter: function (value) {
                        value = value ? value + '%' : '0%';
                        scope.filterValue.match = value;
                        scope.$apply();
                        return 'Current value: ' + value;
                    }
                });

            });
        }
    };
}

function selectRecord($timeout) {
    return {
        restrict: 'A'
        , link: function (scope, element, attrs) {
            $timeout(function () {
                $(element).on('change', function (evt) {
                    var selectedValue = $('#recordCount :selected').text();
                    scope.recordCount = selectedValue;
                    console.log(scope.recordCount);
                    scope.getTalents(scope.recordCount);
                });
            });
        }
    };
}

function selectProject($timeout) {
    return {
        restrict: 'A'
        , link: function (scope, element, attrs) {
            $timeout(function () {
                //$(element).selectbox();
                $('#projectListD3').change(function () {
                    var selectedValue = $('#projectListD3 :selected').text();
                    scope.projectDD = selectedValue;
                    console.log(scope.projectDD);
                });
            });
        }
    };
}

function stageScroll($timeout) {
    return {
        restrict: 'A'
        , link: function (scope, element, attrs) {
            $timeout(function () {
                $(".custom-scroll-rightbar").mCustomScrollbar({
                    scrollButtons: {
                        enable: true
                    }
                    , axis: "y", // horizontal scrollbar
                    scrollInertia: 60,

                });
            });
        }
    };
}

function datePicker($timeout) {
    return {
        restrict: 'A'
        , link: function (scope, element, attrs) {
            $timeout(function () {
                $('.datepicker').remove();
                $(element).datepicker({
                    format: "dd/mm/yyyy", //todayHighlight:true,
                    autoclose: true
                }).on('change', function () {
                    $('.datepicker').hide();
                }).on('click', function () {
                    $('.datepicker').toggle();
                });

                /*$(document).on('focus', '.datepicker',function(){
                $(element).datepicker({
                    todayHighlight:true,
                    format:'dd/mm/yyyy',
                    autoclose:true
                }).mousedown(function() {
                    $('.datepicker').show();
                });
                });*/
            });
        }
    };
}

function datePicker2($timeout) {
    return {
        restrict: 'A'
        , link: function (scope, element, attrs) {
            $timeout(function () {
                $('.datepicker').remove();
                $(element).datepicker({
                    format: "dd/mm/yyyy"
                    , todayHighlight: true
                    , autoclose: true
                }).on('change', function () {
                    $('.datepicker').hide();
                }).on('click', function () {
                    $('.datepicker').toggle();
                });
                /*.on('change', function(){
                    $('.datepicker').hide();
                })*/
                /*$('#lastContacted').mousedown(function() {
                      $('.datepicker').toggle();
                  });*/
                /*$('#lastContacted').focusout(function() {
                      $('.datepicker').remove();
                  });*/
            });
        }
    };
}


function datePickerStage($timeout) {
    return {
        restrict: 'A'
        , link: function (scope, element, attrs) {
            $timeout(function () {
                $('.datepicker').remove();
                $(element).datepicker({
                    format: "dd/mm/yyyy", //todayHighlight:true,
                    autoclose: true
                }).on('change', function () {
                    $('.datepicker').hide();
                }).on('click', function () {
                    scope.hideValidation();
                    $('.datepicker').toggle();
                });
            });
        }
    };
}

function fileDropzone() {
    return {
        restrict: 'A'
        , scope: {
//            file: '=',
            fileName: '=',
            fileObj: '='
        }
        , link: function (scope, element, attrs) {
            var validMimeTypes = attrs.fileDropzone;
            var processDragOverOrEnter = function (event) {
                if (event != null) {
                    event.preventDefault();
                }
                event.dataTransfer.effectAllowed = 'copy';
                return false;
            };
            var checkSize = function (size) {
                var _ref;
                if (((_ref = attrs.maxFileSize) === (void 0) || _ref === '') || (size / 1024) / 1024 < attrs.maxFileSize) {
                    return true;
                } else {
                    alert("File must be smaller than " + attrs.maxFileSize + " MB");
                    return false;
                }
            };
            var isTypeValid = function (type) {
                if ((validMimeTypes === (void 0) || validMimeTypes === '') || validMimeTypes.indexOf(type) > -1) {
                    return true;
                } else {
                    alert("Invalid file type.  File must be one of following types " + validMimeTypes);
                    return false;
                }
            };

            element.bind('dragover', processDragOverOrEnter);
            element.bind('dragenter', processDragOverOrEnter);

            return element.bind('drop', function (event) {
                var file, name, reader, size, type;
                if (event != null) {
                    event.preventDefault();
                }
                reader = new FileReader();
                reader.onload = function (evt) {
                    if (checkSize(size) && isTypeValid(type)) {
                        return scope.$apply(function () {
//                            scope.file = evt.target.result;
                            if (angular.isString(scope.fileName)) {
                                return scope.fileName = name;
                            }
                        });
                    }
                };
                file = event.dataTransfer.files[0];
                scope.fileObj = event.dataTransfer.files[0];
                name = file.name;
                type = file.type;
                size = file.size;
                reader.readAsDataURL(file);
                return false;
            });
        }
    };
}

function phoneMask($timeout) {

    function makePhoneNo (value) {
     var result = value;

      var ssn = value ? value.toString() : '';
      if (ssn.length > 3) {
        result = ssn.substr(0, 3) + '-';
        if (ssn.length > 6) {
          result += ssn.substr(3, 3) + '-';
          result += ssn.substr(6, 4);
        }
        else {
          result += ssn.substr(3);
        }
      }

      return result;
    }

    return {
      restrict: 'A',
      require: 'ngModel',
      link: function (scope, element, attrs, ngModel) {
        ngModel.$formatters.push(function (value) {
          return makePhoneNo(value);
        });

        // clean output as digits
        ngModel.$parsers.push(function (value) {
          var cursorPosition = element[0].selectionStart;
          var oldLength = value.toString().length;
          var nonDigits = /(^0$)|[^0-9]/g;
          var intValue = value.replace(nonDigits, '');
          if (intValue.length > 10) {
            intValue = intValue.substr(0, 10);
          }
          var newValue = makePhoneNo(intValue);
          ngModel.$setViewValue(newValue);
          ngModel.$render();
          $timeout (function(){element[0].setSelectionRange(cursorPosition + newValue.length - oldLength, cursorPosition + newValue.length - oldLength)},100);
          return intValue;
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
    .directive('dropZone', dropZone)
    .directive('dropDown', dropDown)
    .directive('starRating', starRating)
    .directive('starRating2', starRating2)
    .directive('tableScroll', tableScroll)
    .directive('pieChart', pieChart)
    .directive('searchDropDown', searchDropDown)
    .directive('sliderInit', sliderInit)
    .directive('selectRecord', selectRecord)
    .directive('stageScroll', stageScroll)
    .directive('selectProject', selectProject)
    .directive('datePicker', datePicker)
    .directive('datePicker2', datePicker2)
    .directive('datePickerStage', datePickerStage)
    .directive('fileDropzone', fileDropzone)
    .directive('viewAllScroll', viewAllScroll)
    .directive('phoneMask', phoneMask);
