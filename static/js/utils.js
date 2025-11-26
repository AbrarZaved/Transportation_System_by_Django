// utils.js
export function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
export async function showToast(title, message) {
  var toasts = {
    "Logged Out!": "You have been successfully logged out.",
    "Logged In!": "Welcome back! You have successfully logged in.",
    "Not Allowed": "Only DIU students are allowed to access this system.",
    "OTP Sent!": "A One-Time Password has been sent to your registered email.",
  };
  const toastTitle = document.getElementById("toast-title");
  const toastMessage = document.getElementById("toast-message");
  const toastNotification = document.getElementById("toast-notification");
  toastNotification.classList.add("translate-x-full", "opacity-0");
  toastNotification.classList.remove("hidden");
  if (title == "Logged In!") {
    toastTitle.textContent = message;
    toastMessage.textContent = toasts["Logged In!"];
    console.log(title, message);
  } else {
    toastTitle.textContent = title;
    console.log(title);
    toastMessage.textContent = toasts[title] || message || "";
  }

  setTimeout(() => {
    toastNotification.classList.remove("translate-x-full", "opacity-0");
  }, 50);
  setTimeout(() => {
    toastNotification.classList.add("translate-x-full", "opacity-0");
    toastNotification.addEventListener("transitionend", function handler() {
      toastNotification.classList.add("hidden");
      toastNotification.removeEventListener("transitionend", handler);
    });
  }, 3000);
}
function convertTo24Hour(timeStr) {
  // Handle null, undefined, or empty string
  if (!timeStr || typeof timeStr !== "string") {
    return null;
  }

  // Check if already in 24-hour format (HH:MM without AM/PM)
  if (/^\d{1,2}:\d{2}$/.test(timeStr.trim())) {
    const [hours, minutes] = timeStr.trim().split(":").map(Number);

    // Validate hours and minutes for 24-hour format
    if (
      isNaN(hours) ||
      isNaN(minutes) ||
      hours < 0 ||
      hours > 23 ||
      minutes < 0 ||
      minutes > 59
    ) {
      return null;
    }

    return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(
      2,
      "0"
    )}`;
  }

  // Handle 12-hour format with AM/PM
  const [time, modifier] = timeStr.split(" ");
  console.log(time, modifier);

  // Additional validation for 12-hour format
  if (!time || !modifier) {
    return null;
  }

  let [hours, minutes] = time.split(":").map(Number);

  // Validate hours and minutes for 12-hour format
  if (
    isNaN(hours) ||
    isNaN(minutes) ||
    hours < 1 ||
    hours > 12 ||
    minutes < 0 ||
    minutes > 59
  ) {
    return null;
  }

  if (modifier === "PM" && hours !== 12) {
    hours += 12;
  }
  if (modifier === "AM" && hours === 12) {
    hours = 0;
  }

  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(
    2,
    "0"
  )}`;
}

export async function filterRoutesByTime(routes, selectedTime) {
  if (selectedTime === "all") return routes;
  if (!routes || routes.length === 0) return [];
  const selected24HrTime = convertTo24Hour(selectedTime);
  // If selectedTime conversion failed, return all routes
  if (!selected24HrTime) {
    return routes;
  }

  const filteredRoutes = routes.filter((route) => {
    // Handle cases where departure_time might be null/undefined
    if (!route.departure_time) {
      return false;
    }

    const route24HrTime = convertTo24Hour(route.departure_time);

    // If route time conversion failed, exclude this route
    if (!route24HrTime) {
      return false;
    }

    return route24HrTime.startsWith(selected24HrTime.split(":")[0]);
  });

  return filteredRoutes;
}
// Toggle function to expand/collapse bus details and ensure only one open at a time
function toggleBusDetails(index) {
  const allDetails = document.querySelectorAll('[id^="bus-details-"]');
  allDetails.forEach((el, i) => {
    if (i === index) {
      const isCollapsed = el.classList.contains("max-h-0");
      if (isCollapsed) {
        el.classList.remove(
          "max-h-0",
          "opacity-0",
          "invisible",
          "pt-0",
          "pb-0",
          "overflow-hidden"
        );
        el.classList.add(
          "max-h-96",
          "opacity-100",
          "visible",
          "pt-4",
          "pb-4",
          "overflow-visible"
        );
      } else {
        el.classList.add(
          "max-h-0",
          "opacity-0",
          "invisible",
          "pt-0",
          "pb-0",
          "overflow-hidden"
        );
        el.classList.remove(
          "max-h-96",
          "opacity-100",
          "visible",
          "pt-4",
          "pb-4",
          "overflow-visible"
        );
      }
    } else {
      // Collapse others
      el.classList.add(
        "max-h-0",
        "opacity-0",
        "invisible",
        "pt-0",
        "pb-0",
        "overflow-hidden"
      );
      el.classList.remove(
        "max-h-96",
        "opacity-100",
        "visible",
        "pt-4",
        "pb-4",
        "overflow-visible"
      );
    }
  });
}

