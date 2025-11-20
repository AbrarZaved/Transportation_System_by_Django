// import CSRF-safe fetch utility
import { csrfFetch } from "./api.js";
import { showToast } from "./utils.js";

// Cache keys for localStorage
const CACHE_KEYS = {
  FROM_DSC_ROUTES: "from_dsc_routes_cache",
  TO_DSC_ROUTES: "to_dsc_routes_cache",
};

// Utility: Clear route cache from localStorage
function clearRouteCache() {
  localStorage.removeItem(CACHE_KEYS.FROM_DSC_ROUTES);
  localStorage.removeItem(CACHE_KEYS.TO_DSC_ROUTES);
  console.log("Route cache cleared");
}

// Utility: Get routes from cache or fetch from backend
async function getRoutesForDirection(direction) {
  const cacheKey =
    direction === "from_dsc"
      ? CACHE_KEYS.FROM_DSC_ROUTES
      : CACHE_KEYS.TO_DSC_ROUTES;

  // Try to get from localStorage first
  const cachedRoutes = localStorage.getItem(cacheKey);
  if (cachedRoutes) {
    console.log(`Using cached routes for ${direction}`);
    return JSON.parse(cachedRoutes);
  }

  // If no cache, check if routeData from template is available
  if (typeof window.routeData !== "undefined" && window.routeData[direction]) {
    const routes = window.routeData[direction];
    // Store in cache for future use
    localStorage.setItem(cacheKey, JSON.stringify(routes));
    console.log(`Cached routes for ${direction} from template data`);
    return routes;
  }

  // Fallback: fetch from backend (should not happen with current implementation)
  console.log(`Fetching routes for ${direction} from backend`);
  try {
    const response = await csrfFetch(`${location.origin}/filter_route/`, {
      method: "POST",
      body: JSON.stringify({ direction }),
    });

    if (!response || !Array.isArray(response.routes)) {
      throw new Error("Invalid route response structure.");
    }

    const routes =
      response.routes.length > 0
        ? response.routes
        : [{ id: 0, name: "No routes available" }];

    // Cache the fetched routes
    localStorage.setItem(cacheKey, JSON.stringify(routes));
    return routes;
  } catch (err) {
    console.error("Failed to fetch routes:", err);
    return [{ id: 0, name: "Failed to load routes" }];
  }
}

// Utility: Render route radio buttons
function renderRouteOptions(routes) {
  const routeList = document.getElementById("route-list");
  routeList.innerHTML = "";

  if (routes.length === 0) {
    const noRoutesLabel = document.createElement("div");
    noRoutesLabel.className = "p-3 text-gray-500 text-center text-sm";
    noRoutesLabel.textContent = "No routes available for this direction";
    routeList.appendChild(noRoutesLabel);
    return;
  }

  routes.forEach((route) => {
    const label = document.createElement("label");
    label.className =
      "flex items-center p-2 bg-gray-50 rounded border hover:bg-indigo-50 cursor-pointer text-sm";

    const input = document.createElement("input");
    input.type = "radio";
    input.name = "route";
    input.value = route.id;
    input.required = true;
    input.className = "mr-2";

    const span = document.createElement("span");
    span.textContent = route.name;
    span.className = "text-gray-700 font-medium";

    label.appendChild(input);
    label.appendChild(span);
    routeList.appendChild(label);
  });
}

// Initialize logic when DOM is ready
document.addEventListener("DOMContentLoaded", async () => {
  // Make routeData available globally from the template
  if (typeof routeData !== "undefined") {
    window.routeData = routeData;
  }

  const directionRadios = document.getElementsByName("direction");
  const storedDirection = localStorage.getItem("direction") || "from_dsc";
  const messages = document.getElementById("messages");

  if (messages) {
    showToast(
      messages.dataset.message,
      messages.dataset.messageUsername || null
    );
  }

  // Set the previously selected direction if it exists
  const selectedRadio = document.querySelector(
    `input[name="direction"][value="${storedDirection}"]`
  );
  if (selectedRadio) selectedRadio.checked = true;

  // Initial render of routes using cached or fresh data
  const initialRoutes = await getRoutesForDirection(storedDirection);
  renderRouteOptions(initialRoutes);

  // Event listeners for changing direction - now using cached data
  directionRadios.forEach((radio) => {
    radio.addEventListener("change", async (e) => {
      const direction = e.target.value;
      localStorage.setItem("direction", direction);

      // Use cached routes or fetch if not available
      const routes = await getRoutesForDirection(direction);
      renderRouteOptions(routes);
    });
  });

  // Form validation
  document.querySelector("form").addEventListener("submit", function (e) {
    const selectedTimes = document.querySelectorAll(
      'input[name="times"]:checked'
    );
    if (selectedTimes.length === 0) {
      e.preventDefault();
      alert("Please select at least one time slot.");
      return false;
    }
    if (selectedTimes.length > 3) {
      e.preventDefault();
      alert("You can select maximum 3 time slots.");
      return false;
    }
  });

  // Clear cache when page is unloaded or refreshed
  window.addEventListener("beforeunload", () => {
    clearRouteCache();
  });

  // Clear cache when navigating away from the page
  window.addEventListener("pagehide", () => {
    clearRouteCache();
  });
});

