import { csrfFetch } from "./api.js";
import {
  buildBusCards,
  renderNoRoutesFound,
  filterRoutesByTime,
} from "./utils.js";

let filterRoute = null;
let filterTime = "all";

async function handleRecentSearch(studentId) {
  document.querySelectorAll('[name="recent_searches"]').forEach((el) => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      const tripType = document.querySelector(
        'input[name="trip-type"]:checked'
      ).value;
      const place = el.textContent.trim();
      document.getElementById("place").value = place;
      fetchRoutes(place, tripType, studentId, filterTime);
    });
  });
}

async function fetchRoutes(place, tripType, studentId, timeFilter = "all") {
  const recentSearchContainer = document.getElementById("recent-searches");
  const loadingSpinner = document.getElementById("loading-screen");
  const results = document.getElementById("results");

  let recentSearches = [];
  if (recentSearchContainer) {
    recentSearches = Array.from(recentSearchContainer.children).map((child) =>
      child.textContent.trim()
    );
  }

  let routeData = null;
  try {
    loadingSpinner?.classList.remove("hidden");
    results.innerHTML = "";

    const response = await csrfFetch(`${location.origin}/search_route/`, {
      method: "POST",
      body: JSON.stringify({ tripType, place, studentId }),
    });

    routeData = response.routes;
    filterRoute = routeData;
    if (!routeData || routeData.length === 0) {
      results.innerHTML = renderNoRoutesFound("No Routes Found");
      return;
    }

    if (!recentSearches.includes(place) && recentSearchContainer) {
      recentSearchContainer.innerHTML += `<span name="recent_searches" class="bg-white border border-pink-200 text-pink-600 text-sm font-medium px-3 py-1 rounded-full cursor-pointer hover:bg-pink-50 transition">${
        place.charAt(0).toUpperCase() + place.slice(1)
      }</span>`;
      await handleRecentSearch(studentId);
    }

    const filtered = await filterRoutesByTime(routeData, timeFilter);
    if (filtered.length === 0) {
      results.innerHTML = renderNoRoutesFound(
        "No routes found for the selected time"
      );
    } else {
      results.innerHTML = buildBusCards(filtered);
      requestAnimationFrame(() => {
        results.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
  } catch (error) {
    console.error("Error fetching routes:", error);
    results.innerHTML = `
      <div class="p-6 bg-red-100 border border-red-300 rounded-md text-red-700 text-center text-base">
        <svg xmlns="http://www.w3.org/2000/svg" class="inline mr-2" width="24" height="24" fill="none" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="12" fill="#ffb3b3"/>
          <path d="M12 7v5m0 3h.01" stroke="#b30000" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <span>Failed to load routes. Please try again later.</span>
      </div>
    `;
  } finally {
    loadingSpinner?.classList.add("hidden");
    results.style.display = "block";
  }
}

function setupTimeFilterButtons() {
  document.querySelectorAll(".time-filter-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      filterTime = btn.dataset.time;

      document.querySelectorAll(".time-filter-btn").forEach((b) => {
        b.classList.remove("border-pink-500", "text-pink-600", "bg-pink-50");
      });
      btn.classList.add("border-pink-500", "text-pink-600", "bg-pink-50");

      if (!filterRoute) return;

      const filtered = await filterRoutesByTime(filterRoute, filterTime);
      const results = document.getElementById("results");
      if (filtered.length === 0 || !filtered) {
        results.innerHTML = renderNoRoutesFound(
          "No routes found for the selected time"
        );
      } else {
        results.innerHTML = buildBusCards(filtered);
        results.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });
}

function setupScrollToTop() {
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
}

function setupRouteCardToggles() {
  document.querySelectorAll(".route-card").forEach((card) => {
    const details = card.querySelector(".bus-details");
    if (!details) return;

    card.addEventListener("click", () => {
      const isExpanded = details.classList.contains("expanded");

      if (isExpanded) {
        details.style.height = details.scrollHeight + "px";
        details.offsetHeight;
        details.style.height = "0px";
        details.classList.remove("expanded");
      } else {
        details.style.height = details.scrollHeight + "px";
        details.classList.add("expanded");
      }
    });

    details.addEventListener("transitionend", () => {
      if (details.classList.contains("expanded")) {
        details.style.height = "auto";
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  const studentId = localStorage.getItem("student_id");
  const results = document.getElementById("results");
  results.style.display = "none";

  setupScrollToTop();
  setupTimeFilterButtons();
  setupRouteCardToggles();

  document.querySelectorAll('input[name="trip-type"]').forEach((radio) => {
    radio.addEventListener("change", function () {
      const placeInput = document.getElementById("place");
      placeInput.placeholder =
        this.value === "To DSC"
          ? "From which place to DSC?"
          : "Enter your destination";
    });
  });

  if (studentId) await handleRecentSearch(studentId);

  document.getElementById("search").addEventListener("click", async (e) => {
    e.preventDefault();
    const place = document.getElementById("place").value.trim();
    const tripType = document.querySelector(
      'input[name="trip-type"]:checked'
    ).value;

    await fetchRoutes(place, tripType, studentId, filterTime);
  });
});
