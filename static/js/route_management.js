import { getCookie } from "/static/js/utils.js";
function stoppageAdd(stoppageId, buttonId) {
  const stoppageFields = document.getElementById(`${stoppageId}`);
  const addBtn = document.getElementById(`${buttonId}`);

  // Remove any existing event listeners by cloning the button
  if (addBtn && !addBtn.hasAttribute("data-listener-added")) {
    addBtn.addEventListener("click", () => {
      const wrapper = document.createElement("div");
      wrapper.className = "flex gap-2 items-center";

      let options = `<option disabled selected>Choose a stoppage</option>`;
      stoppagesList.forEach((stop) => {
        options += `<option value="${stop.id}">${stop.stoppage_name}</option>`;
      });

      wrapper.innerHTML = `
          <select name="stoppages[]" class="w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:ring-indigo-500 focus:outline-none">
              ${options}
          </select>
          <button type="button" class="remove-stoppage text-red-500 hover:text-red-700">✕</button>
      `;

      stoppageFields.appendChild(wrapper);
    });

    // Mark that listener has been added
    addBtn.setAttribute("data-listener-added", "true");
  }
}
document.addEventListener("DOMContentLoaded", () => {
  const addRouteModal = document.getElementById("addRouteModal");
  const viewRouteModal = document.getElementById("viewRouteModal");

  const addRouteBtn = document.getElementById("addRouteBtn");
  const closeAddRouteModalBtn = document.getElementById("closeAddRouteModal");
  const closeViewRouteModalBtn = document.getElementById("closeViewRouteModal");

  if (addRouteBtn) {
    addRouteBtn.addEventListener("click", () => {
      addRouteModal.classList.remove("hidden");
      addRouteModal.querySelector("div").classList.remove("scale-95");
      addRouteModal.querySelector("div").classList.add("scale-100");
    });
  }

  if (closeAddRouteModalBtn) {
    closeAddRouteModalBtn.addEventListener("click", () => {
      addRouteModal.classList.add("hidden");
      addRouteModal.querySelector("div").classList.remove("scale-100");
      addRouteModal.querySelector("div").classList.add("scale-95");
    });
  }

  if (closeViewRouteModalBtn) {
    closeViewRouteModalBtn.addEventListener("click", () => {
      viewRouteModal.classList.add("hidden");
      viewRouteModal.querySelector("div").classList.remove("scale-100");
      viewRouteModal.querySelector("div").classList.add("scale-95");
    });
  }

  document.querySelectorAll(".view-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      // Fill form with existing route data
      document.getElementById("editRouteForm").action=`${location.origin}/update_route/${btn.dataset.routeId}`;
      document.getElementById("editRouteId").value = btn.dataset.routeId;
      document.getElementById("editRouteName").value = btn.dataset.routeName;
      document.getElementById("editRouteNumber").value =
        btn.dataset.routeNumber;
      document.getElementById("editRouteStatus").checked =
        btn.dataset.routeStatus === "True";
      document.getElementById("editFromDSC").checked =
        btn.dataset.routeDirection === "True";
      document.getElementById("editToDSC").checked =
        btn.dataset.routeDirection === "False";
      var route_id = btn.dataset.routeId;
      const csrftoken = getCookie("csrftoken");
      fetch(`${location.origin}/route_stoppages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({ route_id }),
      })
        .then((res) => res.json())
        .then((data) => {
          console.log(data);
          // Clear existing stoppages first
          const editStoppageFields =
            document.getElementById("editStoppageFields");
          editStoppageFields.innerHTML = "";

          if (data.stoppages && Array.isArray(data.stoppages)) {
            data.stoppages.forEach((stoppage) => {
              const wrapper = document.createElement("div");
              wrapper.className = "flex gap-2 items-center";

              const select = document.createElement("select");
              select.name = "stoppages[]";
              select.className =
                "w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:ring-indigo-500 focus:outline-none";

              const defaultOption = document.createElement("option");
              defaultOption.disabled = true;
              defaultOption.textContent = "Choose a stoppage";
              select.appendChild(defaultOption);
              stoppagesList.forEach((stop) => {
                const option = document.createElement("option");
                option.value = stop.id;
                option.textContent = stop.stoppage_name;
                // console.log(String(stop.id), String(stoppage.id));
                // Safe comparison for preselecting the correct stoppage
                if (
                  String(stop.stoppage_name) ===
                  String(stoppage.stoppage__stoppage_name)
                ) {
                  option.selected = true;
                }

                select.appendChild(option);
              });

              const removeBtn = document.createElement("button");
              removeBtn.type = "button";
              removeBtn.className =
                "remove-stoppage text-red-500 hover:text-red-700";
              removeBtn.textContent = "✕";

              wrapper.appendChild(select);
              wrapper.appendChild(removeBtn);
              editStoppageFields.appendChild(wrapper);
            });
          } else {
            console.error(
              "Expected data.stoppages to be an array but got:",
              data
            );
          }

          // Initialize the add stoppage functionality after loading existing stoppages
          stoppageAdd("editStoppageFields", "addEditStoppage");
        })
        .catch((error) => {
          console.error("Error fetching route stoppages:", error);
        });

      document.getElementById("editRouteModal").classList.remove("hidden");
    });
  });
  stoppageAdd("stoppageFields", "addStoppage");
  // Close modal
  const closeEditRouteModalBtn = document.getElementById("closeEditRouteModal");
  const cancelEditRouteBtn = document.getElementById("cancelEditRoute");

  if (closeEditRouteModalBtn) {
    closeEditRouteModalBtn.addEventListener("click", () => {
      document.getElementById("editRouteModal").classList.add("hidden");
    });
  }

  if (cancelEditRouteBtn) {
    cancelEditRouteBtn.addEventListener("click", () => {
      document.getElementById("editRouteModal").classList.add("hidden");
    });
  }

  // Remove the client-side search since we now have server-side search
  // Search is now handled by the form submission in the template

  // Delegate remove-stoppage button click event for dynamically added buttons
  document.addEventListener("click", function (e) {
    if (e.target && e.target.classList.contains("remove-stoppage")) {
      e.target.parentElement.remove();
    }
  });
});
