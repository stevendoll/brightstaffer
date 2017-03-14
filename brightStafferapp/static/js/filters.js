function dateFormat($filter)
{
 return function(input)
 {
  if(input == null){ return ""; }
     input = input.split('/');
     input =  input[1]+'/'+input[0]+'/'+input[2];
  var _date = $filter('date')(new Date(input), 'MMM dd, yyyy');

  return _date;

 };
}

function yearFormat($filter)
{
 return function(input)
 {
  if(input == null){ return ""; }
     input = input.split('/');
     input =  input[1]+'/'+input[0]+'/'+input[2];
  var _date = $filter('date')(new Date(input), 'yyyy');

  return _date;

 };
}


function capitalize() {
    return function(input) {
      return (!!input) ? input.charAt(0).toUpperCase() + input.substr(1).toLowerCase() : '';
    }
}

function capitalizeAll() {
    return function(input) {
      return (!!input) ? input.toUpperCase() : '';
    }
}

function capitalizeWord() {
  return function(input){
    if(input.indexOf(' ') !== -1){
      var inputPieces,
          i;

      input = input.toLowerCase();
      inputPieces = input.split(' ');

      for(i = 0; i < inputPieces.length; i++){
        inputPieces[i] = capitalizeString(inputPieces[i]);
      }

      return inputPieces.toString().replace(/,/g, ' ');
    }
    else {
      input = input.toLowerCase();
      return capitalizeString(input);
    }

    function capitalizeString(inputString){
      return inputString.substring(0,1).toUpperCase() + inputString.substring(1);
    }
  };
}

function sumOfValue() {
    return function (data, key) {
        if (angular.isUndefined(data) || angular.isUndefined(key))
            return 0;
        var sum = 0;
        angular.forEach(data,function(value){
            sum = sum + parseInt(value[key]);
        });
        return sum;
    }
}

function dateDiff() {
  var magicNumber = (1000 * 60 * 60 * 24);

  return function (toDate, fromDate) {
    if(toDate && fromDate){
      var dayDiff = Math.floor((toDate - fromDate) / magicNumber);
      if (angular.isNumber(dayDiff)){
        return dayDiff + 1;
      }
    }
  };
}


angular
    .module('brightStaffer')
    .filter('dateFormat', dateFormat)
    .filter('capitalize', capitalize)
    .filter('sumOfValue', sumOfValue)
    .filter('yearFormat', yearFormat)
    .filter('capitalizeAll', capitalizeAll)
    .filter('capitalizeWord', capitalizeWord);
