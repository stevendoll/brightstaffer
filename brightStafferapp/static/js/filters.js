function dateFormat($filter) {
    return function (input) {
        if (input == null) {
            return "";
        }
        input = input.split('/');
        input = input[1] + '/' + input[0] + '/' + input[2];
        var _date = $filter('date')(new Date(input), 'MMM dd, yyyy');

        return _date;

    };
}

function yearFormat($filter) {
    return function (input) {
        if (!input) {
            return "";
        }
        input = input.split('/');
        input = input[1] + '/' + input[0] + '/' + input[2];
        var _date = $filter('date')(new Date(input), 'yyyy');

        return _date;

    };
}


function capitalize() {
    return function (input) {
        return (!!input) ? input.charAt(0).toUpperCase() + input.substr(1).toLowerCase() : '';
    }
}

function capitalizeAll() {
    return function (input) {
        return (!!input) ? input.toUpperCase() : '';
    }
}

function capitalizeWord() {
    return function (input) {
        if (input) {
            if (input.indexOf(' ') !== -1) {
                var inputPieces
                    , i;

                input = input.toLowerCase();
                inputPieces = input.split(' ');

                for (i = 0; i < inputPieces.length; i++) {
                    inputPieces[i] = capitalizeString(inputPieces[i]);
                }

                return inputPieces.toString().replace(/,/g, ' ');
            } else {
                input = input.toLowerCase();
                return capitalizeString(input);
            }
        }

        function capitalizeString(inputString) {
            return inputString.substring(0, 1).toUpperCase() + inputString.substring(1);
        }
    };
}

function sumOfValue() {
    return function (data, key) {
        if (angular.isUndefined(data) || angular.isUndefined(key))
            return 0;
        var sum = 0;
        angular.forEach(data, function (value) {
            sum = sum + parseInt(value[key]);
        });
        return sum;
    }
}

function dateDiff() {
    var magicNumber = (1000 * 60 * 60 * 24);

    return function (toDate, fromDate) {
        if (toDate && fromDate) {
            var dayDiff = Math.floor((toDate - fromDate) / magicNumber);
            if (angular.isNumber(dayDiff)) {
                return dayDiff + 1;
            }
        }
    };
}

function contactFormat() {

    return function (input) {
        if (!input) return input;
        input = input.toString();
        input = input.substr(0, 3) + '-' + input.substr(3);
        input = input.substr(0, 7) + '-' + input.substr(7);
        return input;
    }

}

function locationFormat() {
    return function (input) {
        input = input.trim();
        if(input == ',')
            return '';
        var b = input.split(',');
        if (b[0]) {
            b[0] = capitalizeString(b[0].trim());
        }
        if (b[1]) {
            b[1] = capitalizeString(b[1].trim());
        }
        input = b.join(', ')
        return input;

        function capitalizeString(inputString) {
            return inputString.substring(0, 1).toUpperCase() + inputString.substring(1);
        }
    }
}

angular
    .module('brightStaffer')
    .filter('dateFormat', dateFormat)
    .filter('capitalize', capitalize)
    .filter('sumOfValue', sumOfValue)
    .filter('yearFormat', yearFormat)
    .filter('capitalizeAll', capitalizeAll)
    .filter('capitalizeWord', capitalizeWord)
    .filter('contactFormat', contactFormat)
    .filter('locationFormat', locationFormat);