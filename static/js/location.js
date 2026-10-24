document.addEventListener("DOMContentLoaded", () => {

    
  

    const currentLocationButton =
        document.getElementById("use-current-location");

    const mapButton =
        document.getElementById("choose-location-map");

    const mapWrapper =
        document.getElementById("map-wrapper");

    const locationStatus =
        document.getElementById("location-status");


    const latitudeInput =
        document.getElementById("id_latitude");

    const longitudeInput =
        document.getElementById("id_longitude");

    const accuracyInput =
        document.getElementById("id_location_accuracy");

    const locationNameInput =
        document.getElementById("id_location_name");

    const locationSourceInput =
        document.getElementById("id_location_source");

   


    let map = null;
    let marker = null;


    /*
     * -----------------------------
     * CURRENT LOCATION
     * -----------------------------
     */

    currentLocationButton.addEventListener("click", () => {
        if (!navigator.geolocation) {
            locationStatus.textContent =
                "Your browser does not support location.";

            return;
        }

        currentLocationButton.disabled = true;

        locationStatus.textContent =
            "Finding your current location...";


        navigator.geolocation.getCurrentPosition(
            handleLocationSuccess,
            handleLocationError,
            {
                enableHighAccuracy: true,
                timeout: 15000,
                maximumAge: 0,
            }
        );
    });


    async function handleLocationSuccess(position) {
        const {
            latitude,
            longitude,
            accuracy,
        } = position.coords;


        await setLocation({
            latitude,
            longitude,
            accuracy,
            source: "gps",
        });


        currentLocationButton.disabled = false;

        currentLocationButton.textContent =
            "Update current location";


        /*
         * If map already exists,
         * move it to the GPS position.
         */

        if (map) {
            updateMapPosition(
                latitude,
                longitude
            );
        }
    }


    function handleLocationError(error) {
        currentLocationButton.disabled = false;

        switch (error.code) {
            case error.PERMISSION_DENIED:
                locationStatus.textContent =
                    "Location permission was denied. You can choose the location manually on the map.";
                break;

            case error.POSITION_UNAVAILABLE:
                locationStatus.textContent =
                    "Your current location is unavailable. Try choosing it on the map.";
                break;

            case error.TIMEOUT:
                locationStatus.textContent =
                    "Getting your location took too long. Please try again.";
                break;

            default:
                locationStatus.textContent =
                    "Could not determine your location.";
        }
    }



    /*
     * -----------------------------
     * MAP
     * -----------------------------
     */
mapButton.addEventListener("click", async () => {
    mapWrapper.classList.remove("hidden");

    const existingLatitude =
        parseFloat(latitudeInput.value);

    const existingLongitude =
        parseFloat(longitudeInput.value);

    const hasExistingLocation =
        !Number.isNaN(existingLatitude) &&
        !Number.isNaN(existingLongitude);


    if (hasExistingLocation) {
        showMapAtLocation(
            existingLatitude,
            existingLongitude
        );

        return;
    }


    locationStatus.textContent =
        "Finding your current location...";


    if (!navigator.geolocation) {
        showFallbackMap();
        return;
    }


    navigator.geolocation.getCurrentPosition(
        (position) => {
            const {
                latitude,
                longitude,
            } = position.coords;

            showMapAtLocation(
                latitude,
                longitude
            );
        },

        () => {
            showFallbackMap();
        },

        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 60000,
        }
    );
});

function showMapAtLocation(
    latitude,
    longitude
) {
    if (!map) {
        initialiseMap(
            latitude,
            longitude,
            16
        );
    } else {
        map.setView(
            [latitude, longitude],
            16
        );
    }

    createOrMoveMarker(
        latitude,
        longitude
    );


    setTimeout(() => {
        map.invalidateSize();
    }, 100);
}


function initialiseMap(
    latitude,
    longitude,
    zoom = 16
) {
    const mapContainer =
        document.getElementById("location-map");

    const maptilerKey =
        mapContainer.dataset.maptilerKey;


    map = L.map("location-map").setView(
        [
            latitude,
            longitude,
        ],
        zoom
    );


    L.tileLayer(
        `https://api.maptiler.com/maps/streets-v4/256/{z}/{x}/{y}.png?key=${maptilerKey}`,
        {
            maxZoom: 19,
            attribution:
                '&copy; MapTiler &copy; OpenStreetMap contributors',
        }
    ).addTo(map);


    map.on("click", async (event) => {
        const {
            lat,
            lng,
        } = event.latlng;


        createOrMoveMarker(
            lat,
            lng
        );


        await setLocation({
            latitude: lat,
            longitude: lng,
            accuracy: null,
            source: "map",
        });
    });
}   

function showFallbackMap() {
    locationStatus.textContent =
        "We couldn't access your location. Choose the location on the map.";

    if (!map) {
        initialiseMap(
            4.8156,
            7.0498,
            12
        );
    }

    setTimeout(() => {
        map.invalidateSize();
    }, 100);
}

    function createOrMoveMarker(
        latitude,
        longitude
    ) {
        if (!marker) {

            marker = L.marker(
                [
                    latitude,
                    longitude,
                ],
                {
                    draggable: true,
                }
            ).addTo(map);


            /*
             * When user finishes dragging,
             * save the new location.
             */

            marker.on(
                "dragend",
                async (event) => {
                    const position =
                        event.target.getLatLng();


                    await setLocation({
                        latitude: position.lat,
                        longitude: position.lng,
                        accuracy: null,
                        source: "map",
                    });
                }
            );

        } else {

            marker.setLatLng(
                [
                    latitude,
                    longitude,
                ]
            );
        }
    }


    function updateMapPosition(
        latitude,
        longitude
    ) {
        map.setView(
            [
                latitude,
                longitude,
            ],
            16
        );

        createOrMoveMarker(
            latitude,
            longitude
        );
    }



    /*
     * -----------------------------
     * SHARED LOCATION HANDLER
     * -----------------------------
     */

    async function setLocation({
        latitude,
        longitude,
        accuracy = null,
        source,
    }) {

        latitudeInput.value =
            latitude;

        longitudeInput.value =
            longitude;

        accuracyInput.value =
            accuracy ?? "";

        locationSourceInput.value =
            source;


        locationStatus.textContent =
            "Getting place name...";


        try {
            const locationName =
                await reverseGeocode(
                    latitude,
                    longitude
                );


            locationNameInput.value =
                locationName;


            locationStatus.textContent =
                `📍 ${locationName}`;

        } catch (error) {

            console.error(
                "Reverse geocoding failed:",
                error
            );


            locationNameInput.value = "";


            locationStatus.textContent =
                "Location selected.";
        }
    }



    /*
     * -----------------------------
     * DJANGO REVERSE GEOCODING
     * -----------------------------
     */

    async function reverseGeocode(
        latitude,
        longitude
    ) {

        const url = new URL(
            currentLocationButton.dataset
                .reverseGeocodeUrl,

            window.location.origin
        );


        url.searchParams.set(
            "lat",
            latitude
        );

        url.searchParams.set(
            "lon",
            longitude
        );


        const response =
            await fetch(url);


        if (!response.ok) {
            throw new Error(
                "Reverse geocoding failed."
            );
        }


        const data =
            await response.json();


        return data.location_name;
    }
});



// document.addEventListener("DOMContentLoaded", () => {
//     console.log("Leaflet available:", typeof L);

//     const container = document.getElementById("location-map");

//     console.log("Map container:", container);
//     console.log("Height:", container.offsetHeight);
//     console.log("Width:", container.offsetWidth);

//     const map = L.map("location-map").setView(
//         [9.0820, 8.6753],
//         6
//     );

//     console.log("Map created:", map);

//     const tiles =L.tileLayer(
//     "https://api.maptiler.com/maps/streets-v4/256/{z}/{x}/{y}.png?key=BpK6rcnO1OH0I73mmPQi",
//     {
//         maxZoom: 19,
//         attribution:
//             '&copy; MapTiler &copy; OpenStreetMap contributors'
//     }
// ).addTo(map);

//     tiles.on("loading", () => {
//         console.log("Tiles loading...");
//     });

//     tiles.on("load", () => {
//         console.log("Tiles loaded successfully.");
//     });

//     tiles.on("tileerror", (error) => {
//         console.error("Tile failed:", error);
//     });

//     tiles.addTo(map);
// });