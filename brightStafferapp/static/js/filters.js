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

angular
    .module('brightStaffer')
    .filter('dateFormat', dateFormat)
    .filter('capitalize', capitalize);