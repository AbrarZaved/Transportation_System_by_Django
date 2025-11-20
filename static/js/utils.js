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

  const [time, modifier] = timeStr.split(" ");

  // Additional validation
  if (!time || !modifier) {
    return null;
  }

  let [hours, minutes] = time.split(":").map(Number);

  // Validate hours and minutes
  if (isNaN(hours) || isNaN(minutes)) {
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
              <h3 class="text-lg font-bold text-gray-800 hover:underline cursor-pointer">${value.bus.name}</h3>
              <p class="text-sm text-gray-600">Route: ${value.route.route_name}</p>
            </div>
          </div>

          <!-- Right: Departure Time and Track Button -->
          <div class="mt-3 md:mt-0 md:w-1/4 text-center space-y-2">
            <span class="inline-block bg-green-600 text-white text-sm md:text-base font-semibold py-2 px-4 rounded-lg shadow">
              ${value.departure_time}
            </span>
            <button onclick="openTrackModal('${value.bus.name}', '${value.route.route_name}')" class="inline-block bg-blue-600 text-white text-sm md:text-base font-semibold py-2 px-4 rounded-lg shadow">
              <div class="inline-flex items-center justify-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
                Track Bus
              </div>
            </button>
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
      
      <div class="p-6">
        <div class="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div class="flex items-center gap-2 mb-2">
            <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <span class="text-green-800 font-semibold">Bus is currently moving</span>
          </div>
          <div class="text-sm text-gray-700 space-y-1">
            <p><span class="font-medium">Current Location:</span> <span id="currentLocation">Loading...</span></p>
            <p><span class="font-medium">Latitude:</span> <span id="currentLat">0.000000</span></p>
            <p><span class="font-medium">Longitude:</span> <span id="currentLng">0.000000</span></p>
            <p><span class="font-medium">Speed:</span> <span id="currentSpeed">0</span> km/h</p>
            <p><span class="font-medium">Last Updated:</span> <span id="lastUpdated">--</span></p>
          </div>
        </div>
        
        <div class="mb-4">
          <h4 class="font-semibold text-gray-800 mb-2 flex items-center">
            <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0121 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m-6 3l6-3"/>
            </svg>
            Live Map View
          </h4>
          <div id="trackingMap" class="h-64 bg-gray-200 rounded-lg overflow-hidden">
            <div class="h-full flex items-center justify-center">
              <div class="text-center">
                <div class="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                <p class="text-gray-600">Loading Map...</p>
                <p class="text-xs text-gray-500 mt-1">Initializing Google Maps API</p>
              </div>
            </div>
          </div>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-blue-50 p-3 rounded-lg text-center">
            <p class="text-2xl font-bold text-blue-600" id="etaMinutes">--</p>
            <p class="text-sm text-gray-600">ETA (minutes)</p>
          </div>
          <div class="bg-green-50 p-3 rounded-lg text-center">
            <p class="text-2xl font-bold text-green-600" id="distanceKm">--</p>
            <p class="text-sm text-gray-600">Distance (km)</p>
          </div>
        </div>
      </div>
      
      <div class="bg-gray-50 px-6 py-3 flex justify-end">
        <button onclick="closeTrackModal()" class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition">
          Close Tracking
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
  document.body.style.overflow = "hidden";

  // Initialize map with dynamic API loading
  setTimeout(() => {
    initializeTrackingMapWithApiLoad();
  }, 100);
};

window.closeTrackModal = function () {
  const modal = document.getElementById("trackBusModal");
  if (modal) {
    modal.remove();
    document.body.style.overflow = "";
    // Stop tracking
    if (window.trackingInterval) {
      clearInterval(window.trackingInterval);
      window.trackingInterval = null;
    }
    // Reset tracking variables
    trackingMap = null;
    busMarker = null;
    currentIndex = 0;
    progress = 0;
  }
};

// Demo route coordinates (simulating a bus route in Dhaka with more realistic stops)
const demoRoute = [
  {
    lat: 23.8103,
    lng: 90.4125,
    location: "Daffodil Smart City",
    isOrigin: true,
  },
  { lat: 23.815, lng: 90.42, location: "Kalabagan", estimatedTime: "2 min" },
  { lat: 23.82, lng: 90.425, location: "Green Road", estimatedTime: "5 min" },
  { lat: 23.825, lng: 90.43, location: "Panthapath", estimatedTime: "8 min" },
  {
    lat: 23.83,
    lng: 90.435,
    location: "Karwan Bazar",
    estimatedTime: "12 min",
  },
  { lat: 23.835, lng: 90.44, location: "Tejgaon", estimatedTime: "15 min" },
  { lat: 23.84, lng: 90.445, location: "Farmgate", estimatedTime: "18 min" },
  {
    lat: 23.845,
    lng: 90.45,
    location: "Bijoy Sarani",
    estimatedTime: "22 min",
    isDestination: true,
  },
];

let trackingMap = null;
let busMarker = null;
let currentIndex = 0;
let progress = 0;

