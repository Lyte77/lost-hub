// document.addEventListener("DOMContentLoaded", () => {
//     const form =
//         document.getElementById("report-filters");

//     const nearMeButton =
//         document.getElementById("near-me-button");

//     const clearButton =
//         document.getElementById(
//             "clear-nearby-button"
//         );

//     const latitudeInput =
//         document.getElementById(
//             "nearby-latitude"
//         );

//     const longitudeInput =
//         document.getElementById(
//             "nearby-longitude"
//         );

//     const nearbyInput =
//         document.getElementById(
//             "nearby-enabled"
//         );

//     const status =
//         document.getElementById(
//             "nearby-status"
//         );

//       if (
//     !form ||
//     !nearMeButton ||
//     !clearButton ||
//     !latitudeInput ||
//     !longitudeInput ||
//     !nearbyInput ||
//     !status
// ) {
//     return;
// }


//     nearMeButton.addEventListener(
//         "click",
//         () => {
//             if (!navigator.geolocation) {
//                 status.textContent =
//                     "Location isn't supported by your browser.";

//                 return;
//             }


//             nearMeButton.disabled = true;

//             status.textContent =
//                 "Finding reports near you...";


//             navigator.geolocation.getCurrentPosition(
//                 handleSuccess,
//                 handleError,
//                 {
//                     enableHighAccuracy: true,
//                     timeout: 15000,
//                     maximumAge: 60000,
//                 }
//             );
//         }
//     );


//     function handleSuccess(position) {
//         const {
//             latitude,
//             longitude,
//         } = position.coords;


//         latitudeInput.value =
//             latitude;

//         longitudeInput.value =
//             longitude;

//         nearbyInput.value = "1";


//         status.textContent =
//             "Showing reports near you.";

//         clearButton.hidden = false;

//         nearMeButton.disabled = false;


//         htmx.trigger(
//             form,
//             "nearby"
//         );
//     }


//     function handleError(error) {
//         nearMeButton.disabled = false;

//         switch (error.code) {
//             case error.PERMISSION_DENIED:
//                 status.textContent =
//                     "Location permission was denied.";
//                 break;

//             case error.POSITION_UNAVAILABLE:
//                 status.textContent =
//                     "Your location couldn't be determined.";
//                 break;

//             case error.TIMEOUT:
//                 status.textContent =
//                     "Location request timed out.";
//                 break;

//             default:
//                 status.textContent =
//                     "Could not get your location.";
//         }
//     }


//     clearButton.addEventListener(
//         "click",
//         () => {
//             latitudeInput.value = "";
//             longitudeInput.value = "";
//             nearbyInput.value = "0";

//             status.textContent = "";

//             clearButton.hidden = true;

//             htmx.trigger(
//                 form,
//                 "nearby"
//             );
//         }
//     );


// });

