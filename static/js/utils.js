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
  return `<p>No routes found matching your criteria.</p>`;
}
