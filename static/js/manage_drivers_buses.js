function filterBuses() {
  const query = document.getElementById("filter-bus").value.toLowerCase();
  const rows = document.querySelectorAll("#bus-details");

  rows.forEach((row) => {
    const keywords = row.getAttribute("bus-data").toLowerCase();
    row.style.display = keywords.includes(query) ? "table-row" : "none";
  });
}
function filterDrivers() {
  const query = document.getElementById("filter-driver").value.toLowerCase();
  const rows = document.querySelectorAll("#driver-details");

  rows.forEach((row) => {
    const keywords = row.getAttribute("driver-data").toLowerCase();
    row.style.display = keywords.includes(query) ? "table-row" : "none";
  });
}

function toggleModal(id) {
  const modal = document.getElementById(id);
  const content = modal.querySelector(".transform");
  if (modal.classList.contains("hidden")) {
    modal.classList.remove("hidden");
    setTimeout(() => {
      content.classList.remove("scale-90", "opacity-0");
      content.classList.add("scale-100", "opacity-100");
      modal.classList.remove("animate-fade-out");
      modal.classList.add("animate-fade-in");
    }, 10);
  } else {
    content.classList.remove("scale-100", "opacity-100");
    content.classList.add("scale-90", "opacity-0");
    modal.classList.remove("animate-fade-in");
    modal.classList.add("animate-fade-out");
    setTimeout(() => modal.classList.add("hidden"), 300);
  }
}

function editBus(id, name, tag, number, model, capacity, status) {
  // Populate the edit form with current values
  document.getElementById("editBusId").value = id;
  document.getElementById("editBusName").value = name;
  document.getElementById("editBusTag").value = tag;
  document.getElementById("editBusNumber").value = number;
  document.getElementById("editBusModel").value = model;
  document.getElementById("editBusCapacity").value = capacity;
  document.getElementById("editBusStatus").checked = status;

  // Open the edit modal
  toggleModal("editBusModal");
}

function editDriver(
  id,
  name,
  phone,
  license,
  licenseClass,
  issued,
  expiry,
  country,
  status
) {
  // Populate the edit form with current values
  document.getElementById("editDriverId").value = id;
  document.getElementById("editDriverName").value = name;
  document.getElementById("editDriverPhone").value = phone || "";
  document.getElementById("editDriverLicense").value = license;
  document.getElementById("editDriverLicenseClass").value = licenseClass;
  document.getElementById("editDriverLicenseIssued").value = issued;
  document.getElementById("editDriverLicenseExpiry").value = expiry;
  document.getElementById("editDriverLicenseCountry").value = country;
  document.getElementById("editDriverStatus").checked = status;

  // Open the edit modal
  toggleModal("editDriverModal");
}
document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("filter-bus").addEventListener("input", filterBuses);
  document
    .getElementById("filter-driver")
    .addEventListener("input", filterDrivers);
  document.querySelectorAll(".modal-toggle").forEach((button) => {
    button.addEventListener("click", function () {
      const modalId = this.getAttribute("data-modal-id");
      toggleModal(modalId);
    });
  });
});