// Your main export function generating bus cards HTML
export function buildBusCards(routeData) {
  let html = `
    <div class="px-4 py-6 font-sans max-w-7xl mx-auto">
      <div class="search-container">
        <div class="results space-y-4">
          <div class="results-header hidden md:flex font-semibold text-gray-700 border-b-2 border-gray-300 pb-2 mb-3">
            <div class="w-3/4">Available Buses</div>
            <div class="w-1/4 text-center">Departure Time</div>
          </div>
  `;

  routeData.forEach((value, index) => {
    const busImage = value.bus.bus_image
      ? value.bus.bus_image.startsWith("http")
        ? value.bus.bus_image
        : new URL(value.bus.bus_image, location.origin).href
      : "/static/img/default-bus.png";

    html += `
      <div
        class="bus-card border border-gray-200 rounded-2xl shadow-sm hover:shadow-md transition-shadow duration-200 bg-white overflow-hidden cursor-pointer"
        onclick="toggleBusDetails(${index})"
      >
        <div class="md:flex justify-between items-center p-4 gap-4">
          <!-- Left: Bus Image and Basic Info -->
          <div class="flex items-center flex-1 gap-4">
            <img
              src="${busImage}"
              alt="Bus Image"
              class="w-20 h-16 rounded-lg object-cover shadow-md flex-shrink-0"
              loading="lazy"
              onerror="this.onerror=null;this.src='/static/img/default-bus.png';"
            />
            <div>
              <h3 class="text-lg font-bold text-gray-800 hover:underline cursor-pointer">${
                value.bus.name
              }</h3>
              <p class="text-sm text-gray-600">Route: ${
                value.route.route_name
              }</p>
            </div>
          </div>

          <!-- Right: Departure Time and Track Button -->
          <div class="mt-3 md:mt-0 md:w-1/4 text-center space-y-2">
            <span class="inline-block bg-green-600 text-white text-sm md:text-base font-semibold py-2 px-4 rounded-lg shadow">
              ${value.departure_time}
            </span>
            ${
              value.departure_time !== "Available"
                ? `
            <button onclick="openTrackModal('${value.bus.name}', '${value.route.route_name}')" class="inline-block bg-blue-600 text-white text-sm md:text-base font-semibold py-2 px-4 rounded-lg shadow">
              <div class="inline-flex items-center justify-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
                Track Bus
              </div>
            </button>
            `
                : ""
            }
          </div>
        </div>
    `;

    html +=
      value.departure_time === "Available"
        ? `
      <div
        id="bus-details-${index}"
        class="max-h-0 opacity-0 invisible overflow-hidden px-4 pt-0 pb-0 text-sm transition-all duration-300 ease-in-out"
      >
        <div class="backdrop-blur-md bg-white/50 shadow-md rounded-xl px-4 py-3 border border-gray-200">
          <p class="text-sm text-gray-800 font-semibold mb-1 tracking-wide">Login Required!</p>
          <p class="text-sm text-gray-700 leading-relaxed">
            Kindly
            <a
              href="#"
              onclick='document.getElementById("customModal").classList.remove("hidden");
                      const modalContent = document.getElementById("modalContent");
                      setTimeout(() => {
                        modalContent.classList.remove("scale-90", "opacity-0");
                        modalContent.classList.add("scale-100", "opacity-100");
                        studentIdInput.focus();
                      }, 10);
                      document.body.style.overflow = "hidden";'
              class="text-indigo-600 hover:underline font-medium"
            >log in</a>
            to view this bus's details.
          </p>
        </div>
      </div>
      `
        : `
      <div
        id="bus-details-${index}"
        class="max-h-0 opacity-0 invisible overflow-hidden px-4 pt-0 pb-0 text-sm text-gray-700 space-y-1 transition-all duration-300 ease-in-out"
      >
        <p>
          <span class="font-semibold text-blue-700">Capacity:</span>
          <span class="text-gray-800">${value.bus.capacity}</span>
        </p>
        <p>
          <span class="font-semibold text-green-700">Audience:</span>
          <span class="text-gray-800">${value.audience}</span>
        </p>
        <p>
          <span class="font-semibold text-purple-700">Driver:</span>
          <span class="text-gray-800">${value.driver.name}</span>
        </p>
        <p>
          <span class="font-semibold text-slate-700">Stoppages:</span>
          <span class="text-gray-800">${value.stoppage_names.join(", ")}</span>
        </p>
      </div>
      `;

    // Close card div
    html += `</div>`;
  });

  html += `
        </div> <!-- .results -->
      </div> <!-- .search-container -->
    </div> <!-- .container -->
  `;

  return html;
}

