import { csrfFetch } from "./api.js";
import { buildBusCards, renderNoRoutesFound } from "./utils.js";

async function handleRecentSearch(studentId) {
  document.querySelectorAll('[name="recent_searches"]').forEach((el) => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      setTimeout(() => {
        const tripType = document.querySelector(
          'input[name="trip-type"]:checked'
        ).value;
        const place = el.textContent.trim();
        document.getElementById("place").value = place;
        fetchRoutes(place, tripType, studentId);
      });
    });
  });
}

async function fetchRoutes(place, tripType, studentId) {
  let recentSearches = [];
  const recentSearchContainer = document.getElementById("recent-searches");

  if (recentSearchContainer) {
    recentSearches = Array.from(recentSearchContainer.children).map((child) =>
      child.textContent.trim()
    );
  }

  const loading_spinner = document.getElementById("loading-screen");
  let routeData = null;
  try {
    if (loading_spinner) loading_spinner.style.display = "block";

    const startTime = performance.now();

    const response = await csrfFetch(`${location.origin}/search_route/`, {
      method: "POST",
      body: JSON.stringify({ tripType, place, studentId }),
    });

    const endTime = performance.now();
    console.log(
      `Request took ${(endTime - startTime).toFixed(2)} milliseconds.`
    );
    console.log(response);

    results.innerHTML = "";

    routeData = response.routes;

    if (!routeData || routeData.length === 0) {
      if (loading_spinner) loading_spinner.style.display = "none";
      results.style.display = "block";
      results.innerHTML = renderNoRoutesFound();
      return;
    }
    if (!recentSearches.includes(place) && recentSearchContainer) {
      document.getElementById(
        "recent-searches"
      ).innerHTML += `<span name="recent_searches" class="bg-white border border-pink-200 text-pink-600 text-sm font-medium px-3 py-1 rounded-full cursor-pointer hover:bg-pink-50 transition">${
        place.charAt(0).toUpperCase() + place.slice(1)
      }</span>`;
      await handleRecentSearch(studentId);
    }

    const htmlContent = buildBusCards(routeData);
    results.innerHTML = htmlContent;
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
  } finally {
    if (loading_spinner) loading_spinner.style.display = "none";
    results.style.display = "block";
    if (routeData && routeData.length > 0) {
      results.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }
}

document.addEventListener("DOMContentLoaded", async function () {
  const scrollBtn = document.getElementById("scrollToTopBtn");
  window.addEventListener("scroll", () => {
    if (window.scrollY > 600) {
      scrollBtn.classList.remove("opacity-0", "pointer-events-none");
      scrollBtn.classList.add("opacity-100");
    } else {
      scrollBtn.classList.add("opacity-0", "pointer-events-none");
      scrollBtn.classList.remove("opacity-100");
    }
  });
  scrollBtn.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
  const cards = document.querySelectorAll(".route-card");

  cards.forEach((card) => {
    const details = card.querySelector(".bus-details");
    if (details) {
      card.addEventListener("click", () => {
        const isExpanded = details.classList.contains("expanded");

        if (isExpanded) {
          // COLLAPSING
          details.style.height = details.scrollHeight + "px"; // from auto to fixed px
          details.offsetHeight; // force reflow
          details.style.height = "0px";
          details.classList.remove("expanded");
        } else {
          // EXPANDING
          details.style.height = details.scrollHeight + "px";
          details.classList.add("expanded");
        }
      });

      // Cleanup on transition end
      details.addEventListener("transitionend", () => {
        if (details.classList.contains("expanded")) {
          details.style.height = "auto"; // allow natural resizing
        }
      });
    }
  });
  const studentId = localStorage.getItem("student_id");

  window.scrollTo({ top: 0, behavior: "smooth" });

  const results = document.getElementById("results");
  results.style.display = "none";

  // Update placeholder based on trip type selection
  document.querySelectorAll('input[name="trip-type"]').forEach((radio) => {
    radio.addEventListener("change", function () {
      const tripType = this.value;
      const placeInput = document.getElementById("place");
      if (tripType === "To DSC") {
        placeInput.placeholder = "From which place to DSC?";
      } else {
        placeInput.placeholder = "Enter your destination";
      }
    });
  });

  // Handle recent search clicks
  if (studentId) await handleRecentSearch(studentId);
  // Handle search button click
  document.getElementById("search").addEventListener("click", async (e) => {
    e.preventDefault();
    const place = document.getElementById("place").value.trim();
    const tripType = document.querySelector(
      'input[name="trip-type"]:checked'
    ).value;

    console.log("Selected Trip Type:", tripType);
    console.log("Entered Place:", place);
    console.log(studentId);

    fetchRoutes(place, tripType, studentId);
  });
});
