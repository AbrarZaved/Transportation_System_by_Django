import { showToast } from "./utils.js";
document.addEventListener("DOMContentLoaded", () => {
  const msg = document.getElementById("update-success");
  if (msg) {
    showToast("Profile updated", msg.dataset.message);
  }
  const modal = document.getElementById("editProfile");
  const modalContent = document.getElementById("editModalContent");
  const editButton = document.getElementById("edit");
  const historyButton = document.getElementById("historyButton");
  const historyModal = document.getElementById("historyModal");
  const historyList = document.getElementById("historyList");

  let batchCode = document.getElementById("batch").dataset.profile;
  let deptName = document.getElementById("dept").dataset.profile;
  if (!batchCode || !deptName) {
    showToast(
      "Please complete your profile",
      "Your information is required to proceed"
    );
  }
  if (editButton) {
    editButton.addEventListener("click", openEditModal);
  }

  if (modal) {
    modal.addEventListener("click", (e) => {
      if (!modalContent.contains(e.target)) closeEditModal();
    });
  }

  if (historyButton) {
    historyButton.addEventListener("click", openHistoryModal);
  }

  if (historyModal) {
    historyModal.addEventListener("click", handleHistoryModalClick);
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (!modal.classList.contains("hidden")) closeEditModal();
      if (historyModal.style.display === "flex") closeHistoryModal();
    }
  });

  function openEditModal() {
    modal.classList.remove("hidden");
    setTimeout(() => {
      modalContent.classList.remove("scale-90", "opacity-0");
      modalContent.classList.add("scale-100", "opacity-100");
    }, 10);
    document.body.style.overflow = "hidden";
  }

  function closeEditModal() {
    modalContent.classList.remove("scale-100", "opacity-100");
    modalContent.classList.add("scale-90", "opacity-0");
    setTimeout(() => {
      modal.classList.add("hidden");
      document.body.style.overflow = "";
    }, 300);
  }

  function openHistoryModal() {
    historyModal.style.display = "flex";
    fetchSearchHistory();
  }

  function closeHistoryModal() {
    historyModal.style.display = "none";
  }

  function handleHistoryModalClick(event) {
    if (
      event.target.classList.contains("modal-overlay") ||
      event.target.classList.contains("close-button")
    ) {
      closeHistoryModal();
    }
  }

  async function fetchSearchHistory() {
    const studentId = localStorage.getItem("student_id");
    if (!studentId) return;

    try {
      const res = await fetch(`get_history`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ studentId }),
      });

      const data = await res.json();
      renderHistory(data.history || []);
    } catch (error) {
      console.error("Error fetching history:", error);
      historyList.innerHTML = `<li class="text-red-500">Failed to load history.</li>`;
    }
  }

  function renderHistory(history) {
    historyList.innerHTML = "";

    if (history.length === 0) {
      historyList.innerHTML = `<li>No history found.</li>`;
      return;
    }

    history.forEach((item) => {
      const li = document.createElement("li");
      li.innerHTML = `
        <span>${item.place}</span>
        <button name="place_id" class="delete-history-btn" data-id="${item.id}">
          Delete
        </button>
      `;
      historyList.appendChild(li);
    });

    document.querySelectorAll(".delete-history-btn").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        e.preventDefault();
        const id = btn.dataset.id;
        if (id) await deleteHistory(id, btn);
      });
    });
  }

  async function deleteHistory(id, button) {
    try {
      const res = await fetch(`delete_history/${id}/`, {
        method: "DELETE",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
      });

      if (res.ok) {
        const li = button.closest("li");
        if (li) li.remove();
      } else {
        alert("Failed to delete item.");
      }
    } catch (error) {
      console.error("Error deleting history:", error);
      alert("An error occurred while deleting the item.");
    }
  }

  function getCookie(name) {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        return decodeURIComponent(cookie.slice(name.length + 1));
      }
    }
    return null;
  }
});
