document.addEventListener("DOMContentLoaded", function () {
  const messageTextarea = document.getElementById("message");
  const charCount = document.getElementById("charCount");
  const previewBtn = document.getElementById("previewBtn");
  const noticePreview = document.getElementById("noticePreview");
  const previewContent = document.getElementById("previewContent");
  const routeSearch = document.getElementById("routeSearch");
  const routeSelect = document.getElementById("route");
  const routeDropdown = document.getElementById("routeDropdown");

  // Route search functionality
  let selectedRoute = "";

  routeSearch.addEventListener("input", function () {
    const query = this.value.toLowerCase();
    const dropdown = routeDropdown;
    const items = dropdown.querySelectorAll("[data-value]");

    dropdown.classList.remove("hidden");

    items.forEach((item) => {
      const routeName = item.getAttribute("data-name");
      if (
        !query ||
        (routeName && routeName.includes(query)) ||
        item.getAttribute("data-value") === ""
      ) {
        item.style.display = "block";
      } else {
        item.style.display = "none";
      }
    });
  });

  routeSearch.addEventListener("focus", function () {
    routeDropdown.classList.remove("hidden");
  });

  // Route selection
  routeDropdown.addEventListener("click", function (e) {
    const item = e.target.closest("[data-value]");
    if (item) {
      const value = item.getAttribute("data-value");
      const text = item.querySelector(".text-sm").textContent;

      routeSearch.value = value ? text : "";
      routeSelect.value = value;
      routeDropdown.classList.add("hidden");
      selectedRoute = text;
    }
  });

  // Hide dropdown when clicking outside
  document.addEventListener("click", function (e) {
    if (!routeSearch.contains(e.target) && !routeDropdown.contains(e.target)) {
      routeDropdown.classList.add("hidden");
    }
  });

  // Character count
  messageTextarea.addEventListener("input", function () {
    const count = this.value.length;
    charCount.textContent = `${count}/500`;
    if (count > 450) {
      charCount.classList.add("text-red-500");
    } else {
      charCount.classList.remove("text-red-500");
    }
  });

  // Preview functionality
  previewBtn.addEventListener("click", function () {
    const title = document.getElementById("title").value;
    const noticeType = document.getElementById("notice_type").value;
    const message = document.getElementById("message").value;
    const routeText = selectedRoute || "Global Notice";

    if (!title || !noticeType || !message) {
      alert("Please fill in all required fields to preview");
      return;
    }

    const typeColors = {
      info: "border-blue-200 bg-blue-50",
      warning: "border-yellow-200 bg-yellow-50",
      urgent: "border-red-200 bg-red-50",
      maintenance: "border-gray-200 bg-gray-50",
    };

    const typeLabels = {
      info: "Information",
      warning: "Warning",
      urgent: "Urgent",
      maintenance: "Maintenance",
    };

    previewContent.innerHTML = `
      <div class="border ${typeColors[noticeType]} rounded-lg p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <div class="w-3 h-3 bg-blue-500 rounded-full mt-1"></div>
          </div>
          <div class="ml-3">
            <div class="flex items-center space-x-2 mb-1">
              <h4 class="text-sm font-semibold text-gray-800">${title}</h4>
              <span class="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600">${typeLabels[noticeType]}</span>
            </div>
            <p class="text-sm text-gray-600">${message}</p>
            <p class="text-xs text-gray-500 mt-2">Target: ${routeText}</p>
          </div>
        </div>
      </div>
    `;

    noticePreview.classList.remove("hidden");
    noticePreview.scrollIntoView({ behavior: "smooth" });
  });

  // Set minimum datetime to current time
  const now = new Date();
  const currentDateTime = now.toISOString().slice(0, 16);
  document.getElementById("expires_at").min = currentDateTime;
});
