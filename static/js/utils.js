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
// utils.js
export async function filterRoutesByTime(routes, selectedTime) {
  if (selectedTime === "all") {
    return routes; // No filtering needed
  }
  if (!routes || routes.length === 0) {
    return false; // No routes to filter
  }
  const filteredRoutes = routes.filter((route) => {
    const departureTime = new Date(`1970-01-01T${route.departure_time}:00`);
    const selectedDepartureTime = new Date(`1970-01-01T${selectedTime}:00`);
    return departureTime.getHours() === selectedDepartureTime.getHours();
  });

  return filteredRoutes;
}
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
    // Determine bus image URL with fallback
    const busImage = value.bus.bus_image
      ? value.bus.bus_image.startsWith("http")
        ? value.bus.bus_image
        : new URL(value.bus.bus_image, location.origin).href
      : "/static/img/default-bus.png"; // Change path to your default image

    html += `
    <div class="bus-card border border-gray-200 rounded-2xl shadow-sm hover:shadow-md transition-shadow duration-200 bg-white overflow-hidden cursor-pointer" onclick="toggleBusDetails(${index})">
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
            <h3 class="text-lg font-bold text-gray-800 hover:underline cursor-pointer">
              ${value.bus.name}
            </h3>
            <p class="text-sm text-gray-600">Route: ${
              value.route.route_name
            }</p>
          </div>
        </div>

        <!-- Right: Departure Time -->
        <div class="mt-3 md:mt-0 md:w-1/4 text-center">
          <span class="inline-block bg-green-600 text-white text-sm md:text-base font-semibold py-2 px-4 rounded-lg shadow">
            ${value.departure_time}
          </span>
        </div>
      </div>

      <!-- Hidden Details with transition -->
      <div
        id="bus-details-${index}"
        class="max-h-0 overflow-hidden px-4 pt-0 pb-0 text-sm text-gray-700 space-y-1 transition-all duration-300 ease-in-out opacity-0 invisible"
        style="max-height: 0; padding-top: 0; padding-bottom: 0; opacity: 0; transition: max-height 0.3s ease, padding 0.3s ease, opacity 0.3s ease; visibility: hidden;"
      >
        <p><span class="font-semibold">Capacity:</span> ${
          value.bus.capacity
        }</p>
        <p><span class="font-semibold">Audience:</span> ${value.audience}</p>
        <p><span class="font-semibold">Driver:</span> ${value.driver.name}</p>
        <p><span class="font-semibold">Phone:</span> ${
          value.driver.phone_number
        }</p>
        <p><span class="font-semibold">Stoppages:</span> ${value.stoppage_names.join(
          ", "
        )}</p>
      </div>
    </div>
    `;
  });

  html += `
      </div> <!-- .results -->
    </div> <!-- .search-container -->
  </div> <!-- .container -->
  `;

  return html;
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
