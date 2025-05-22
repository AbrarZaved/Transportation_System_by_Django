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

export function formatTime(timeString) {
  const date = new Date(timeString);
  const options = { hour: "numeric", minute: "numeric", hour12: true };
  return date.toLocaleString("en-US", options);
}

export function buildBusCards(routeData) {
  let html = `
  <div class="container" style="padding: 20px; font-family: Arial, sans-serif;">
    <div class="search-container">
      <div class="results">
        <div class="results-header" style="display: flex; font-weight: bold; border-bottom: 2px solid #ccc; padding-bottom: 8px; margin-bottom: 12px;">
          <div class="column service-provider" style="flex: 3;">Available Buses</div>
          <div class="column dep-time" style="flex: 1;">Dep Time</div>
        </div>
`;

  routeData.forEach((value, index) => {
    const formattedDeparture = formatTime(value.departure_time);
    html += `
    <div class="bus-card"
         style="cursor: pointer; display: flex; justify-content: space-between; align-items: center; padding: 15px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 10px; background: #f9f9f9; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); transition: transform 0.2s;">
      <div class="bus-info" style="flex: 3;">
        <h3 style="margin: 0 0 5px 0;" onclick="showBusModal(${index})">${
      value.bus.name
    }</h3>
        <p class="bus-type" style="margin: 0 0 5px 0;">Capacity: ${
          value.bus.capacity
        }</p>
        <div class="route-info" style="font-size: 14px; color: #555;">
          <p><strong>Route:</strong> ${value.route.route_name}</p>
          <p><strong>Audience:</strong> ${value.audience}</p>
          <p><strong>Driver:</strong> ${value.driver.name}</p>
          <p><strong>Stoppages:</strong> ${value.stoppage_names.join(", ")}</p>
        </div>
      </div>
      <div class="departure" style="
        flex: 1;
        text-align: center;
        font-weight: bold;
        color: #ffffff;
        background-color: #28a745;
        padding: 10px 15px;
        border-radius: 8px;
        font-size: 16px;
        box-shadow: 0 0 5px rgba(0,0,0,0.1);
      ">
        ${formattedDeparture}
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

export function setupModalHandlers(routeData) {
  window.showBusModal = function (index) {
    const item = routeData[index];
    document.getElementById("modalBusName").innerText = item.bus.name;
    document.getElementById("modalBusImage").src = item.bus.bus_image;
    document.getElementById("modalDriverName").innerText = item.driver.name;
    document.getElementById("modalDriverPhone").innerText =
      item.driver.phone_number || "Not Available";
    document.getElementById("busModal").style.display = "block";
  };

  document.querySelector(".close-btn").onclick = () => {
    document.getElementById("busModal").style.display = "none";
  };

  window.onclick = (event) => {
    const modal = document.getElementById("busModal");
    if (event.target === modal) {
      modal.style.display = "none";
    }
  };
}

export function renderNoRoutesFound() {
  // Show a modal popup with the "No Routes Found" message
  const modalId = "noRoutesModal";
  let modal = document.getElementById(modalId);

  if (!modal) {
    modal = document.createElement("div");
    modal.id = modalId;
    modal.style.position = "fixed";
    modal.style.top = "0";
    modal.style.left = "0";
    modal.style.width = "100vw";
    modal.style.height = "100vh";
    modal.style.background = "rgba(0,0,0,0.4)";
    modal.style.display = "flex";
    modal.style.alignItems = "center";
    modal.style.justifyContent = "center";
    modal.style.zIndex = "9999";

    // Add a wrapper for animation
    modal.innerHTML = `
      <div id="noRoutesModalContent" style="
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.15);
        padding: 40px 32px;
        text-align: center;
        min-width: 320px;
        position: relative;
        opacity: 0;
        transform: scale(0.9);
        transition: opacity 0.3s cubic-bezier(0.4,0,0.2,1), transform 0.3s cubic-bezier(0.4,0,0.2,1);
      ">
        <button id="closeNoRoutesModal" style="
          position: absolute;
          top: 12px;
          right: 12px;
          background: transparent;
          border: none;
          font-size: 1.5em;
          color: #aaa;
          cursor: pointer;
        ">&times;</button>
        <svg width="64" height="64" fill="none" viewBox="0 0 64 64">
          <circle cx="32" cy="32" r="32" fill="#f2f2f2"/>
          <path d="M20 44h24M32 20v16M32 36a2 2 0 100-4 2 2 0 000 4z" stroke="#bbb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <h2 style="margin: 20px 0 10px 0; font-size: 1.5em; color: #888;">No Routes Found</h2>
        <p style="font-size: 1em; color: #888;">Sorry, we couldn't find any routes matching your criteria.<br>Try adjusting your search.</p>
      </div>
    `;
    document.body.appendChild(modal);

    // Animate in after appending
    setTimeout(() => {
      const content = document.getElementById("noRoutesModalContent");
      if (content) {
        content.style.opacity = "1";
        content.style.transform = "scale(1)";
      }
    }, 10);

    document.getElementById("closeNoRoutesModal").onclick = () => {
      modal.style.display = "none";
    };

    modal.onclick = (e) => {
      if (e.target === modal) {
        modal.style.display = "none";
      }
    };
  } else {
    modal.style.display = "flex";
    // Animate in again if needed
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
