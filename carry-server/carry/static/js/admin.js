var report = (car_id) => {
    var desc = prompt("Enter Detail");
    if (desc != null && desc != "") {
        document.getElementById("car_id").value = car_id;
        document.getElementById("detail").value = desc;
        document.getElementById("reportForm").submit();
    } 
}