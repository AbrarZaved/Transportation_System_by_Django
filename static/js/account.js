document.addEventListener("DOMContentLoaded", () => {
  const historyButton = document.getElementById("historyButton");
  historyButton.addEventListener("click", openHistoryModal);
  function openHistoryModal() {
    document.getElementById("historyModal").style.display = "flex";
    fetchSearchHistory();
  }
  const historyModal = document.getElementById("historyModal");
  historyModal.addEventListener("click", closeHistoryModal);
  function closeHistoryModal(event) {
    if (
      event.target.classList.contains("modal-overlay") ||
      event.target.classList.contains("close-button")
    ) {
      document.getElementById("historyModal").style.display = "none";
    }
  }

  async function fetchSearchHistory() {
    const studentId = localStorage.getItem("student_id");
    const res = await fetch(`get_history`, {
      method: "POST",
      body: JSON.stringify({ studentId }),
    });
    const data = await res.json();
    console.log(data);

    const list = document.getElementById("historyList");
    list.innerHTML = "";

    if (data.history.length === 0) {
      list.innerHTML = `<li>No history found.</li>`;
      return;
    }

    data.history.forEach((item) => {
      const li = document.createElement("li");
      li.innerHTML = `
        <span>${item.place}</span>
        <button name="place_id" id="${item.id}">Delete</button>
      `;
      list.appendChild(li);
    });
    var placeId = document.querySelectorAll('button[name="place_id"]');
    placeId.forEach((button) => {
      button.addEventListener("click", async (e) => {
        e.preventDefault();
        const id = button.id;
        console.log(id);
        await deleteHistory(id, button);
      });
    });
  }

  async function deleteHistory(id, btn) {
    const res = await fetch(`delete_history/${id}/`, {
      method: "DELETE",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
    });

    if (res.ok) {
      btn.closest("li").remove();
    } else {
      alert("Failed to delete item.");
    }
  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