// Track Bus Modal Functionality
window.openTrackModal = function (busName, routeName) {
  const modal = document.createElement("div");
  modal.id = "trackBusModal";
  modal.className =
    "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50";

  modal.innerHTML = `
    <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl mx-4 overflow-hidden">
      <div class="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 flex justify-between items-center">
        <div>
          <h3 class="text-xl font-bold">Tracking ${busName}</h3>
          <p class="text-blue-100 text-sm">Route: ${routeName}</p>
        </div>
        <button onclick="closeTrackModal()" class="text-white hover:text-gray-200 text-2xl font-bold">&times;</button>
      </div>
      
      <div class="p-4">
        <div class="mb-3 p-3 border rounded-lg">
          <div class="flex items-center justify-between mb-2">
            <span class="text-gray-800 font-semibold">Status:</span>
            <span id="busStatus" class="px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
              <i class="fas fa-spinner fa-spin mr-2"></i>Checking...
            </span>
          </div>
          <div class="text-sm text-gray-700">
            <div class="grid grid-cols-2 gap-x-4 gap-y-1">
              <p><span class="font-medium">Current Location:</span> <span id="currentLocation">Detecting...</span></p>
              <p><span class="font-medium">Speed:</span> <span id="busSpeed">-- km/h</span></p>
              <p><span class="font-medium">Next Stop:</span> <span id="nextStop">Loading...</span></p>
              <p><span class="font-medium">ETA:</span> <span id="estimatedArrival">Calculating...</span></p>
            </div>
          </div>
          <div class="mt-2 flex items-center justify-between">
            <label class="flex items-center text-sm text-gray-700">
              <input type="checkbox" id="showPathToggle" checked class="mr-2 rounded">
              <span>Show route path</span>
            </label>
            <div class="text-xs text-gray-600">
              Last updated: <span id="lastUpdate">--</span>
            </div>
          </div>
        </div>
        
        <div class="mb-3">
          <h4 class="font-semibold text-gray-800 mb-2 flex items-center">
            <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0121 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m-6 3l6-3"/>
            </svg>
            Live Map View
          </h4>
          <div id="trackingMap" class="h-60 bg-gray-200 rounded-lg overflow-hidden">
            <div class="h-full flex items-center justify-center">
              <div class="text-center">
                <div class="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                <p class="text-gray-600">Loading Map...</p>
                <p class="text-xs text-gray-500 mt-1">Initializing Google Maps API</p>
              </div>
            </div>
        </div>
        
        <div class="mt-3 p-3 bg-blue-50 rounded-lg">
          <p class="text-sm text-blue-800 text-center">
            <i class="fas fa-satellite-dish mr-1"></i>
            Real GPS tracking updates every 5 seconds
          </p>
        </div>
      </div>
      
      <div class="bg-gray-50 px-4 py-3 flex justify-between items-center">
        <button onclick="refreshBusLocation('${busName}')" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition">
          <i class="fas fa-sync-alt mr-2"></i>Refresh
        </button>
        <button onclick="closeTrackModal()" class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition">
          Close Tracking
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
  document.body.style.overflow = "hidden";

  // Store bus name for tracking
  window.currentTrackingBus = busName;

  // Set up path toggle control
  setTimeout(() => {
    setupPathToggle();
  }, 100);

  // Initialize real GPS tracking
  setTimeout(() => {
    initializeRealBusTracking(busName);
  }, 100);
};

window.closeTrackModal = function () {
  const modal = document.getElementById("trackBusModal");
  if (modal) {
    modal.remove();
    document.body.style.overflow = "";
    // Stop real GPS tracking
    if (window.busTrackingInterval) {
      clearInterval(window.busTrackingInterval);
      window.busTrackingInterval = null;
    }
    // Reset tracking variables
    window.currentTrackingBus = null;
    if (window.busTrackingMap) {
      window.busTrackingMap = null;
    }
    if (window.busMarker) {
      window.busMarker = null;
    }
    if (window.startMarker) {
      window.startMarker = null;
    }
    if (window.busPathPolyline) {
      window.busPathPolyline = null;
    }
    // Reset path coordinates
    window.busPathCoordinates = [];
  }
};

// Real GPS tracking variables
window.busTrackingMap = null;
window.busMarker = null;
window.busTrackingInterval = null;
window.currentTrackingBus = null;
window.lastKnownPosition = null;
window.busPathPolyline = null;
window.busPathCoordinates = [];
window.startMarker = null;

// Initialize real bus tracking
function initializeRealBusTracking(busName) {
  // Set up map first
  initializeTrackingMapWithApiLoad();

  // Start fetching real GPS data immediately
  fetchBusLocation(busName);

  // Set up interval to fetch GPS data every 5 seconds
  if (window.busTrackingInterval) {
    clearInterval(window.busTrackingInterval);
  }

  window.busTrackingInterval = setInterval(() => {
    fetchBusLocation(busName);
  }, 5000);
}

// Function to fetch real bus location from API
async function fetchBusLocation(busName) {
  try {
    const response = await fetch(`/api/bus_location/${busName}/`);
    const result = await response.json();
    console.log(result);

    if (result.success && result.data) {
      const data = result.data;
      updateBusLocationOnMap(
        data.latitude,
        data.longitude,
        data.is_moving,
        data.last_updated
      );
      updateTrackingUI({
        status: "success",
        latitude: data.latitude,
        longitude: data.longitude,
        is_moving: data.is_moving,
        last_updated: data.last_updated,
        timestamp: data.timestamp,
      });
    } else {
      // No location data available
      updateTrackingUI({
        status: "error",
        message: "No location data available",
        is_moving: false,
      });
    }
  } catch (error) {
    console.error("Error fetching bus location:", error);
    updateTrackingUI({
      status: "error",
      message: "Error fetching location data",
      is_moving: false,
    });
  }
}

// Update bus location on map
function updateBusLocationOnMap(lat, lng, isMoving, lastUpdated) {
  if (window.busTrackingMap && window.googleMapsLoaded) {
    const position = { lat: parseFloat(lat), lng: parseFloat(lng) };

    // Create or update bus marker
    if (window.busMarker) {
      // Add current position to path before updating marker
      const currentPos = window.busMarker.getPosition();
      if (
        currentPos &&
        (currentPos.lat() !== position.lat || currentPos.lng() !== position.lng)
      ) {
        window.busPathCoordinates.push({
          lat: currentPos.lat(),
          lng: currentPos.lng(),
        });
        updatePolyline();
      }
      window.busMarker.setPosition(position);
    } else {
      // Create start marker for the first position
      window.startMarker = new google.maps.Marker({
        position: position,
        map: window.busTrackingMap,
        title: `Start: ${window.currentTrackingBus}`,
        icon: {
          url:
            "data:image/svg+xml;charset=UTF-8," +
            encodeURIComponent(`
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" fill="#10B981" stroke="white" stroke-width="2"/>
              <path d="M8 12l2 2 4-4" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          `),
          scaledSize: new google.maps.Size(24, 24),
          anchor: new google.maps.Point(12, 12),
        },
      });

      // Initialize path with starting position
      window.busPathCoordinates = [position];

      // Create the bus marker
      window.busMarker = new google.maps.Marker({
        position: position,
        map: window.busTrackingMap,
        title: `Bus: ${window.currentTrackingBus}`,
        icon: {
          url:
            "data:image/svg+xml;charset=UTF-8," +
            encodeURIComponent(`
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="16" cy="16" r="14" fill="${
                isMoving ? "#22C55E" : "#EF4444"
              }" stroke="white" stroke-width="2"/>
              <path d="M8 12h16v8H8v-8zm2 2v4h12v-4H10zm-2-4h16v2H8V10zm4 12h8v2h-8v-2z" fill="white"/>
            </svg>
          `),
          scaledSize: new google.maps.Size(32, 32),
          anchor: new google.maps.Point(16, 16),
        },
      });

      // Initialize polyline
      initializePolyline();
    }

    // Update marker icon color based on movement
    window.busMarker.setIcon({
      url:
        "data:image/svg+xml;charset=UTF-8," +
        encodeURIComponent(`
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="16" cy="16" r="14" fill="${
            isMoving ? "#22C55E" : "#EF4444"
          }" stroke="white" stroke-width="2"/>
          <path d="M8 12h16v8H8v-8zm2 2v4h12v-4H10zm-2-4h16v2H8V10zm4 12h8v2h-8v-2z" fill="white"/>
        </svg>
      `),
      scaledSize: new google.maps.Size(32, 32),
      anchor: new google.maps.Point(16, 16),
    });

    // Center map on bus location but don't zoom in too much if we have a path
    if (window.busPathCoordinates.length > 5) {
      // If we have a significant path, fit bounds to show the whole route
      const bounds = new google.maps.LatLngBounds();
      window.busPathCoordinates.forEach((coord) => bounds.extend(coord));
      bounds.extend(position);
      window.busTrackingMap.fitBounds(bounds, { padding: 50 });
    } else {
      // For shorter paths, just center on current position
      window.busTrackingMap.setCenter(position);
      window.busTrackingMap.setZoom(15);
    }
  }

  // Store last known position
  window.lastKnownPosition = { lat, lng, isMoving, lastUpdated };
}

// Initialize polyline for bus path tracking
function initializePolyline() {
  if (window.busTrackingMap && window.googleMapsLoaded) {
    window.busPathPolyline = new google.maps.Polyline({
      path: window.busPathCoordinates,
      geodesic: true,
      strokeColor: "#2563EB",
      strokeOpacity: 0.8,
      strokeWeight: 4,
      map: window.busTrackingMap,
    });
  }
}

// Update polyline with new coordinates
function updatePolyline() {
  if (window.busPathPolyline && window.busPathCoordinates.length > 0) {
    window.busPathPolyline.setPath(window.busPathCoordinates);
    updatePathStats();
  }
}

// Calculate and update path statistics
function updatePathStats() {
  // Path statistics are now handled internally for polyline updates
  // No need to display technical path information to users
  return;
}

// Calculate distance between two coordinates (Haversine formula)
function calculateDistance(pos1, pos2) {
  const R = 6371; // Radius of the Earth in kilometers
  const dLat = ((pos2.lat - pos1.lat) * Math.PI) / 180;
  const dLon = ((pos2.lng - pos1.lng) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((pos1.lat * Math.PI) / 180) *
      Math.cos((pos2.lat * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

// Clear bus path
window.clearBusPath = function () {
  if (window.busPathPolyline) {
    window.busPathPolyline.setPath([]);
  }
  window.busPathCoordinates = [];
  updatePathStats();
};

// Toggle path visibility
function setupPathToggle() {
  const toggle = document.getElementById("showPathToggle");
  if (toggle) {
    toggle.addEventListener("change", function () {
      if (window.busPathPolyline) {
        window.busPathPolyline.setVisible(this.checked);
      }
    });
  }
}

// Update tracking UI with status information
function updateTrackingUI(data) {
  const statusElement = document.getElementById("busStatus");
  const currentLocationElement = document.getElementById("currentLocation");
  const busSpeedElement = document.getElementById("busSpeed");
  const nextStopElement = document.getElementById("nextStop");
  const estimatedArrivalElement = document.getElementById("estimatedArrival");
  const lastUpdateElement = document.getElementById("lastUpdate");

  if (statusElement) {
    if (data.status === "success" && data.latitude && data.longitude) {
      statusElement.innerHTML = `
        <i class="fas fa-circle ${
          data.is_moving ? "text-green-500" : "text-red-500"
        } mr-2"></i>
        ${data.is_moving ? "Moving" : "Stationary"}
      `;
      statusElement.className = `px-3 py-1 rounded-full text-sm font-medium ${
        data.is_moving
          ? "bg-green-100 text-green-800"
          : "bg-red-100 text-red-800"
      }`;
    } else {
      statusElement.innerHTML = `
        <i class="fas fa-exclamation-triangle text-yellow-500 mr-2"></i>
        No GPS Data
      `;
      statusElement.className =
        "px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800";
    }
  }

  // Update current location with a more user-friendly description
  if (currentLocationElement && data.latitude && data.longitude) {
    // For now, show area coordinates, but this could be enhanced with reverse geocoding
    const lat = parseFloat(data.latitude);
    const lng = parseFloat(data.longitude);

    // Simple area detection based on coordinates (can be enhanced)
    let locationName = "On Route";
    if (lat >= 23.875 && lat <= 23.885 && lng >= 90.315 && lng <= 90.325) {
      locationName = "Near Daffodil Campus";
    } else if (lat >= 23.81 && lat <= 23.82 && lng >= 90.405 && lng <= 90.415) {
      locationName = "Dhaka City Center";
    } else if (lat >= 23.76 && lat <= 23.77 && lng >= 90.36 && lng <= 90.37) {
      locationName = "Motijheel Area";
    }

    currentLocationElement.textContent = locationName;
  } else if (currentLocationElement) {
    currentLocationElement.textContent = "Location unavailable";
  }

  // Calculate and display speed
  if (busSpeedElement) {
    if (
      data.is_moving &&
      window.lastKnownPosition &&
      data.latitude &&
      data.longitude
    ) {
      // Calculate speed based on distance and time difference
      const now = new Date();
      const lastUpdate = window.lastPositionTime || now;
      const timeDiff = (now - lastUpdate) / 1000; // seconds

      if (
        timeDiff > 0 &&
        window.lastKnownPosition.lat &&
        window.lastKnownPosition.lng
      ) {
        const distance = calculateDistance(
          {
            lat: parseFloat(window.lastKnownPosition.lat),
            lng: parseFloat(window.lastKnownPosition.lng),
          },
          { lat: parseFloat(data.latitude), lng: parseFloat(data.longitude) }
        );
        const speed = ((distance * 1000) / timeDiff) * 3.6; // Convert m/s to km/h

        if (speed > 0 && speed < 120) {
          // Reasonable speed range for a bus
          busSpeedElement.textContent = `${Math.round(speed)} km/h`;
        } else {
          busSpeedElement.textContent = data.is_moving ? "Moving" : "0 km/h";
        }
      } else {
        busSpeedElement.textContent = data.is_moving ? "Moving" : "0 km/h";
      }
    } else {
      busSpeedElement.textContent = data.is_moving ? "Starting..." : "0 km/h";
    }

    // Store current position and time for next calculation
    window.lastPositionTime = new Date();
  }

  // Update next stop (this would ideally come from route data)
  if (nextStopElement) {
    // This is a placeholder - in a real system, you'd calculate this based on route and current position
    if (data.is_moving) {
      nextStopElement.textContent = "Approaching next stop...";
    } else {
      nextStopElement.textContent = "At current stop";
    }
  }

  // Update estimated arrival (placeholder)
  if (estimatedArrivalElement) {
    if (data.is_moving) {
      const now = new Date();
      const eta = new Date(now.getTime() + (Math.random() * 10 + 5) * 60000); // Random 5-15 mins
      estimatedArrivalElement.textContent = eta.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });
    } else {
      estimatedArrivalElement.textContent = "Waiting at stop";
    }
  }

  // Update last update time
  if (lastUpdateElement) {
    if (data.timestamp) {
      const updateTime = new Date(data.timestamp);
      const now = new Date();
      const diffMinutes = Math.floor((now - updateTime) / 60000);

      if (diffMinutes < 1) {
        lastUpdateElement.textContent = "just now";
      } else if (diffMinutes < 60) {
        lastUpdateElement.textContent = `${diffMinutes}m ago`;
      } else {
        lastUpdateElement.textContent = updateTime.toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        });
      }
    } else if (data.last_updated) {
      lastUpdateElement.textContent = data.last_updated;
    } else {
      lastUpdateElement.textContent = "never";
    }
  }

  // Update demo coordinates if in demo mode
  const demoCoordinatesElement = document.getElementById("demoCoordinates");
  if (demoCoordinatesElement) {
    if (data.latitude && data.longitude) {
      demoCoordinatesElement.innerHTML = `
        <div class="flex justify-between items-center mb-1">
          <span class="text-xs text-gray-500">Lat:</span>
          <span class="font-medium">${parseFloat(data.latitude).toFixed(
            6
          )}</span>
        </div>
        <div class="flex justify-between items-center mb-1">
          <span class="text-xs text-gray-500">Lng:</span>
          <span class="font-medium">${parseFloat(data.longitude).toFixed(
            6
          )}</span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-xs text-gray-500">Status:</span>
          <span class="font-medium ${
            data.is_moving ? "text-green-600" : "text-red-600"
          }">
            ${data.is_moving ? "Moving" : "Stationary"}
          </span>
        </div>
      `;
    } else {
      demoCoordinatesElement.innerHTML = `
        <div class="text-center text-yellow-600">
          <i class="fas fa-exclamation-triangle mb-1"></i>
          <div>No GPS data available</div>
        </div>
      `;
    }
  }
}

// Refresh bus location manually
window.refreshBusLocation = function (busName) {
  if (busName && typeof fetchBusLocation === "function") {
    fetchBusLocation(busName);
  }
};

// Function to dynamically load Google Maps API if not already loaded
function initializeTrackingMapWithApiLoad() {
  // Check if Google Maps API is already loaded
  if (typeof google !== "undefined" && google.maps) {
    window.googleMapsLoaded = true;
    window.googleMapsApiLoaded = true;
    initializeTrackingMap();
    return;
  }

  // Check if API is already being loaded
  if (document.querySelector('script[src*="maps.googleapis.com"]')) {
    // Wait for it to load
    const checkGoogleMaps = setInterval(() => {
      if (typeof google !== "undefined" && google.maps) {
        clearInterval(checkGoogleMaps);
        window.googleMapsLoaded = true;
        window.googleMapsApiLoaded = true;
        initializeTrackingMap();
      }
    }, 100);

    // Timeout after 10 seconds
    setTimeout(() => {
      clearInterval(checkGoogleMaps);
      if (typeof google === "undefined" || !google.maps) {
        loadGoogleMapsScript();
      }
    }, 10000);
    return;
  }

  // Load Google Maps script dynamically
  loadGoogleMapsScript();
}

// Function to load Google Maps script from server
function loadGoogleMapsScript() {
  // Create script element to load Google Maps
  const script = document.createElement("script");
  script.src = "/load_google_maps.js"; // This will load our secure script
  script.async = true;
  script.defer = true;

  script.onload = function () {
    console.log("Google Maps loader script loaded");
    // Wait a bit for the actual Google Maps API to load
    setTimeout(() => {
      if (typeof google !== "undefined" && google.maps) {
        window.googleMapsLoaded = true;
        window.googleMapsApiLoaded = true;
        initializeTrackingMap();
      } else {
        // Still check periodically
        const checkGoogleMaps = setInterval(() => {
          if (typeof google !== "undefined" && google.maps) {
            clearInterval(checkGoogleMaps);
            window.googleMapsLoaded = true;
            window.googleMapsApiLoaded = true;
            initializeTrackingMap();
          }
        }, 500);

        // Final timeout
        setTimeout(() => {
          clearInterval(checkGoogleMaps);
          console.warn("Google Maps API failed to load - running in demo mode");
          initializeTrackingMap(); // Will show demo mode
        }, 15000);
      }
    }, 1000);
  };

  script.onerror = function () {
    console.warn("Failed to load Google Maps API - running in demo mode");
    initializeTrackingMap(); // Will show demo mode
  };

  document.head.appendChild(script);
}

function initializeTrackingMap() {
  // Initialize Google Map
  const mapContainer = document.getElementById("trackingMap");

  if (typeof google === "undefined" || !google.maps) {
    // If Google Maps is not loaded or API key invalid, show demo mode
    mapContainer.innerHTML = `
      <div class="h-full flex items-center justify-center bg-blue-50">
        <div class="text-center p-6">
          <svg class="w-12 h-12 text-blue-500 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0121 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m-6 3l6-3"/>
          </svg>
          <p class="text-blue-600 font-semibold">Demo Tracking Mode</p>
          <p class="text-sm text-gray-600 mb-4">Loading Google Maps API...</p>
          <div class="bg-white p-4 rounded-lg shadow-sm border">
            <p class="text-xs text-gray-500 mb-2 font-medium">Live GPS Coordinates:</p>
            <div id="demoCoordinates" class="text-sm font-mono text-gray-700 bg-gray-50 p-2 rounded"></div>
          </div>
          <div class="mt-4 text-xs text-gray-500">
            <p>🚌 Real-time GPS tracking (API loading...)</p>
          </div>
        </div>
      </div>
    `;

    // Try to load Google Maps API again after a delay
    setTimeout(() => {
      if (typeof google === "undefined" || !google.maps) {
        console.warn(
          "Google Maps API still not available - staying in demo mode"
        );
        mapContainer.innerHTML = mapContainer.innerHTML
          .replace(
            "Loading Google Maps API...",
            "Configure Google Maps API key for live map view"
          )
          .replace("API loading...", "API fallback mode");
      } else {
        // API became available, reinitialize
        initializeTrackingMap();
      }
    }, 3000);
    return;
  }

  // Initialize the map with default center (Dhaka, Bangladesh)
  const defaultCenter = { lat: 23.8103, lng: 90.4125 };

  window.busTrackingMap = new google.maps.Map(mapContainer, {
    zoom: 13,
    center: defaultCenter,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    styles: [
      {
        featureType: "poi",
        stylers: [{ visibility: "off" }],
      },
      {
        featureType: "transit",
        stylers: [{ visibility: "simplified" }],
      },
    ],
  });

  console.log("Google Maps initialized successfully for tracking");
}

// Real GPS tracking functions are now implemented above

export function renderNoRoutesFound(text) {
  const modalId = "noRoutesModal";
  let modal = document.getElementById(modalId);

  if (!modal) {
    modal = document.createElement("div");
    modal.id = modalId;
    Object.assign(modal.style, {
      position: "fixed",
      top: "0",
      left: "0",
      width: "100vw",
      height: "100vh",
      background: "rgba(0,0,0,0.6)", // Slightly darker overlay for focus
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: "9999",
      fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    });

    modal.innerHTML = `
      <div id="noRoutesModalContent" style="
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        padding: 36px 48px;
        max-width: 400px;
        width: 90%;
        text-align: center;
        position: relative;
        opacity: 0;
        transform: scale(0.9);
        transition: opacity 0.3s cubic-bezier(0.4,0,0.2,1), transform 0.3s cubic-bezier(0.4,0,0.2,1);
      ">
        <button id="closeNoRoutesModal" aria-label="Close modal" style="
          position: absolute;
          top: 16px;
          right: 16px;
          background: transparent;
          border: none;
          font-size: 1.6rem;
          color: #888;
          cursor: pointer;
          transition: color 0.2s ease;
        ">&times;</button>

        <svg
          width="64"
          height="64"
          fill="none"
          viewBox="0 0 64 64"
          aria-hidden="true"
          style="display: block; margin: 0 auto 24px auto;"
        >
          <circle cx="32" cy="32" r="32" fill="#ffe6e6"/>
          <path d="M20 44h24M32 20v16M32 36a2 2 0 100-4 2 2 0 000 4z" stroke="#e55353" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>


        <h2 style="margin: 0 0 12px 0; font-size: 1.75rem; font-weight: 700; color: #e55353;">
          ${text || "No Routes Found"}
        </h2>

        <p style="margin: 0 0 24px 0; font-size: 1.1rem; color: #555;">
          Sorry, we couldn't find any routes matching your criteria.<br>Try adjusting your search.
        </p>

        <button id="retrySearch" style="
          background-color: #e55353;
          border: none;
          color: white;
          padding: 12px 28px;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          box-shadow: 0 4px 12px rgba(229, 83, 83, 0.4);
          transition: background-color 0.3s ease;
        ">Retry Search</button>
      </div>
    `;

    document.body.appendChild(modal);

    // Animate in modal content
    setTimeout(() => {
      const content = document.getElementById("noRoutesModalContent");
      if (content) {
        content.style.opacity = "1";
        content.style.transform = "scale(1)";
      }
    }, 10);

    const closeBtn = document.getElementById("closeNoRoutesModal");
    closeBtn.onmouseover = () => (closeBtn.style.color = "#e55353");
    closeBtn.onmouseout = () => (closeBtn.style.color = "#888");
    closeBtn.onclick = () => {
      modal.style.display = "none";
    };

    modal.onclick = (e) => {
      if (e.target === modal) {
        modal.style.display = "none";
      }
    };

    // Retry button to close modal and maybe clear search input or refocus
    document.getElementById("retrySearch").onclick = () => {
      modal.style.display = "none";
      const searchInput = document.getElementById("place");
      if (searchInput) {
        searchInput.focus();
      }
    };
  } else {
    modal.style.display = "flex";
    const content = document.getElementById("noRoutesModalContent");
    if (content) {
      content.style.opacity = "0";
      content.style.transform = "scale(0.9)";
      setTimeout(() => {
        content.style.opacity = "1";
        content.style.transform = "scale(1)";
      }, 10);
    }
  }

  return "";
}

window.toggleBusDetails = function (index) {
  const details = document.getElementById(`bus-details-${index}`);
  if (!details) return;

  if (details.classList.contains("open")) {
    // Collapse: step 1 — fix height before collapsing
    details.style.maxHeight = details.scrollHeight + "px";

    // Force reflow to allow transition from scrollHeight to 0
    void details.offsetHeight;

    // Step 2 — collapse
    details.style.maxHeight = "0";
    details.style.paddingTop = "0";
    details.style.paddingBottom = "0";
    details.style.opacity = "0";
    details.style.visibility = "hidden";
    details.classList.remove("open");
  } else {
    // Expand
    details.style.maxHeight = details.scrollHeight + "px";
    details.style.paddingTop = "0.5rem";
    details.style.paddingBottom = "1rem";
    details.style.opacity = "1";
    details.style.visibility = "visible";
    details.classList.add("open");

    // Optional: cleanup after animation ends
    details.addEventListener("transitionend", function handler(e) {
      if (e.propertyName === "max-height") {
        details.style.maxHeight = "none"; // allows natural growth after animation
        details.removeEventListener("transitionend", handler);
      }
    });
  }
};
