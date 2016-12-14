angular
    .module('brightStaffer')
    .constant('REQUEST_URL', 'http://127.0.0.1:8080/');

function loginService($http ,REQUEST_URL){
    return {
      userLogin: function(data){
        console.log(data);
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

angular
    .module('brightStaffer')
    .service('loginService', loginService)
    .service('forgotService', forgotService)
    .service('resetPasswordService', resetPasswordService)
    .service('signupService', signupService);