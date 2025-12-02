// Location Tracker for Student Login
(function () {
  "use strict";

  // Check if there's a login activity ID in session (set on every login)
  // This will be triggered only after a fresh login
  fetch("/check-login-session/", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (!data.should_track) {
        return; // No fresh login, skip location request
      }

      // Check if geolocation is supported
      if (!navigator.geolocation) {
        console.log("Geolocation is not supported by this browser.");
        return;
      }

      // Request location with timeout
      const options = {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      };

      navigator.geolocation.getCurrentPosition(
        function (position) {
          // Success - send location to server
          const locationData = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          };

          fetch("/update-login-location/", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(locationData),
          })
            .then((response) => response.json())
            .then((data) => {
              if (data.success) {
                console.log("Location recorded successfully");
              } else {
                console.log("Failed to record location:", data.message);
              }
            })
            .catch((error) => {
              console.error("Error sending location:", error);
            });
        },
        function (error) {
          // User denied or error occurred
          console.log("Location access denied or error:", error.message);
          // Continue without location - server will have null values
        },
        options
      );
    })
    .catch((error) => {
      console.error("Error checking login session:", error);
    });
})();
