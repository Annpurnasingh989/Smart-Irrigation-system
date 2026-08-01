function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    } else {
        document.getElementById("location").innerHTML =
            "Geolocation is not supported.";
    }
}

function showPosition(position) {
    document.getElementById("location").innerHTML =
        "Latitude: " + position.coords.latitude +
        "<br>Longitude: " + position.coords.longitude;
}