import { csrfFetch } from "./api.js";
import {
  buildBusCards,
  renderNoRoutesFound,
  filterRoutesByTime,
  showToast,
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

async function fetchRoutes(place, tripType, timeFilter = "all") {
  const recentSearchContainer = document.getElementById("recent-searches");
  const loadingSpinner = document.getElementById("loading-screen");
  const results = document.getElementById("results");
  
  let recentSearches = [];
  if (recentSearchContainer) {
    recentSearches = Array.from(recentSearchContainer.children).map((child) =>
      child.textContent.trim()
    );
  }
  console.log(recentSearches);
  let routeData = null;
  try {
    loadingSpinner?.classList.remove("hidden");
    results.innerHTML = "";

    const response = await csrfFetch(`${location.origin}/search_route/`, {
      method: "POST",
      body: JSON.stringify({ tripType, place }),
    });

    routeData = response.routes;
    filterRoute = routeData;
    if (!routeData || routeData.length === 0) {
      results.innerHTML = renderNoRoutesFound("No Routes Found");
      return;
    }

    if (!recentSearches.includes(place) && recentSearchContainer) {
      recentSearches.unshift(place);
      if (recentSearches.length > 3) {
        recentSearches.pop();
      }
      recentSearchContainer.innerHTML = "";
      recentSearches.forEach((search) => {
        recentSearchContainer.innerHTML += `<span name="recent_searches" class="bg-white border border-slate-200 text-slate-600 text-sm font-medium px-3 py-1 rounded-full cursor-pointer hover:bg-slate-50 transition">${
          search.charAt(0).toUpperCase() + search.slice(1)
        }</span>`;
      });

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
        b.classList.remove("border-slate-500", "text-slate-600", "bg-slate-50");
      });
      btn.classList.add("border-slate-500", "text-slate-600", "bg-slate-50");

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

// Clear sessionStorage on page unload (when session ends)
window.addEventListener("beforeunload", () => {
  // Clear stoppages from sessionStorage when user is leaving
  console.log("Clearing stoppages from sessionStorage");
});

// Clear sessionStorage when user logs out
function clearStoppagesCache() {
  sessionStorage.removeItem("stoppages");
  console.log("Stoppages cache cleared");
}

document.addEventListener("DOMContentLoaded", async () => {
  const messages = document.getElementById("messages");
  if (messages) {
    console.log(messages.dataset.message, messages.dataset.messageUsername);
  }
  
  if (messages) {
    showToast(messages.dataset.message, messages.dataset.messageUsername || null);
    // Clear stoppages cache on logout
    clearStoppagesCache();
  }
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

  await handleRecentSearch(studentId);
  document.getElementById("place").addEventListener("input", function () {
    document.getElementById("place-error").textContent = "";
  });
  document.getElementById("search").addEventListener("click", async (e) => {
    e.preventDefault();
    const place = document.getElementById("place").value.trim();
    const tripType = document.querySelector(
      'input[name="trip-type"]:checked'
    ).value;
    if (!place || place.length < 4) {
      document.getElementById("place-error").textContent =
        "Please enter a valid place.";
      return;
    } else {
      document.getElementById("place-error").textContent = "";
    }

    await fetchRoutes(place, tripType, studentId, filterTime);
  });
});

// Load stoppages into session storage
async function loadStoppagesIntoSession() {
  // Check if stoppages are already in sessionStorage
  const cachedStoppages = sessionStorage.getItem("stoppages");
  if (cachedStoppages) {
    console.log("Stoppages loaded from sessionStorage");
    return JSON.parse(cachedStoppages);
  }

  // If not in sessionStorage, fetch from API
  try {
    console.log("Fetching stoppages from API...");
    const response = await fetch(`${location.origin}/api/stoppages/`);
    const data = await response.json();

    // Store in sessionStorage for future use
    sessionStorage.setItem("stoppages", JSON.stringify(data.stoppages));
    console.log("Stoppages cached in sessionStorage");

    return data.stoppages || [];
  } catch (error) {
    console.error("Error fetching stoppages:", error);
    return [];
  }
}

// Autocomplete functionality with sessionStorage
function setupAutocomplete() {
  const placeInput = document.getElementById("place");
  const dropdown = document.getElementById("autocomplete-dropdown");
  const resultsList = document.getElementById("autocomplete-results");
  const loadingIndicator = document.getElementById("autocomplete-loading");
  const noResultsMessage = document.getElementById("autocomplete-no-results");

  let searchTimeout;
  let currentFocus = -1;
  let allStoppages = []; // Store all stoppages here

  if (!placeInput || !dropdown) return;

  // Function to filter stoppages locally
  function filterStoppages(query) {
    if (!query || query.length === 0) return [];

    return allStoppages
      .filter((stoppage) =>
        stoppage.stoppage_name.toLowerCase().includes(query.toLowerCase())
      )
      .slice(0, 10); // Limit to 10 results
  }

  // Function to render results
  function renderResults(stoppages) {
    resultsList.innerHTML = "";
    currentFocus = -1;

    if (stoppages.length === 0) {
      noResultsMessage.classList.remove("hidden");
      return;
    }

    noResultsMessage.classList.add("hidden");

    stoppages.forEach((stoppage, index) => {
      const li = document.createElement("li");
      li.className =
        "px-4 py-2 hover:bg-slate-50 cursor-pointer text-gray-700 border-b border-gray-100 last:border-b-0 transition-colors duration-150";
      li.textContent = stoppage.stoppage_name;
      li.dataset.index = index;

      // Click handler
      li.addEventListener("click", () => {
        placeInput.value = stoppage.stoppage_name;
        hideDropdown();
        placeInput.focus();
      });

      resultsList.appendChild(li);
    });
  }

  // Function to show dropdown
  function showDropdown() {
    dropdown.classList.remove("hidden");
  }

  // Function to hide dropdown
  function hideDropdown() {
    dropdown.classList.add("hidden");
    currentFocus = -1;
  }

  // Function to handle keyboard navigation
  function handleKeyNavigation(e) {
    const items = resultsList.querySelectorAll("li");

    if (e.key === "ArrowDown") {
      e.preventDefault();
      currentFocus++;
      if (currentFocus >= items.length) currentFocus = 0;
      setActive(items);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      currentFocus--;
      if (currentFocus < 0) currentFocus = items.length - 1;
      setActive(items);
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (currentFocus > -1 && items[currentFocus]) {
        items[currentFocus].click();
      }
    } else if (e.key === "Escape") {
      hideDropdown();
      placeInput.blur();
    }
  }

  // Function to set active item
  function setActive(items) {
    items.forEach((item, index) => {
      if (index === currentFocus) {
        item.classList.add("bg-slate-50");
      } else {
        item.classList.remove("bg-slate-50");
      }
    });
  }

  // Initialize autocomplete with stoppages data - only when needed
  let isInitialized = false;
  async function initializeAutocomplete() {
    if (isInitialized) return; // Don't initialize multiple times

    try {
      loadingIndicator.classList.remove("hidden");
      allStoppages = await loadStoppagesIntoSession();
      loadingIndicator.classList.add("hidden");
      isInitialized = true;
      console.log(`Loaded ${allStoppages.length} stoppages for autocomplete`);
    } catch (error) {
      console.error("Error initializing autocomplete:", error);
      loadingIndicator.classList.add("hidden");
    }
  }

  // Input event handler
  placeInput.addEventListener("input", async (e) => {
    const query = e.target.value.trim();

    clearTimeout(searchTimeout);

    if (query.length === 0) {
      hideDropdown();
      return;
    }

    // Initialize stoppages if not already done
    if (!isInitialized) {
      await initializeAutocomplete();
    }

    // Debounce the search (much faster now since it's local)
    searchTimeout = setTimeout(() => {
      showDropdown();
      const filteredStoppages = filterStoppages(query);
      renderResults(filteredStoppages);
    }, 150); // Reduced debounce time since we're searching locally
  });

  // Focus event handler - initialize only on first focus
  placeInput.addEventListener("focus", async () => {
    if (!isInitialized) {
      await initializeAutocomplete();
    }

    const query = placeInput.value.trim();
    if (query.length > 0) {
      showDropdown();
      const filteredStoppages = filterStoppages(query);
      renderResults(filteredStoppages);
    }
  });

  // Keyboard event handler
  placeInput.addEventListener("keydown", handleKeyNavigation);

  // Hide dropdown when clicking outside
  document.addEventListener("click", (e) => {
    if (!placeInput.contains(e.target) && !dropdown.contains(e.target)) {
      hideDropdown();
    }
  });

  // Don't initialize automatically - wait for user interaction
}

// Carousel functionality
document.addEventListener("DOMContentLoaded", function () {
  const carousel = document.getElementById("hero-carousel");
  if (!carousel) return;

  const items = carousel.querySelectorAll(".carousel-item");
  const indicators = carousel.querySelectorAll(".carousel-indicator");
  const prevButton = carousel.querySelector(".carousel-prev");
  const nextButton = carousel.querySelector(".carousel-next");

  let currentIndex = 0;
  let autoSlideInterval;

  function showSlide(index) {
    // Hide all items
    items.forEach((item, i) => {
      item.classList.toggle("opacity-100", i === index);
      item.classList.toggle("opacity-0", i !== index);
    });

    // Update indicators
    indicators.forEach((indicator, i) => {
      indicator.classList.toggle("active", i === index);
      indicator.classList.toggle("bg-opacity-100", i === index);
      indicator.classList.toggle("bg-opacity-50", i !== index);
    });

    currentIndex = index;
  }

  function nextSlide() {
    const nextIndex = (currentIndex + 1) % items.length;
    showSlide(nextIndex);
  }

  function prevSlide() {
    const prevIndex = (currentIndex - 1 + items.length) % items.length;
    showSlide(prevIndex);
  }

  function startAutoSlide() {
    autoSlideInterval = setInterval(nextSlide, 5000); // Change slide every 5 seconds
  }

  function stopAutoSlide() {
    clearInterval(autoSlideInterval);
  }

  // Event listeners
  nextButton?.addEventListener("click", () => {
    nextSlide();
    stopAutoSlide();
    startAutoSlide(); // Restart auto-slide
  });

  prevButton?.addEventListener("click", () => {
    prevSlide();
    stopAutoSlide();
    startAutoSlide(); // Restart auto-slide
  });

  // Indicator event listeners
  indicators.forEach((indicator, index) => {
    indicator.addEventListener("click", () => {
      showSlide(index);
      stopAutoSlide();
      startAutoSlide(); // Restart auto-slide
    });
  });

  // Pause auto-slide on hover
  carousel.addEventListener("mouseenter", stopAutoSlide);
  carousel.addEventListener("mouseleave", startAutoSlide);

  // Start auto-slide
  startAutoSlide();

  // Initialize first slide
  showSlide(0);

  // Initialize autocomplete
  setupAutocomplete();
});
