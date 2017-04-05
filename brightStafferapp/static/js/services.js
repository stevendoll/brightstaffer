var baseUrl = 'http://' + window.location.host + '/';
angular
    .module('brightStaffer')
    .constant('REQUEST_URL', baseUrl)

.config(['$httpProvider', function ($httpProvider) {
    //Reset headers to avoid OPTIONS request (aka preflight)
    $httpProvider.defaults.headers.common = {};
    $httpProvider.defaults.headers.post = {};
    $httpProvider.defaults.headers.put = {};
    $httpProvider.defaults.headers.patch = {};
}]);

function appService($rootScope, $http) {
    return {
        httpRequest: function (data, callback) {
            $rootScope.showLoader(true);
            $http(data).success(function (response) {
                $rootScope.showLoader(false);
                callback(response || {});
            }).error(function (error) {
                $rootScope.showLoader(false);
                callback({
                    success: false,
                    errorstring: 'Some problem occured.'
                });
            });
        }
    }
}

function loginService($rootScope, $http, REQUEST_URL) {
    return {
        userLogin: function (data) {
            $rootScope.showLoader(true);
            return $http({
                url: REQUEST_URL + 'user_login/'
                , method: "POST", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                , }
                , data: JSON.stringify(data)
                , dataType: 'json'
            , }).then(function (response) {
                $rootScope.showLoader(false);
                return response.data;
            });
        }
    }
}

function signupService($http, REQUEST_URL) {
    return {
        userSignup: function (data) {
            return $http({
                url: REQUEST_URL + 'user_account/'
                , method: "POST", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                , }
                , data: JSON.stringify(data)
                , dataType: 'json'
            , }).then(function (response) {
                return response.data;
            });
        }
    }
}

function forgotService($http, REQUEST_URL) {
    return {
        forgotPassword: function (data) {
            return $http({
                url: REQUEST_URL + 'forget/'
                , method: "POST", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                , }
                , data: JSON.stringify(data)
                , dataType: 'json'
            , }).then(function (response) {
                return response.data;
            });
        }
    }
}

function resetPasswordService($http, REQUEST_URL) {
    return {
        resetPassword: function (data) {
            return $http({
                url: REQUEST_URL + 'resetapi/'
                , method: "POST", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                , }
                , data: JSON.stringify(data)
                , dataType: 'json'
            , }).then(function (response) {
                return response.data;
            });
        }
    }
}

function jobPostService($http, REQUEST_URL) {
    return {
        jobPost: function (data) {
            return $http({
                url: REQUEST_URL + 'job_posting/'
                , method: "POST", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                , }
                , data: JSON.stringify(data)
                , dataType: 'json'
            , }).then(function (response) {
                return response.data;
            });
        }
    }
}

function alchemyAnalysis($rootScope, $http, REQUEST_URL) {
    return {
        alchemyAPI: function (data) {
            $rootScope.showLoader(true);
            return $http({
                url: REQUEST_URL + 'alchemy_analysis/'
                , method: "POST", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                , }
                , data: JSON.stringify(data)
                , dataType: 'json'
            , }).then(function (response) {
                $rootScope.showLoader(false);
                return response.data;
            });
        }
    }
}

function updateConcepts($http, REQUEST_URL) {
    return {
        conceptsAPI: function (data) {
            return $http({
                url: REQUEST_URL + 'update_concept/'
                , method: "POST", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                , }
                , data: JSON.stringify(data)
                , dataType: 'json'
            , }).then(function (response) {
                return response.data;
            });
        }
    }
}


function publishProject($http, REQUEST_URL) {
    return {
        publish: function (data) {
            return $http({
                url: REQUEST_URL + 'publish_jobPost/'
                , method: "POST", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                , }
                , data: JSON.stringify(data)
                , dataType: 'json'
            , }).then(function (response) {
                return response.data;
            });
        }
    }
}

function getTopSixProjects($http, REQUEST_URL) {
    return {
        topSix: function (data) {
            return $http({
                url: REQUEST_URL + 'top_project_list/?format=json&recruiter=' + data.recruiter + '&token=' + data.token
                , method: "GET", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                , }
                , data: JSON.stringify(data)
                , dataType: 'json'
            , }).then(function (response) {
                return response.data;
            });
        }
    }
}

function getAllProjects($http, $rootScope, REQUEST_URL) {
    return {
        allProjects: function (data) {
            $rootScope.showLoader(true);
            $rootScope.apiHiCounter ++;
            return $http({
                url: REQUEST_URL + 'project_list/?recruiter=' + data.recruiter + '&token=' + data.token + '&count=' + data.count
                , method: "GET", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                , }
                , data: JSON.stringify(data)
                , dataType: 'json'
            , }).then(function (response) {
                $rootScope.apiHiCounter --;
                if($rootScope.apiHiCounter <= 0){
                    $rootScope.apiHiCounter = 0;
                    $rootScope.showLoader(false);
                }

                return response.data;
            });
        }
    }
}