// Filter items function for search inputs
function filterItems(inputEl, containerId) {
  const filter = inputEl.value.toLowerCase();
  const items = document.querySelectorAll(`#${containerId} label`);
  items.forEach((label) => {
    const text = label.innerText.toLowerCase();
    label.style.display = text.includes(filter) ? "flex" : "none";
  });
}

// Add custom time function
function addCustomTime() {
  const customTimeInput = document.getElementById("custom-time");
  const timeValue = customTimeInput.value;

  if (!timeValue) {
    alert("Please select a time first.");
    return;
  }

  // Convert 24-hour format to 12-hour format
  const [hours, minutes] = timeValue.split(":");
  const hour12 = parseInt(hours) % 12 || 12;
  const ampm = parseInt(hours) >= 12 ? "PM" : "AM";
  const formattedTime = `${hour12}:${minutes} ${ampm}`;

  // Check if time already exists
  const existingTimes = Array.from(
    document.querySelectorAll('input[name="times"]')
  ).map((input) => input.value);

  if (existingTimes.includes(formattedTime)) {
    alert("This time already exists in the list.");
    return;
  }

  // Create new time option
  const timeList = document.getElementById("time-list");
  const newTimeLabel = document.createElement("label");
  newTimeLabel.className =
    "flex items-center p-2 bg-green-50 rounded border hover:bg-indigo-50 cursor-pointer text-sm custom-time";
  newTimeLabel.innerHTML = `
    <input
      type="checkbox"
      name="times"
      value="${formattedTime}"
      class="mr-2 accent-indigo-600"
      onchange="limitTimeSelection(this)"
    />
    <span class="text-gray-700 font-medium">${formattedTime}</span>
    <button type="button" onclick="removeCustomTime(this)" class="ml-auto text-red-500 text-xs hover:text-red-700">Remove</button>
  `;

  // Insert at the beginning of the list
  timeList.insertBefore(newTimeLabel, timeList.firstChild);

  // Clear the input
  customTimeInput.value = "";

  // Check the newly added time
  const checkbox = newTimeLabel.querySelector('input[type="checkbox"]');
  checkbox.checked = true;
  limitTimeSelection(checkbox);
}

// Remove custom time function
function removeCustomTime(button) {
  const label = button.closest("label");
  const checkbox = label.querySelector('input[type="checkbox"]');

  // If it was checked, update the time selection limit
  if (checkbox.checked) {
    checkbox.checked = false;
    limitTimeSelection(checkbox);
  }

  label.remove();
}

// Limit time selection to maximum 3
function limitTimeSelection(checkbox) {
  const checkedTimes = document.querySelectorAll('input[name="times"]:checked');
  const allTimeCheckboxes = document.querySelectorAll('input[name="times"]');

  if (checkedTimes.length >= 3) {
    // Disable unchecked checkboxes
    allTimeCheckboxes.forEach((cb) => {
      if (!cb.checked) {
        cb.disabled = true;
        cb.parentElement.style.opacity = "0.5";
      }
    });
  } else {
    // Enable all checkboxes
    allTimeCheckboxes.forEach((cb) => {
      cb.disabled = false;
      cb.parentElement.style.opacity = "1";
    });
  }
}

// Make functions globally available for onclick handlers
window.filterItems = filterItems;
window.addCustomTime = addCustomTime;
window.removeCustomTime = removeCustomTime;
window.limitTimeSelection = limitTimeSelection;
