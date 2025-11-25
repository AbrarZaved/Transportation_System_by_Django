// Immediately define global functions for HTML onclick attributes
function viewNotice(id, title, message, type) {
  const typeLabels = {
    info: "Information",
    warning: "Warning",
    urgent: "Urgent",
    maintenance: "Maintenance",
  };

  const typeColors = {
    info: "border-blue-200 bg-blue-50",
    warning: "border-yellow-200 bg-yellow-50",
    urgent: "border-red-200 bg-red-50",
    maintenance: "border-gray-200 bg-gray-50",
  };

  document.getElementById("modalContent").innerHTML = `
    <div class="border ${typeColors[type]} rounded-lg p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <div class="w-3 h-3 bg-blue-500 rounded-full mt-1"></div>
        </div>
        <div class="ml-3">
          <div class="flex items-center space-x-2 mb-2">
            <h4 class="text-sm font-semibold text-gray-800">${title}</h4>
            <span class="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600">${typeLabels[type]}</span>
          </div>
          <p class="text-sm text-gray-600 mt-2">${message}</p>
        </div>
      </div>
    </div>
  `;

  document.getElementById("noticeModal").classList.remove("hidden");
}

function closeModal() {
  document.getElementById("noticeModal").classList.add("hidden");
}

function toggleNotice(id, newStatus) {
  // Make AJAX request to toggle notice status
  fetch("/transport_manager/toggle_notice/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({
      notice_id: id,
      is_active: newStatus,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Reload the page to show updated status
        location.reload();
      } else {
        alert("Error: " + data.message);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("An error occurred while updating the notice status.");
    });
}

// Function to get CSRF token
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Also assign to window for extra safety
window.viewNotice = viewNotice;
window.closeModal = closeModal;
window.toggleNotice = toggleNotice;

// Search and filter functionality
document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("searchInput");
  const routeFilter = document.getElementById("routeFilter");
  const statusFilter = document.getElementById("statusFilter");
  const noticeRows = document.querySelectorAll("tbody tr");

  function filterNotices() {
    const searchTerm = searchInput.value.toLowerCase();
    const routeValue = routeFilter.value.toLowerCase();
    const statusValue = statusFilter.value.toLowerCase();

    noticeRows.forEach((row) => {
      const title = row.querySelector("h3").textContent.toLowerCase();
      const message = row.querySelector("p").textContent.toLowerCase();
      const routeText = row
        .querySelector("td:nth-child(3) span")
        .textContent.toLowerCase();
      const statusText = row
        .querySelector("td:nth-child(4) span")
        .textContent.toLowerCase();

      const matchesSearch =
        !searchTerm ||
        title.includes(searchTerm) ||
        message.includes(searchTerm);
      const matchesRoute =
        !routeValue ||
        (routeValue === "global" && routeText.includes("global")) ||
        (routeValue !== "global" && routeText.includes(routeValue));
      const matchesStatus = !statusValue || statusText.includes(statusValue);

      if (matchesSearch && matchesRoute && matchesStatus) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    });
  }

  searchInput.addEventListener("input", filterNotices);
  routeFilter.addEventListener("change", filterNotices);
  statusFilter.addEventListener("change", filterNotices);

  // Close modal when clicking outside
  document
    .getElementById("noticeModal")
    .addEventListener("click", function (e) {
      if (e.target === this) {
        closeModal();
      }
    });
});
