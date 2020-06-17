var today = new Date();
var time = parseInt(today.toLocaleString().substring(12, 14));
var start_date = document.getElementById("start_date");
var end_date = document.getElementById("end_date");
var start_time = document.getElementById("start_time");
var end_time = document.getElementById("end_time");
var duration_display = document.getElementById("duration_display");
var search = document.getElementById("search");

today = today.getFullYear() + '-' + (
    '0' + (
        today.getMonth() + 1
    )
).slice(-2) + '-' + (
    '0' + today.getDate()
).slice(-2);

const queryString = window.location.search;
const date_validator = () => {
    let start_date_val = document.getElementById("start_date").value;
    let end_date_val = document.getElementById("end_date").value;
    let start_time_val = document.getElementById("start_time").value;
    let end_time_val = document.getElementById("end_time").value;

    // Validate DateTime
    if (start_date_val > end_date_val || today > start_date_val) {
        invalid()
    } else if (today == start_date_val && parseInt(start_time_val) < parseInt(time)) {
        invalid()
    } else if (start_date_val == end_date_val && parseInt(end_time_val) < parseInt(start_time_val)) {
        invalid()
    } else {
        duration_display.innerHTML = getDuration(start_date_val, end_date_val, start_time_val, end_time_val);
        document.getElementById('searchSubmit').disabled = false;
        document.getElementById('searchSubmit').click();
    }
    document.getElementById("car_table").style.display = "none";
};

const urlParams = new URLSearchParams(queryString);
start_date.value = urlParams.get('start_date');
end_date.value = urlParams.get('end_date');
start_time.value = urlParams.get('start_time');
end_time.value = urlParams.get('end_time');
search.value = urlParams.get('search');
duration_input = getDuration(start_date.value, end_date.value, start_time.value, end_time.value);
if (duration_input > 0) {
    duration_display.innerHTML = duration_input;
} else {
    invalid();
}

document.getElementById('start_datetime').value = start_date.value + " " + start_time.value + ":00:00";
document.getElementById('end_datetime').value = end_date.value + " " + end_time.value + ":00:00";
document.getElementById('duration').value = getDuration(start_date.value, end_date.value, start_time.value, end_time.value);

var car_id_radio = document.forms['booking'].elements['car_id'];
// loop through list
for (var i = 0, len = car_id_radio.length; i < len; i++) {
    car_id_radio[i].onclick = function () {
        // assign onclick handler function to each
        document.getElementById('car_id').value = this.value;
    };
}

function invalid() {
    duration_display.innerHTML = "<span style='color: red;'>Invalid</span>";
    document.getElementById('searchSubmit').disabled = true;
}

function getDuration(start_date_val, end_date_val, start_time_val, end_time_val) {
    start = new Date(Date.UTC(start_date_val.substring(0, 4), start_date_val.substring(5, 7), start_date_val.substring(8, 10), start_time_val, '00', '00'))
    end = new Date(Date.UTC(end_date_val.substring(0, 4), end_date_val.substring(5, 7), end_date_val.substring(8, 10), end_time_val, '00', '00'))
    hours = (end - start) / 3600000
    return hours;
}