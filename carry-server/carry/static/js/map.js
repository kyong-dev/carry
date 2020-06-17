
const car_list = appConfig.car_list;
const bookedCars = appConfig.bookedCars;
const user_location = appConfig.user_location;
const available = appConfig.available;
const unavailable = appConfig.unavailable;

function initMap() {
    // Initialise the centre of the map depending on the location of the user
    let center;
    switch (user_location) {
        case "melbourne":
            center = { lat: -37.813629, lng: 144.963058 };
            break;
        case "sydney":
            center = { lat: -33.868820, lng: 151.209290 };
            break;
    }
    let map = new google.maps.Map(document.getElementById('map'), {
        zoom: 13,
        center: center,
    });

    var infowindow = new google.maps.InfoWindow();

    // Available Cars
    for (i = 0; i < car_list.length; i++) {
        let marker = new google.maps.Marker({
            position: car_list[i],
            map: map,
            icon: available,
            title: 'Click to zoom'
        });

        let content;
        content = '<div><strong>' + car_list[i]['make'] + '</strong><button type="button" class="map_book_button" onclick="book(' + parseInt(car_list[i]['id']) + ');">Book</button><br>' +
            'Body Type: ' + car_list[i]['body_type'] + '<br>' +
            'Colour: ' + car_list[i]['colour'] + '<br>' +
            'Seats: ' + car_list[i]['seats'] + '<br>' +
            'Hourly: $' + car_list[i]['cost'].toFixed(2) + '<br>' +
            car_list[i]['address'] + ' ' + car_list[i]['suburb'] + '</div>';

        google.maps.event.addListener(marker, 'mouseover', (function (marker, i) {
            return function () {
                infowindow.setContent(content);
                infowindow.open(map, marker);
            }
        })(marker, i));

        google.maps.event.addListener(marker, 'click', (function (marker, i) {
            return function () {
                infowindow.setContent(content);
                map.setZoom(16);
                map.setCenter(marker.getPosition());
                infowindow.open(map, marker);
            }
        })(marker, i));
    }

    // Unavailable Cars
    for (i = 0; i < bookedCars.length; i++) {
        let marker = new google.maps.Marker({
            position: bookedCars[i],
            map: map,
            icon: unavailable,
            title: 'Click to zoom'
        });

        let content;
        content = '<div><strong>' + bookedCars[i]['make'] + '<br>' +
            'Body Type: ' + bookedCars[i]['body_type'] + '<br>' +
            'Colour: ' + bookedCars[i]['colour'] + '<br>' +
            'Seats: ' + bookedCars[i]['seats'] + '<br>' +
            'Hourly: $' + bookedCars[i]['cost'].toFixed(2) + '<br>' +
            bookedCars[i]['address'] + ' ' + bookedCars[i]['suburb'] + '</div>';

        google.maps.event.addListener(marker, 'mouseover', (function (marker, i) {
            return function () {
                infowindow.setContent(content);
                infowindow.open(map, marker);
            }
        })(marker, i));

        google.maps.event.addListener(marker, 'click', (function (marker, i) {
            return function () {
                infowindow.setContent(content);
                map.setZoom(16);
                map.setCenter(marker.getPosition());
                infowindow.open(map, marker);
            }
        })(marker, i));
    }

}


function book(car_id) {
    document.getElementById(car_id).click();
    document.getElementById('bookingButton').click();
}