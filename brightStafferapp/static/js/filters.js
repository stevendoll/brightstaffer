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

function capitalize() {
    return function(input) {
      return (!!input) ? input.charAt(0).toUpperCase() + input.substr(1).toLowerCase() : '';
    }
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
    .filter('dateDiff', dateDiff);