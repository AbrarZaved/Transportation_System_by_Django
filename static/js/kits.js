import { getCookie } from "/static/js/utils.js";

document.addEventListener("DOMContentLoaded", () => {
  const hamburger = document.getElementById("hamburgerBtn");
  const mobileMenu = document.getElementById("mobileMenu");
  const modal = document.getElementById("customModal");
  const modalContent = document.getElementById("modalContent");
  const studentIdInput = document.getElementById("student_id");
  const errorDisplay = document.getElementById("student-id-error");
  const loginBtn = document.getElementById("loginBtn");

  // Handle hamburger toggle
  hamburger?.addEventListener("click", () => {
    hamburger.classList.toggle("active");
    mobileMenu.classList.toggle("open");
  });

  // Open modal from both buttons
  ["sign_in_desktop", "sign_in_mobile"].forEach((id) => {
    const btn = document.getElementById(id);
    btn?.addEventListener("click", openModal);
  });

  // Open modal function
  function openModal() {
    modal.classList.remove("hidden");
    setTimeout(() => {
      modalContent.classList.remove("scale-90", "opacity-0");
      modalContent.classList.add("scale-100", "opacity-100");
      studentIdInput.focus();
    }, 10);
    document.body.style.overflow = "hidden"; // prevent scroll
  }

  // Close modal function
  function closeModal() {
    modalContent.classList.remove("scale-100", "opacity-100");
    modalContent.classList.add("scale-90", "opacity-0");
    setTimeout(() => {
      modal.classList.add("hidden");
      document.body.style.overflow = "";
    }, 300);
  }

  // Close modal on backdrop click
  modal.addEventListener("click", (e) => {
    if (!modalContent.contains(e.target)) closeModal();
  });

  // Close modal on Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !modal.classList.contains("hidden")) {
      closeModal();
    }
  });

  // Clear error on input focus
  studentIdInput.addEventListener("input", () => {
    errorDisplay.classList.add("hidden");
    errorDisplay.textContent = "";
  });

  // Handle form submission
  document
    .getElementById("sign-in-form")
    .addEventListener("submit", async (e) => {
      e.preventDefault();

      const student_id = studentIdInput.value.trim();
      errorDisplay.classList.add("hidden");
      errorDisplay.textContent = "";

      if (student_id.length < 9) {
        showError("Student ID must be at least 9 characters.");
        return;
      }

      loginBtn.disabled = true;
      loginBtn.textContent = "Logging in...";

      try {
        const response = await fetch("sign_in", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: JSON.stringify({ student_id }),
        });

        const data = await response.json();

        if (!response.ok) {
          showError(data.message || "Sign in failed.");
          return;
        }

        window.location.href = "/my_account";
      } catch {
        showError("Network error. Try again later.");
      }
    });

  // Show error helper
  function showError(message) {
    errorDisplay.textContent = message;
    errorDisplay.classList.remove("hidden");
    loginBtn.textContent = "Login";
    loginBtn.disabled = false;
  }
});
