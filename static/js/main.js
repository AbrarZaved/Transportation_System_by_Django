import { csrfFetch } from "./api.js";
import {
  buildBusCards,
  setupModalHandlers,
  formatTime,
  renderNoRoutesFound,
} from "./utils.js";

document.addEventListener("DOMContentLoaded", function () {
  console.log("loaded");

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

      const response = await csrfFetch("http://127.0.0.1:8000/search_route", {
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
      results.innerHTML = `<p>Failed to load routes. Please try again later.</p>`;
      results.style.display = "block";
    }
  });
});
