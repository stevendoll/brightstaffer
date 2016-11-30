
mainApp.factory('appService', ['$resource','$http','REQUEST_URL', function($resource, $http ,REQUEST_URL){
 var factory = {};
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
    },

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
    },
  }



}]);

