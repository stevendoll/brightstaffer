
var baseUrl = 'http://'+window.location.host+'/';
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

function loginService($http ,REQUEST_URL){
    return {
        userLogin: function(data){
            return $http({
                url: REQUEST_URL+'user_login/',
                method: "POST", // or "get"
                headers: {
                  'Content-Type': 'application/json; charset=utf-8',
                },
                data: JSON.stringify(data),
                dataType:'json',
                }).then( function (response){
                    return response.data;
               });
        }
    }
}

function signupService($http ,REQUEST_URL){
    return {
    userSignup: function(data){
    return $http({
        url: REQUEST_URL+'user_account/',
        method: "POST", // or "get"
        headers: {
					'Content-Type': 'application/json; charset=utf-8',
				},
        data: JSON.stringify(data),
        dataType:'json',
        }).then( function (response){
            return response.data;
       });
      }
    }
 }

function forgotService($http ,REQUEST_URL){
    return {
    forgotPassword: function(data){
    return $http({
        url: REQUEST_URL+'forget/',
        method: "POST", // or "get"
        headers: {
					'Content-Type': 'application/json; charset=utf-8',
				},
        data: JSON.stringify(data),
        dataType:'json',
        }).then( function (response){
            return response.data;
       });
      }
    }
 }

function resetPasswordService($http ,REQUEST_URL){
    return {
    resetPassword: function(data){
    return $http({
        url: REQUEST_URL+'resetapi/',
        method: "POST", // or "get"
        headers: {
					'Content-Type': 'application/json; charset=utf-8',
				},
        data: JSON.stringify(data),
        dataType:'json',
        }).then( function (response){
            return response.data;
       });
      }
    }
 }

function jobPostService($http ,REQUEST_URL){
    return {
        jobPost: function(data){
            return $http({
                url: REQUEST_URL+'job_posting/',
                method: "POST", // or "get"
                headers: {
                            'Content-Type': 'application/json; charset=utf-8',
                        },
                data: JSON.stringify(data),
                dataType:'json',
                }).then( function (response){
                    return response.data;
               });
        }
    }
}

 function alchemyAnalysis($http ,REQUEST_URL){
    return {
        alchemyAPI: function(data){
            return $http({
                url: REQUEST_URL+'alchemy_analysis/',
                method: "POST", // or "get"
                headers: {
                            'Content-Type': 'application/json; charset=utf-8',
                        },
                data: JSON.stringify(data),
                dataType:'json',
                }).then( function (response){
                    return response.data;
               });
          }
    }
 }

 function updateConcepts($http ,REQUEST_URL){
    return {
    conceptsAPI: function(data){
    return $http({
        url: REQUEST_URL+'update_concept/',
        method: "POST", // or "get"
        headers: {
					'Content-Type': 'application/json; charset=utf-8',
				},
        data: JSON.stringify(data),
        dataType:'json',
        }).then( function (response){
            return response.data;
       });
      }
    }
 }


 function publishProject($http ,REQUEST_URL){
    return {
    publish: function(data){
    return $http({
        url: REQUEST_URL+'publish_jobPost/',
        method: "POST", // or "get"
        headers: {
					'Content-Type': 'application/json; charset=utf-8',
				},
        data: JSON.stringify(data),
        dataType:'json',
        }).then( function (response){
            return response.data;
       });
      }
    }
 }

function getTopSixProjects($http ,REQUEST_URL){
    return {
    topSix: function(data){
    return $http({
        url: REQUEST_URL+'top_project_list/?format=json&recruiter='+data.recruiter+'&token='+data.token,
        method: "GET", // or "get"
        headers: {
					'Content-Type': 'application/json; charset=utf-8',
				},
        data: JSON.stringify(data),
        dataType:'json',
        }).then( function (response){
            return response.data;
       });
      }
    }
 }

 function getAllProjects($http ,REQUEST_URL){
    return {
    allProjects: function(data){
    return $http({
        url: REQUEST_URL+'project_list/?recruiter='+data.recruiter+'&token='+data.token+'&count='+data.count,
        method: "GET", // or "get"
        headers: {
					'Content-Type': 'application/json; charset=utf-8',
				},
        data: JSON.stringify(data),
        dataType:'json',
        }).then( function (response){
            return response.data;
       });
      }
    }
 }