function paginationData($http, REQUEST_URL) {
    return {
        paginationApi: function (data) {
            return $http({
                url: data.url
                , method: "GET", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                , }
                , data: JSON.stringify(data)
                , dataType: 'json'
            , }).then(function (response) {
                return response.data;
            });
        }
    }
}

function talentApis($rootScope, $http, REQUEST_URL) {
    return {
        getAllTalents: function (data) {
            $rootScope.showLoader(true);
            return $http({
                url: REQUEST_URL + 'talent_list/?recruiter=' + data.recruiter + '&token=' + data.token + '&count=' + data.count
                , method: "GET", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                , }
                , data: JSON.stringify(data)
                , dataType: 'json'
            , }).then(function (response) {
                $rootScope.showLoader(false);
                return response.data;
            });
        },

        getTalentAllStages: function (data) {
            $rootScope.showLoader(true);
            return $http({
                url: REQUEST_URL + 'talent_view_allstages/?talent_id=' + data.talent_id
                , method: "GET", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                , }
                , data: JSON.stringify(data)
                , dataType: 'json'
            }).then(function (response) {
                $rootScope.showLoader(false);
                return response.data;
            });
        },

        updateRecruiterName: function (data) {
            $rootScope.showLoader(true);
            return $http({
                url: REQUEST_URL + 'update_recruiter/?recruiter=' + data.recruiter + '&display_name=' + data.display_name
                , method: "GET", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                , }
                , data: JSON.stringify(data)
                , dataType: 'json'
            , }).then(function (response) {
                $rootScope.showLoader(false);
                return response.data;
            });
        },

        getCandidateProfile: function (data) {
            $rootScope.showLoader(true);
            return $http({
                url: REQUEST_URL + 'talent_list/' + data.id + '/?recruiter=' + data.recruiter + '&token=' + data.token
                , method: "GET", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                , }
                , data: JSON.stringify(data)
                , dataType: 'json'
            , }).then(function (response) {
                $rootScope.showLoader(false);
                return response.data;
            });
        },

        addTalentsToProject: function (data) {
            /*var url = REQUEST_URL+'talent_project_add/';
       var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function()
            {
                if (xhr.readyState == 4 && xhr.status == 200)
                {
                    callback(xhr.responseText); // Another callback here
                }
            };
        xhr.open('GET', url, true);
        headers = {
        "Accept": "application/json",
        "Cache-Control": "no-cache",
        "X-Requested-With": "XMLHttpRequest"
        };
        for (headerName in headers) {
            headerValue = headers[headerName];
            if (headerValue) {
              xhr.setRequestHeader(headerName, headerValue);
            }
        }
        xhr.send(formData);
*/
            $rootScope.showLoader(true);
            return $http({
                url: REQUEST_URL + 'talent_project_add/?talent_id[]=' + data.talent + '&recruiter=' + data.recruiter + '&token=' + data.token + '&project_id=' + data.project_id
                , method: "GET", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                , }
                , data: JSON.stringify(data)
                , dataType: 'json'
            , }).then(function (response) {
                $rootScope.showLoader(false);
                return response.data;
            });

        },

        deleteTalents: function (data) {
              $rootScope.apiHiCounter ++;
             $rootScope.showLoader(true);
            return $http({
                url: REQUEST_URL + 'delete_talent/?talent=' + data.talent + '&recruiter=' + data.recruiter + '&is_active=' + data.is_active
                , method: "GET", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                , }
                , data: JSON.stringify(data)
                , dataType: 'json'
            , }).then(function (response) {
                 $rootScope.apiHiCounter --;
                 if($rootScope.apiHiCounter <= 0 ){
                     $rootScope.apiHiCounter = 0;
                     $rootScope.showLoader(false);
                 }
                return response.data;
            });

        },

        updateRatings: function (data) {
            return $http({
                url: REQUEST_URL + 'update_rank/?talent_id=' + data.id + '&rating=' + data.rating
                , method: "GET", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                , }
                , data: JSON.stringify(data)
                , dataType: 'json'
            , }).then(function (response) {
                return response.data;
            });

        },

        talentContact: function (formData, callback) {
            var url = REQUEST_URL + 'talent_contact/';
            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    callback(xhr.responseText); // Another callback here
                }
            };
            xhr.open('POST', url, true);
            headers = {
                "Accept": "application/json"
                , "Cache-Control": "no-cache"
                , "X-Requested-With": "XMLHttpRequest"
            };
            for (headerName in headers) {
                headerValue = headers[headerName];
                if (headerValue) {
                    xhr.setRequestHeader(headerName, headerValue);
                }
            }
            xhr.send(formData);
        },

        addEmail: function (formData, callback) {
            var url = REQUEST_URL + 'talent_email/';
            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    callback(xhr.responseText); // Another callback here
                }
            };
            xhr.open('POST', url, true);
            headers = {
                "Accept": "application/json"
                , "Cache-Control": "no-cache"
                , "X-Requested-With": "XMLHttpRequest"
            };
            for (headerName in headers) {
                headerValue = headers[headerName];
                if (headerValue) {
                    xhr.setRequestHeader(headerName, headerValue);
                }
            }
            xhr.send(formData);
        },

        addTalentStages: function (formData, callback) {
            var url = REQUEST_URL + 'talent_add_stage/';
            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    $rootScope.showLoader(false);
                    callback(xhr.responseText); // Another callback here
                }
            };
            xhr.open('POST', url, true);
            headers = {
                "Accept": "application/json"
                , "Cache-Control": "no-cache"
                , "X-Requested-With": "XMLHttpRequest"
            };
            for (headerName in headers) {
                headerValue = headers[headerName];
                if (headerValue) {
                    xhr.setRequestHeader(headerName, headerValue);
                }
            }
            $rootScope.showLoader(true);
            xhr.send(formData);
        },

        filterTalentData: function (data) {
            $rootScope.apiHiCounter ++;
            $rootScope.showLoader(true);
            return $http({
                url: REQUEST_URL + 'talent_search/?talent_company=' + data.company + '&rating=' + data.rating + '&project_match=' + data.project_match + '&recruiter=' + data.recruiter + '&concepts=' + data.concepts + '&projects=' + data.projects + '&stages=' + data.stages + '&last_contacted=' + data.contacted + '&date_added=' + data.date + '&term=' + data.term + '&ordering=' + data.ordering + '&is_active=' + data.active + '&page=' + data.page + '&count=' + data.count
                , method: "GET", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                    , 'token': $rootScope.globals.currentUser.token
                    , 'recruiter': $rootScope.globals.currentUser.user_email
                }
                , data: JSON.stringify(data)
                , dataType: 'json'
            , }).then(function (response) {
                $rootScope.apiHiCounter --;
                if($rootScope.apiHiCounter <=0){
                    $rootScope.apiHiCounter = 0;
                    $rootScope.showLoader(false);
                }
                return response.data;
            }).error(function (response){
                $rootScope.apiHiCounter --;
                if($rootScope.apiHiCounter <=0){
                    $rootScope.apiHiCounter = 0;
                    $rootScope.showLoader(false);
                }
            });;
        }




    }
}


