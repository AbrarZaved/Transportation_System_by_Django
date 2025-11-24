// Reviews Page JavaScript
// Global data arrays
const BUSES_DATA = [];
const DRIVERS_DATA = [];

// Global function to set buses and drivers data from template
window.setReviewsData = function (buses, drivers) {
  BUSES_DATA.length = 0; // Clear existing data
  DRIVERS_DATA.length = 0;
  BUSES_DATA.push(...buses);
  DRIVERS_DATA.push(...drivers);

  // If DOM is already loaded, populate selects immediately
  if (document.readyState === "loading") {
    // DOM not yet loaded, set a flag to populate later
    window.reviewsDataReady = true;
  } else {
    // DOM is ready, populate now
    populateSelects();
  }
};

// Helper function to populate both selects
function populateSelects() {
  if (document.getElementById("busSelect")) {
    window.populateBusSelect();
  }
  if (document.getElementById("driverSelect")) {
    window.populateDriverSelect();
  }
}

// Global populate functions
window.populateBusSelect = function () {
  const busSelect = document.getElementById("busSelect");
  if (!busSelect || BUSES_DATA.length === 0) return;

  busSelect.innerHTML = '<option value="">Choose a bus...</option>';
  BUSES_DATA.forEach((bus) => {
    const option = document.createElement("option");
    option.value = bus.id;
    option.textContent = `${bus.bus_name} (${bus.bus_tag || ""})`;
    busSelect.appendChild(option);
  });
};

window.populateDriverSelect = function () {
  const driverSelect = document.getElementById("driverSelect");
  if (!driverSelect || DRIVERS_DATA.length === 0) return;

  driverSelect.innerHTML = '<option value="">Choose a driver...</option>';
  DRIVERS_DATA.forEach((driver) => {
    const option = document.createElement("option");
    option.value = driver.id;
    option.textContent = driver.driver_name;
    driverSelect.appendChild(option);
  });
};