function paginationData($http ,REQUEST_URL){
    return {
    paginationApi: function(data){
    return $http({
        url: data.url,
        method: "GET", // or "get"
        headers: {
					'Content-Type': 'application/json; charset=utf-8',
				},
        data: JSON.stringify(data),
        dataType:'json',
        }).then( function (response){
            return response.data;
       });
      }
    }
 }

function talentApis($http,REQUEST_URL) {
   return {
    getAllTalents: function(data){
    return $http({
        url: REQUEST_URL+'talent_list/?recruiter='+data.recruiter+'&token='+data.token+'&count='+data.count,
        method: "GET", // or "get"
        headers: {
					'Content-Type': 'application/json; charset=utf-8',
				},
        data: JSON.stringify(data),
        dataType:'json',
        }).then( function (response){
            return response.data;
       });
      },

     updateRecruiterName: function(data){
        return $http({
            url: REQUEST_URL+'update_recruiter/?recruiter='+data.recruiter+'&display_name='+data.display_name,
            method: "GET", // or "get"
            headers: {
                        'Content-Type': 'application/json; charset=utf-8',
                    },
            data: JSON.stringify(data),
            dataType:'json',
            }).then( function (response){
                return response.data;
           });
     },

     getCandidateProfile: function(data){
        return $http({
            url: REQUEST_URL+'talent_list/'+data.id+'/?recruiter='+data.recruiter+'&token='+data.token,
            method: "GET", // or "get"
            headers: {
                        'Content-Type': 'application/json; charset=utf-8',
                    },
            data: JSON.stringify(data),
            dataType:'json',
            }).then( function (response){
                return response.data;
           });
      },

      addTalentsToProject: function(formData, callback){
       var url = REQUEST_URL+'talent_project_add/';
       var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function()
            {
                if (xhr.readyState == 4 && xhr.status == 200)
                {
                    callback(xhr.responseText); // Another callback here
                }
            };
        xhr.open('POST', url, true);
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

      },

    deleteTalents: function(data){
        return $http({
            url: REQUEST_URL+'delete_talent/?talent='+data.talent+'&recruiter='+data.recruiter+'&is_active='+data.is_active,
            method: "DELETE", // or "get"
            headers: {
                        'Content-Type': 'application/json; charset=utf-8',
                    },
            data: JSON.stringify(data),
            dataType:'json',
            }).then( function (response){
                return response.data;
           });

    },

    updateRatings: function(data){
        return $http({
            url: REQUEST_URL+'update_rank/?talent_id='+data.id+'&rating='+data.rating,
            method: "GET", // or "get"
            headers: {
                        'Content-Type': 'application/json; charset=utf-8',
                    },
            data: JSON.stringify(data),
            dataType:'json',
            }).then( function (response){
                return response.data;
           });

    },

    talentContact: function(formData,callback){
       var url = REQUEST_URL+'talent_contact/';
       var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function()
            {
                if (xhr.readyState == 4 && xhr.status == 200)
                {
                    callback(xhr.responseText); // Another callback here
                }
            };
        xhr.open('POST', url, true);
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
    },

    addEmail: function(formData , callback){
       var url = REQUEST_URL+'talent_email/';
       var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function()
            {
                if (xhr.readyState == 4 && xhr.status == 200)
                {
                    callback(xhr.responseText); // Another callback here
                }
            };
        xhr.open('POST', url, true);
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
    }

   }
}


function searchApis($http,REQUEST_URL) {
   return{
        talentSearch: function(data){
        return $http({
            url: REQUEST_URL+'talent_search/?term='+data.keyword,
            method: "GET", // or "get"
            headers: {
                        'Content-Type': 'application/json; charset=utf-8',
                    },
            data: JSON.stringify(data),
            dataType:'json',
            }).then( function (response){
                return response.data;
           });
        }

   }
}

function searchData() {
  var talentList = [];

  return {
    addItem: addItem,
    getList: getList
  };

  function addItem(items) {
    for(var i=0;i<items.length;i++)
    talentList.push(items[i]._source);
  }

  function getList() {
    return talentList;
  }
}


angular
    .module('brightStaffer')
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
    .service('searchData', searchData);