// Function to dynamically load Google Maps API if not already loaded
function initializeTrackingMapWithApiLoad() {
  // Check if Google Maps API is already loaded
  if (typeof google !== "undefined" && window.googleMapsLoaded) {
    initializeTrackingMap();
    return;
  }

  // Check if API is already being loaded
  if (document.querySelector('script[src*="maps.googleapis.com"]')) {
    // Wait for it to load
    const checkGoogleMaps = setInterval(() => {
      if (typeof google !== "undefined" && window.googleMapsLoaded) {
        clearInterval(checkGoogleMaps);
        initializeTrackingMap();
      }
    }, 100);

    // Timeout after 10 seconds
    setTimeout(() => {
      clearInterval(checkGoogleMaps);
      if (typeof google === "undefined" || !window.googleMapsLoaded) {
        initializeTrackingMap(); // Will show demo mode
      }
    }, 10000);
    return;
  }

  // Get the API key from a meta tag or use a default (you'll need to set this)
  let apiKey = "";
  const metaApiKey = document.querySelector('meta[name="google-maps-api-key"]');
  if (metaApiKey) {
    apiKey = metaApiKey.getAttribute("content");
  }

  // If no API key found, show demo mode
  if (!apiKey) {
    console.warn("Google Maps API key not found, running in demo mode");
    initializeTrackingMap(); // Will show demo mode
    return;
  }

  // Set up global callbacks for API loading
  window.initGoogleMapsTracking = function () {
    window.googleMapsLoaded = true;
    console.log("Google Maps API loaded successfully for tracking");
    initializeTrackingMap();
  };

  window.gm_authFailure = function () {
    console.warn(
      "Google Maps API authentication failed - running in demo mode"
    );
    window.googleMapsLoaded = false;
    initializeTrackingMap(); // Will show demo mode
  };

  // Dynamically load Google Maps API
  const script = document.createElement("script");
  script.async = true;
  script.defer = true;
  script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=marker&callback=initGoogleMapsTracking&loading=async`;
  script.onerror = function () {
    console.warn("Google Maps API failed to load - running in demo mode");
    window.googleMapsLoaded = false;
    initializeTrackingMap(); // Will show demo mode
  };

  document.head.appendChild(script);
}

function initializeTrackingMap() {
  // Initialize Google Map
  const mapContainer = document.getElementById("trackingMap");

  if (typeof google === "undefined" || !window.googleMapsLoaded) {
    // If Google Maps is not loaded or API key invalid, show demo mode
    mapContainer.innerHTML = `
      <div class="h-full flex items-center justify-center bg-blue-50">
        <div class="text-center p-6">
          <svg class="w-12 h-12 text-blue-500 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0121 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m-6 3l6-3"/>
          </svg>
          <p class="text-blue-600 font-semibold">Demo Tracking Mode</p>
          <p class="text-sm text-gray-600 mb-4">Configure Google Maps API key for live map view</p>
          <div class="bg-white p-4 rounded-lg shadow-sm border">
            <p class="text-xs text-gray-500 mb-2 font-medium">Live GPS Coordinates:</p>
            <div id="demoCoordinates" class="text-sm font-mono text-gray-700 bg-gray-50 p-2 rounded"></div>
          </div>
          <div class="mt-4 text-xs text-gray-500">
            <p>🚌 Simulating real-time bus movement</p>
          </div>
        </div>
      </div>
    `;
    // Start the demo tracking without map
    startDemoTracking();
    return;
  }

  // Initialize the map centered on first route point
  trackingMap = new google.maps.Map(mapContainer, {
    zoom: 13,
    center: demoRoute[0],
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

  // Create custom bus marker with enhanced styling
  busMarker = new google.maps.Marker({
    position: demoRoute[0],
    map: trackingMap,
    title: "Bus Location",
    icon: {
      path: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z",
      scale: 1.5,
      fillColor: "#1e40af",
      fillOpacity: 1,
      strokeColor: "#ffffff",
      strokeWeight: 2,
      anchor: new google.maps.Point(12, 24),
    },
    zIndex: 1000,
  });

  // Draw the route path with enhanced styling
  const routePath = new google.maps.Polyline({
    path: demoRoute,
    geodesic: true,
    strokeColor: "#3b82f6",
    strokeOpacity: 0.8,
    strokeWeight: 6,
  });
  routePath.setMap(trackingMap);

  // Add enhanced markers for each stop
  demoRoute.forEach((stop, index) => {
    const isOrigin = stop.isOrigin;
    const isDestination = stop.isDestination;

    const marker = new google.maps.Marker({
      position: stop,
      map: trackingMap,
      title:
        stop.location +
        (stop.estimatedTime ? ` (ETA: ${stop.estimatedTime})` : ""),
      icon: {
        path: google.maps.SymbolPath.CIRCLE,
        scale: isOrigin || isDestination ? 8 : 6,
        fillColor: isOrigin ? "#10b981" : isDestination ? "#ef4444" : "#6b7280",
        fillOpacity: 0.9,
        strokeColor: "#ffffff",
        strokeWeight: 2,
      },
    });

    // Add info windows for stops
    const infoWindow = new google.maps.InfoWindow({
      content: `
        <div class="p-2">
          <h3 class="font-semibold text-gray-800">${stop.location}</h3>
          ${
            stop.estimatedTime
              ? `<p class="text-sm text-gray-600">ETA: ${stop.estimatedTime}</p>`
              : ""
          }
          ${
            isOrigin
              ? '<p class="text-xs text-green-600">Starting Point</p>'
              : ""
          }
          ${
            isDestination
              ? '<p class="text-xs text-red-600">Final Destination</p>'
              : ""
          }
        </div>
      `,
    });

    marker.addListener("click", () => {
      infoWindow.open(trackingMap, marker);
    });
  });

  // Start the tracking animation
  startDemoTracking();
}

function startDemoTracking() {
  let startTime = Date.now();

  window.trackingInterval = setInterval(() => {
    const current = demoRoute[currentIndex];
    const next = demoRoute[(currentIndex + 1) % demoRoute.length];

    // Interpolate between current and next point
    const lat = current.lat + (next.lat - current.lat) * progress;
    const lng = current.lng + (next.lng - current.lng) * progress;

    // Calculate more realistic speed and timing
    const elapsedMinutes = (Date.now() - startTime) / 60000;
    const currentSpeed =
      15 + Math.sin(elapsedMinutes * 0.5) * 10 + Math.random() * 8; // Variable speed 15-33 km/h
    const remainingStops = demoRoute.length - currentIndex - 1;
    const estimatedETA = remainingStops * 2.5 + (1 - progress) * 2.5; // ~2.5 min per stop
    const totalDistance = 8.5 - (currentIndex + progress) * 1.1; // Decreasing distance

    // Update UI elements
    const latElement = document.getElementById("currentLat");
    const lngElement = document.getElementById("currentLng");
    const locationElement = document.getElementById("currentLocation");
    const speedElement = document.getElementById("currentSpeed");
    const lastUpdatedElement = document.getElementById("lastUpdated");
    const etaElement = document.getElementById("etaMinutes");
    const distanceElement = document.getElementById("distanceKm");

    if (latElement) latElement.textContent = lat.toFixed(6);
    if (lngElement) lngElement.textContent = lng.toFixed(6);
    if (locationElement) {
      const locationText =
        progress > 0.7
          ? `Approaching ${next.location}`
          : `At ${current.location}`;
      locationElement.textContent = locationText;
    }
    if (speedElement) speedElement.textContent = currentSpeed.toFixed(1);
    if (lastUpdatedElement)
      lastUpdatedElement.textContent = new Date().toLocaleTimeString();
    if (etaElement)
      etaElement.textContent = Math.max(0, estimatedETA).toFixed(0);
    if (distanceElement)
      distanceElement.textContent = Math.max(0, totalDistance).toFixed(1);

    // Update demo coordinates display for non-map mode
    const demoCoordinatesElement = document.getElementById("demoCoordinates");
    if (demoCoordinatesElement) {
      const nextStopInfo = next.estimatedTime
        ? ` (ETA: ${next.estimatedTime})`
        : "";
      demoCoordinatesElement.innerHTML = `
        <div class="space-y-1">
          <div><span class="text-blue-600">Lat:</span> ${lat.toFixed(6)}</div>
          <div><span class="text-blue-600">Lng:</span> ${lng.toFixed(6)}</div>
          <div><span class="text-green-600">Current:</span> ${
            current.location
          }</div>
          <div><span class="text-purple-600">Next Stop:</span> ${
            next.location
          }${nextStopInfo}</div>
          <div><span class="text-orange-600">Speed:</span> ${currentSpeed.toFixed(
            1
          )} km/h</div>
          <div><span class="text-indigo-600">ETA:</span> ${Math.max(
            0,
            estimatedETA
          ).toFixed(0)} min</div>
          <div class="text-xs text-gray-500">Updated: ${new Date().toLocaleTimeString()}</div>
        </div>
      `;
    }

    // Update marker position on map if available
    if (busMarker) {
      const newPosition = { lat, lng };
      busMarker.setPosition(newPosition);

      // Smooth pan to bus location
      if (trackingMap) {
        trackingMap.panTo(newPosition);
      }

      // Update marker title with current info
      busMarker.setTitle(
        `Bus Location - Speed: ${currentSpeed.toFixed(
          1
        )} km/h - ETA: ${Math.max(0, estimatedETA).toFixed(0)} min`
      );
    }

    // Update progress with variable speed
    const progressIncrement = 0.08 + Math.random() * 0.04; // Variable progress 0.08-0.12
    progress += progressIncrement;

    if (progress >= 1) {
      progress = 0;
      currentIndex = (currentIndex + 1) % demoRoute.length;

      // Reset start time when completing full route
      if (currentIndex === 0) {
        startTime = Date.now();
      }
    }
  }, 2500); // Update every 2.5 seconds for more realistic tracking
}

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