function searchApis($rootScope, $http, REQUEST_URL) {
    return {
        talentSearch: function (data) {
            $rootScope.apiHiCounter ++;
            $rootScope.showLoader(true);
            data.term = data.keyword;
            delete data.keyword;
            return $http({
                url: REQUEST_URL + 'talent_search/'
                , method: "GET", // or "get"
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                    , 'token': $rootScope.globals.currentUser.token
                    , 'recruiter': $rootScope.globals.currentUser.user_email
                }
                , params: data
                , dataType: 'json'
            }).then(function (response) {
                 $rootScope.apiHiCounter --;
                 if($rootScope.apiHiCounter <= 0){
                    $rootScope.apiHiCounter = 0;
                    $rootScope.showLoader(false);
                }
                return response.data;
            });
        }
    }
}

function tableService($rootScope, $http, REQUEST_URL, appService) {
    return {
        deleteProjects: function (data, callback) {
            var param = {
                url: REQUEST_URL + 'delete_projects/'
                , method: "GET"
                , headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                    , 'token': $rootScope.globals.currentUser.token
                    , 'recruiter': $rootScope.globals.currentUser.user_email
                }
                , params: data
                , dataType: 'json'
            }
            appService.httpRequest(param, callback);
        }
    }
}

function searchData() {
    var talentList = [];

    return {
        addItem: addItem
        , getList: getList
    };

    function addItem(items) {
        for (var i = 0; i < items.length; i++)
            talentList.push(items[i]._source);
    }

    function getList() {
        return talentList;
    }
}

function createTalentFormService($rootScope, REQUEST_URL, appService) {
    return {
        createTalent: function (data, callback) {
            var param = {
                url: REQUEST_URL + 'talent_add/'
                , method: "POST"
                , headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                    , 'token': $rootScope.globals.currentUser.token
                    , 'recruiter': $rootScope.globals.currentUser.user_email
                }
                , data: data
                , dataType: 'json'
            }
            appService.httpRequest(param, callback);
        }
    }
}


angular
    .module('brightStaffer')
    .service('appService', appService)
    .service('loginService', loginService)
    .service('forgotService', forgotService)
    .service('resetPasswordService', resetPasswordService)
    .service('signupService', signupService)
    .service('jobPostService', jobPostService)
    .service('alchemyAnalysis', alchemyAnalysis)
    .service('updateConcepts', updateConcepts)
    .service('publishProject', publishProject)
    .service('getTopSixProjects', getTopSixProjects)
    .service('getAllProjects', getAllProjects)
    .service('paginationData', paginationData)
    .service('talentApis', talentApis)
    .service('searchApis', searchApis)
    .service('tableService', tableService)
    .service('searchData', searchData)
    .service('createTalentFormService', createTalentFormService);
