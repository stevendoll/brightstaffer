var baseUrl = 'http://'+window.location.host+'/';
angular
    .module('brightStaffer')
.constant('REQUEST_URL', baseUrl);

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
        url: REQUEST_URL+'top_projectlist/',
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

 function getAllProjects($http ,REQUEST_URL){
    return {
    allProjects: function(data){
    return $http({
        url: REQUEST_URL+'publish_project/',
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


function paginationData($http ,REQUEST_URL){
    return {
    paginationApi: function(data){
    return $http({
        url: REQUEST_URL+'pagination/',
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
    .service('paginationData', paginationData);