document.addEventListener("DOMContentLoaded", function () {
  // Check if data was set before DOM loaded
  if (
    window.reviewsDataReady &&
    BUSES_DATA.length > 0 &&
    DRIVERS_DATA.length > 0
  ) {
    populateSelects();
  }

  // Initialize components
  initializeReviewForm();
  initializeDeleteButtons();
  loadSelectOptions();

  /**
   * Initialize the review submission form
   */
  function initializeReviewForm() {
    const reviewForm = document.getElementById("reviewForm");
    const reviewTypeRadios = document.querySelectorAll(
      'input[name="review_type"]'
    );
    const busSelectDiv = document.getElementById("busSelectDiv");
    const driverSelectDiv = document.getElementById("driverSelectDiv");
    const busSelect = document.getElementById("busSelect");
    const driverSelect = document.getElementById("driverSelect");

    if (!reviewForm) return;

    // Handle review type change
    reviewTypeRadios.forEach((radio) => {
      radio.addEventListener("change", function () {
        updateFormFields(this.value);
      });
    });

    // Handle form submission
    reviewForm.addEventListener("submit", function (e) {
      e.preventDefault();
      submitReview();
    });

    // Initialize with default selection
    updateFormFields("bus");

    function updateFormFields(reviewType) {
      switch (reviewType) {
        case "bus":
          busSelectDiv.style.display = "block";
          driverSelectDiv.style.display = "none";
          busSelect.required = true;
          driverSelect.required = false;
          break;
        case "driver":
          busSelectDiv.style.display = "none";
          driverSelectDiv.style.display = "block";
          busSelect.required = false;
          driverSelect.required = true;
          break;
      }
    }
  }

  /**
   * Load buses and routes data for select options
   */
  function loadSelectOptions() {
    // Data should already be loaded via window.setReviewsData
    // This is just a fallback for any additional loading needed
    if (BUSES_DATA.length === 0 || DRIVERS_DATA.length === 0) {
      // Try loading from embedded JSON (fallback)
      const busesScript = document.querySelector(
        'script[type="application/json"][data-buses]'
      );
      if (busesScript) {
        try {
          BUSES_DATA.push(...JSON.parse(busesScript.textContent));
        } catch (e) {
          console.error("Error parsing buses data:", e);
        }
      }

      const driversScript = document.querySelector(
        'script[type="application/json"][data-drivers]'
      );
      if (driversScript) {
        try {
          DRIVERS_DATA.push(...JSON.parse(driversScript.textContent));
        } catch (e) {
          console.error("Error parsing drivers data:", e);
        }
      }
    }

    // Populate select options
    window.populateBusSelect();
    window.populateDriverSelect();
  }

  /**
   * Update target select options based on review type
   */
  function updateTargetOptions(reviewType) {
    const targetSelect = document.getElementById("targetSelect");
    if (!targetSelect) return;

    // Clear existing options
    targetSelect.innerHTML = '<option value="">Choose...</option>';

    let data = [];
    let placeholder = "";

    if (reviewType === "bus") {
      data = BUSES_DATA;
      placeholder = "Select a bus";
      targetSelect.setAttribute("data-type", "bus");
    } else {
      data = DRIVERS_DATA;
      placeholder = "Select a driver";
      targetSelect.setAttribute("data-type", "driver");
    }

    // Add options
    data.forEach((item) => {
      const option = document.createElement("option");
      option.value = item.id;
      if (reviewType === "bus") {
        option.textContent = `${item.bus_name} (${item.bus_tag || ""})`;
      } else {
        option.textContent = item.driver_name;
      }
      targetSelect.appendChild(option);
    });

    // Update placeholder
    targetSelect.firstElementChild.textContent = placeholder;
  }

  /**
   * Submit review form
   */
  async function submitReview() {
    const form = document.getElementById("reviewForm");
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;

    // Get form data
    const reviewType = form.querySelector(
      'input[name="review_type"]:checked'
    )?.value;
    const busId = form.querySelector("#busSelect").value;
    const driverId = form.querySelector("#driverSelect").value;
    const rating = form.querySelector('input[name="rating"]:checked')?.value;
    const comment = form.querySelector("#comment").value.trim();

    // Validate form based on review type
    if (!reviewType || !rating || !comment) {
      showToast("error", "Please fill in all required fields.");
      return;
    }

    // Validate selections based on review type
    if (reviewType === "bus" && !busId) {
      showToast("error", "Please select a bus to review.");
      return;
    } else if (reviewType === "driver" && !driverId) {
      showToast("error", "Please select a driver to review.");
      return;
    }

    if (comment.length < 10) {
      showToast("error", "Comment must be at least 10 characters long.");
      return;
    }

    // Show loading state
    submitBtn.innerHTML =
      '<i class="fas fa-spinner fa-spin"></i> Submitting...';
    submitBtn.disabled = true;

    try {
      const response = await fetch("/submit_review/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({
          review_type: reviewType,
          bus_id: busId ? parseInt(busId) : null,
          driver_id: driverId ? parseInt(driverId) : null,
          rating: parseInt(rating),
          comment: comment,
        }),
      });

      const result = await response.json();

      if (response.ok && result.success) {
        showToast("success", result.message);
        form.reset();
        window.populateBusSelect();
        window.populateDriverSelect();

        // Refresh page after short delay
        setTimeout(() => {
          window.location.reload();
        }, 1500);
      } else {
        showToast("error", result.message || "Failed to submit review.");
      }
    } catch (error) {
      console.error("Error submitting review:", error);
      showToast("error", "Network error. Please try again.");
    } finally {
      // Restore button state
      submitBtn.innerHTML = originalBtnText;
      submitBtn.disabled = false;
    }
  }

  /**
   * Initialize delete review buttons
   */
  function initializeDeleteButtons() {
    const deleteButtons = document.querySelectorAll(".delete-review");

    deleteButtons.forEach((btn) => {
      btn.addEventListener("click", function () {
        const reviewId = this.getAttribute("data-review-id");
        if (reviewId) {
          deleteReview(reviewId, this);
        }
      });
    });
  }

  /**
   * Delete a review
   */
  async function deleteReview(reviewId, button) {
    if (!confirm("Are you sure you want to delete this review?")) {
      return;
    }

    const originalBtnContent = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    button.disabled = true;

    try {
      const response = await fetch(`/delete_review/${reviewId}/`, {
        method: "DELETE",
        headers: {
          "X-CSRFToken": getCSRFToken(),
        },
      });

      const result = await response.json();

      if (response.ok && result.success) {
        showToast("success", result.message);

        // Remove the review item from DOM
        const reviewItem = button.closest(
          ".user-review-item, [class*='border-l-4']"
        );
        if (reviewItem) {
          reviewItem.classList.add("slide-up");
          setTimeout(() => {
            reviewItem.remove();

            // Check if no more reviews
            const reviewsContainer = reviewItem.closest(
              ".your-reviews-card, [class*='space-y-4']"
            );
            const remainingReviews = reviewsContainer?.querySelectorAll(
              ".user-review-item, [class*='border-l-4']"
            );
            if (!remainingReviews?.length) {
              const reviewsCard = reviewsContainer.closest(
                ".your-reviews-card, [class*='bg-white'][class*='rounded-xl']"
              );
              if (reviewsCard) {
                reviewsCard.style.display = "none";
              }
            }
          }, 300);
        }
      } else {
        showToast("error", result.message || "Failed to delete review.");
        button.innerHTML = originalBtnContent;
        button.disabled = false;
      }
    } catch (error) {
      console.error("Error deleting review:", error);
      showToast("error", "Network error. Please try again.");
      button.innerHTML = originalBtnContent;
      button.disabled = false;
    }
  }

  /**
   * Show toast notification
   */
  function showToast(type, message) {
    // Use the global showToast function if available, otherwise fallback
    if (typeof window.showToast === "function") {
      window.showToast(type, message);
    } else {
      const toast = document.getElementById(type + "Toast");
      const messageEl = document.getElementById(type + "Message");

      if (toast && messageEl) {
        messageEl.textContent = message;
        toast.classList.remove("hidden");

        setTimeout(() => {
          toast.classList.add("hidden");
        }, 5000);
      } else {
        // Fallback to alert
        alert(message);
      }
    }
  }

  /**
   * Get CSRF token from cookie
   */
  function getCSRFToken() {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      const [name, value] = cookie.trim().split("=");
      if (name === "csrftoken") {
        return decodeURIComponent(value);
      }
    }

    // Fallback: try to get from meta tag
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
      return metaTag.getAttribute("content");
    }

    return "";
  }

  /**
   * Add animation classes to elements as they come into view
   */
  function initializeAnimations() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: "0px 0px -50px 0px",
    };

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("fade-in");
        }
      });
    }, observerOptions);

    // Observe review cards
    const reviewCards = document.querySelectorAll(".review-card");
    reviewCards.forEach((card) => {
      observer.observe(card);
    });
  }

  // Initialize animations
  initializeAnimations();

  /**
   * Handle rating stars interaction in display
   */
  function initializeRatingStars() {
    const ratingInputs = document.querySelectorAll(".rating-input");

    ratingInputs.forEach((ratingInput) => {
      const stars = ratingInput.querySelectorAll("label.star");
      const inputs = ratingInput.querySelectorAll('input[name="rating"]');

      stars.forEach((star, index) => {
        star.addEventListener("mouseenter", function () {
          highlightStars(stars, stars.length - index);
        });

        star.addEventListener("mouseleave", function () {
          const checkedInput = ratingInput.querySelector(
            'input[name="rating"]:checked'
          );
          if (checkedInput) {
            const checkedValue = parseInt(checkedInput.value);
            highlightStars(stars, checkedValue);
          } else {
            clearStarHighlight(stars);
          }
        });
      });

      inputs.forEach((input) => {
        input.addEventListener("change", function () {
          highlightStars(stars, parseInt(this.value));
        });
      });
    });
  }

  /**
   * Highlight rating stars
   */
  function highlightStars(stars, rating) {
    stars.forEach((star, index) => {
      if (stars.length - index <= rating) {
        star.style.color = "#ffc107";
        star.style.transform = "scale(1.1)";
      } else {
        star.style.color = "#ddd";
        star.style.transform = "scale(1)";
      }
    });
  }

  /**
   * Clear star highlighting
   */
  function clearStarHighlight(stars) {
    stars.forEach((star) => {
      star.style.color = "#ddd";
      star.style.transform = "scale(1)";
    });
  }

  // Initialize rating stars
  initializeRatingStars();

  /**
   * Search functionality enhancement
   */
  function initializeSearch() {
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
      // Add search on enter key
      searchInput.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
          e.preventDefault();
          this.closest("form").submit();
        }
      });
    }
  }

  // Initialize search
  initializeSearch();
});
