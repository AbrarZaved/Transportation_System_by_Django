import { csrfFetch } from "./api.js";
import {
  buildBusCards,
  setupModalHandlers,
  formatTime,
  renderNoRoutesFound,
} from "./utils.js";

document.addEventListener("DOMContentLoaded", function () {
  console.log("loaded");
  window.scrollTo({ top: 0, behavior: "smooth" });

  const results = document.getElementById("results");
  results.style.display = "none";

  document.getElementById("search").addEventListener("click", async (e) => {
    e.preventDefault();

    const place = document.getElementById("place").value;
    const tripType = document.querySelector(
      'input[name="trip-type"]:checked'
    ).value;

    console.log("Selected Trip Type:", tripType);
    console.log("Entered Place:", place);

    try {
      const startTime = performance.now();

      const response = await csrfFetch(`${location.origin}/search_route`, {
        method: "POST",
        body: JSON.stringify({ tripType, place }),
      });

      const endTime = performance.now();
      console.log(
        `Request took ${(endTime - startTime).toFixed(2)} milliseconds.`
      );
      console.log(response);

      results.innerHTML = "";

      const routeData = response.routes;

      if (!routeData || routeData.length === 0) {
        results.style.display = "block";
        results.innerHTML = renderNoRoutesFound();
        return;
      }

      const htmlContent = buildBusCards(routeData);
      results.innerHTML = htmlContent;
      results.style.display = "block"; // <-- Move this before scroll
      results.scrollIntoView({ behavior: "smooth" });
      setupModalHandlers(routeData);
      results.style.display = "block";
    } catch (error) {
      console.error("Error:", error);
      results.innerHTML = `
        <div style="padding: 24px; background: #ffeaea; border: 1px solid #ffb3b3; border-radius: 8px; color: #b30000; text-align: center; font-size: 1.1em;">
          <svg xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle; margin-right: 8px;" width="24" height="24" fill="none" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="12" fill="#ffb3b3"/>
        <path d="M12 7v5m0 3h.01" stroke="#b30000" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span>Failed to load routes. Please try again later.</span>
        </div>
      `;
      results.style.display = "block";
    }
  });
});
