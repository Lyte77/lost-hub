document.addEventListener("DOMContentLoaded", () => {
    const form =
        document.getElementById("report-filters");

    const nearMeButton =
        document.getElementById("near-me-button");

    const clearButton =
        document.getElementById(
            "clear-nearby-button"
        );

    const latitudeInput =
        document.getElementById(
            "nearby-latitude"
        );

    const longitudeInput =
        document.getElementById(
            "nearby-longitude"
        );

    const nearbyInput =
        document.getElementById(
            "nearby-enabled"
        );

    const status =
        document.getElementById(
            "nearby-status"
        );


    nearMeButton.addEventListener(
        "click",
        () => {
            if (!navigator.geolocation) {
                status.textContent =
                    "Location isn't supported by your browser.";

                return;
            }


            nearMeButton.disabled = true;

            status.textContent =
                "Finding reports near you...";


            navigator.geolocation.getCurrentPosition(
                handleSuccess,
                handleError,
                {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 60000,
                }
            );
        }
    );


    function handleSuccess(position) {
        const {
            latitude,
            longitude,
        } = position.coords;


        latitudeInput.value =
            latitude;

        longitudeInput.value =
            longitude;

        nearbyInput.value = "1";


        status.textContent =
            "Showing reports near you.";

        clearButton.hidden = false;

        nearMeButton.disabled = false;


        htmx.trigger(
            form,
            "nearby"
        );
    }


    function handleError(error) {
        nearMeButton.disabled = false;

        switch (error.code) {
            case error.PERMISSION_DENIED:
                status.textContent =
                    "Location permission was denied.";
                break;

            case error.POSITION_UNAVAILABLE:
                status.textContent =
                    "Your location couldn't be determined.";
                break;

            case error.TIMEOUT:
                status.textContent =
                    "Location request timed out.";
                break;

            default:
                status.textContent =
                    "Could not get your location.";
        }
    }


    clearButton.addEventListener(
        "click",
        () => {
            latitudeInput.value = "";
            longitudeInput.value = "";
            nearbyInput.value = "0";

            status.textContent = "";

            clearButton.hidden = true;

            htmx.trigger(
                form,
                "nearby"
            );
        }
    );
});