document.addEventListener("DOMContentLoaded", () => {
    function setupNearbyControl({
        formId,
        triggerButtonId,
        clearButtonId,
        latitudeInputId,
        longitudeInputId,
        nearbyInputId,
        radiusSelectId,
        statusId,
        resultsId,
        eventName,
        clearResultsOnReset = false,
    }) {
        const form = document.getElementById(formId);
        const nearMeButton = document.getElementById(triggerButtonId);
        const clearButton = document.getElementById(clearButtonId);
        const latitudeInput = document.getElementById(latitudeInputId);
        const longitudeInput = document.getElementById(longitudeInputId);
        const nearbyInput = document.getElementById(nearbyInputId);
        const radiusSelect = radiusSelectId ? document.getElementById(radiusSelectId) : null;
        const status = document.getElementById(statusId);
        const resultsContainer = resultsId ? document.getElementById(resultsId) : null;

        if (
            !form ||
            !nearMeButton ||
            !clearButton ||
            !latitudeInput ||
            !longitudeInput ||
            !nearbyInput ||
            !status
        ) {
            return null;
        }

        function updateActiveStatus() {
            const radiusLabel = radiusSelect ? `within ${radiusSelect.value} km` : "near you";
            status.textContent = `Showing active reports ${radiusLabel} of your location.`;
        }

        nearMeButton.addEventListener("click", () => {
            if (!navigator.geolocation) {
                status.textContent = "Location isn't supported by your browser.";
                return;
            }

            nearMeButton.disabled = true;
            status.textContent = "Requesting your location...";

            navigator.geolocation.getCurrentPosition(
                handleSuccess,
                handleError,
                {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 60000,
                }
            );
        });

        if (radiusSelect) {
            radiusSelect.addEventListener("change", () => {
                if (nearbyInput.value === "1" && latitudeInput.value && longitudeInput.value) {
                    updateActiveStatus();
                    if (clearResultsOnReset) {
                        htmx.trigger(form, eventName);
                    }
                }
            });
        }

        function handleSuccess(position) {
            const { latitude, longitude } = position.coords;

            latitudeInput.value = latitude;
            longitudeInput.value = longitude;
            nearbyInput.value = "1";

            updateActiveStatus();

            clearButton.hidden = false;
            nearMeButton.disabled = false;

            htmx.trigger(form, eventName);
        }

        function handleError(error) {
            nearMeButton.disabled = false;

            switch (error.code) {
                case error.PERMISSION_DENIED:
                    status.textContent = "Location permission was denied. Enable location access or browse all reports.";
                    break;
                case error.POSITION_UNAVAILABLE:
                    status.textContent = "Your location couldn't be determined right now.";
                    break;
                case error.TIMEOUT:
                    status.textContent = "Location request timed out. Please try again.";
                    break;
                default:
                    status.textContent = "Could not get your location.";
            }
        }

        function resetNearbyState() {
            latitudeInput.value = "";
            longitudeInput.value = "";
            nearbyInput.value = "0";
            status.textContent = "";
            clearButton.hidden = true;
        }

        clearButton.addEventListener("click", () => {
            resetNearbyState();

            if (clearResultsOnReset && resultsContainer) {
                resultsContainer.innerHTML = "";
                return;
            }

            htmx.trigger(form, eventName);
        });

        return { form, resetNearbyState };
    }

    // Discovery page nearby control
    const discoveryNearby = setupNearbyControl({
        formId: "report-filters",
        triggerButtonId: "near-me-button",
        clearButtonId: "clear-nearby-button",
        latitudeInputId: "nearby-latitude",
        longitudeInputId: "nearby-longitude",
        nearbyInputId: "nearby-enabled",
        radiusSelectId: "nearby-radius",
        statusId: "nearby-status",
        eventName: "nearby",
    });

    // Discovery page reset, search-clear, and removable active filter chips
    const resetFiltersButton = document.getElementById("reset-filters-button");
    const clearSearchButton = document.getElementById("clear-search-btn");
    const searchInput = document.getElementById("report-search");

    function resetAllDiscoveryFilters() {
        if (!discoveryNearby) return;
        const { form, resetNearbyState } = discoveryNearby;

        const allTypeRadio = document.getElementById("filter-type-all");
        const allCategoryRadio = document.getElementById("filter-category-all");
        const radiusSelect = document.getElementById("nearby-radius");

        if (searchInput) searchInput.value = "";
        if (allTypeRadio) allTypeRadio.checked = true;
        if (allCategoryRadio) allCategoryRadio.checked = true;
        if (radiusSelect) radiusSelect.value = "5";

        resetNearbyState();
        htmx.trigger(form, "nearby");
    }

    if (resetFiltersButton && discoveryNearby) {
        resetFiltersButton.addEventListener("click", resetAllDiscoveryFilters);
    }

    if (clearSearchButton && searchInput && discoveryNearby) {
        clearSearchButton.addEventListener("click", () => {
            if (!searchInput.value) return;
            searchInput.value = "";
            searchInput.focus();
            htmx.trigger(discoveryNearby.form, "nearby");
        });
    }

    document.addEventListener("click", (event) => {
        const chipBtn = event.target.closest("[data-clear-filter]");
        if (!chipBtn) return;

        const filterKey = chipBtn.getAttribute("data-clear-filter");

        // If clicked inside homepage nearby results, reset homepage nearby widget
        if (chipBtn.closest("#home-nearby-results")) {
            const homeClearBtn = document.getElementById("home-clear-nearby-btn");
            if (homeClearBtn) homeClearBtn.click();
            return;
        }

        if (!discoveryNearby) return;
        const { form, resetNearbyState } = discoveryNearby;

        if (filterKey === "type") {
            const allTypeRadio = document.getElementById("filter-type-all");
            if (allTypeRadio) allTypeRadio.checked = true;
            htmx.trigger(form, "nearby");
        } else if (filterKey === "category") {
            const allCategoryRadio = document.getElementById("filter-category-all");
            if (allCategoryRadio) allCategoryRadio.checked = true;
            htmx.trigger(form, "nearby");
        } else if (filterKey === "q") {
            if (searchInput) searchInput.value = "";
            htmx.trigger(form, "nearby");
        } else if (filterKey === "nearby") {
            resetNearbyState();
            htmx.trigger(form, "nearby");
        } else if (filterKey === "all") {
            resetAllDiscoveryFilters();
        }
    });

    // Homepage nearby control
    setupNearbyControl({
        formId: "home-nearby-form",
        triggerButtonId: "home-near-me-btn",
        clearButtonId: "home-clear-nearby-btn",
        latitudeInputId: "home-nearby-lat",
        longitudeInputId: "home-nearby-lon",
        nearbyInputId: "home-nearby-enabled",
        radiusSelectId: "home-nearby-radius",
        statusId: "home-nearby-status",
        resultsId: "home-nearby-results",
        eventName: "homeNearby",
        clearResultsOnReset: true,
    });
});
