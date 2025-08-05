// import CSRF-safe fetch utility
import { csrfFetch } from "./api.js";

// Utility: Render route radio buttons
async function renderRouteOptions(routes) {
  const routeList = document.getElementById("route-list");
  routeList.innerHTML = "";

  routes.forEach((route) => {
    const label = document.createElement("label");
    label.className =
      "flex items-center p-3 bg-gray-50 rounded border hover:bg-indigo-50 cursor-pointer text-base";

    const input = document.createElement("input");
    input.type = "radio";
    input.name = "route";
    input.value = route.id;
    input.required = true;
    input.className = "mr-3";

    const span = document.createElement("span");
    span.textContent = route.name;
    span.className = "text-gray-700 font-medium";

    label.appendChild(input);
    label.appendChild(span);
    routeList.appendChild(label);
  });
}

// Utility: Fetch routes by direction (to_dsc or from_dsc)
async function fetchRoutesByDirection(direction) {
  try {
    const response = await csrfFetch(`${location.origin}/filter_route/`, {
      method: "POST",
      body: JSON.stringify({ direction }),
    });

    if (!response || !Array.isArray(response.routes)) {
      throw new Error("Invalid route response structure.");
    }

    return response.routes.length > 0
      ? response.routes
      : [{ id: 0, name: "No routes available" }];
  } catch (err) {
    console.error("Failed to fetch routes:", err);
    return [{ id: 0, name: "Failed to load routes" }];
  }
}

// Initialize logic when DOM is ready
document.addEventListener("DOMContentLoaded", async () => {
  const directionRadios = document.getElementsByName("direction");
  const storedDirection = localStorage.getItem("direction") || "from_dsc";

  // Set the previously selected direction if it exists
  const selectedRadio = document.querySelector(
    `input[name="direction"][value="${storedDirection}"]`
  );
  if (selectedRadio) selectedRadio.checked = true;

  // Initial fetch and render of routes
  const initialRoutes = await fetchRoutesByDirection(storedDirection);
  await renderRouteOptions(initialRoutes);

  // Event listeners for changing direction
  directionRadios.forEach((radio) => {
    radio.addEventListener("change", async (e) => {
      const direction = e.target.value;
      localStorage.setItem("direction", direction);
      const routes = await fetchRoutesByDirection(direction);
      await renderRouteOptions(routes);
    });
  });
});
