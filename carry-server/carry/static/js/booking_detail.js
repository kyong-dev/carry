// Client ID and API key from the Developer Console
var CLIENT_ID = '234950171399-09o9ani0c3ut1brov77vq24ovm4pr3i8.apps.googleusercontent.com';
var API_KEY = 'GOOGLEMAP_API_KEY';

// Array of API discovery doc URLs for APIs used by the quickstart
var DISCOVERY_DOCS = ["https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest"];

// Authorization scopes required by the API; multiple scopes can be
// included, separated by spaces.
var SCOPES = "https://www.googleapis.com/auth/calendar.events";

var addButton = document.getElementById('add_button');
// var deleteButton = document.getElementById('delete_button');
/**
*  On load, called to load the auth2 library and API client library.
*/
function handleClientLoad() {
    gapi.load('client:auth2', initClient);
}

const car_make = appConfig.car_make;
const car_full_address = appConfig.car_full_address;
const start_datetime = appConfig.start_datetime;
const end_datetime = appConfig.end_datetime;
const booking_id = appConfig.booking_id;

/**
*  Initializes the API client library and sets up sign-in state
*  listeners.
*/
function initClient() {
    gapi.client.init({ apiKey: API_KEY, clientId: CLIENT_ID, discoveryDocs: DISCOVERY_DOCS, scope: SCOPES }).then(function () {
        addButton.onclick = handleAddButtonClick;
    }, function (error) {
        document.getElementById('content').innerHTML = JSON.stringify(error, null, 2);
    });
}

/**
*  Sign in the user upon button click.
*/
function handleAddButtonClick(event) {
    if (!gapi.auth2.getAuthInstance().isSignedIn.get()) {
        gapi.auth2.getAuthInstance().signIn().then(() => {
            if (gapi.auth2.getAuthInstance().isSignedIn.get()) {
                addEvent();
            }
        });
    } else {
        addEvent();
    }
}

/**
* Print the summary and start datetime/date of the next ten events in
* the authorized user's calendar. If no events are found an
* appropriate message is printed.
*/
function addEvent() {
    var event = {
        'summary': 'Carry (' + car_make + ')',
        'location': car_full_address,
        'description': booking_id,
        'start': {
            'dateTime': start_datetime,
            'timeZone': 'Australia/Melbourne'
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': 'Australia/Melbourne'
        },
        'reminders': {
            'useDefault': false,
            'overrides': [
                {
                    'method': 'email',
                    'minutes': 24 * 60
                }, {
                    'method': 'popup',
                    'minutes': 10
                }
            ]
        }
    };

    var request = gapi.client.calendar.events.insert({ 'calendarId': 'primary', 'resource': event });

    request.execute((event) => {
        if (event.id != undefined) {

            fetch("/booking/detail/event", {
                method: "POST",
                credentials: "include",
                body: JSON.stringify(event),
                cache: "no-cache",
                headers: new Headers(
                    { "content-type": "application/json" }
                )
            }).then(res => {
                gapi.auth2.getAuthInstance().signOut();
                addButton.style.display = 'none';
                document.getElementById('content').innerHTML = 'Event has been successfully created: <a target="_blank "href="' + event.htmlLink + '">Go Check</a>';
            });
        } else {
            document.getElementById('content').innerHTML = 'There was an error with connecting to your calendar';
        }
    });

}