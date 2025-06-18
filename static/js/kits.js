import { getCookie } from "/static/js/utils.js";

document.addEventListener("DOMContentLoaded", function () {
  const hamburger = document.getElementById("hamburgerBtn");
  const signInBtn = document.getElementById("sign_in");
  const signUpBtn = document.getElementById("sign_up");
  const registerFields = document.getElementById("register_fields");
  const authMode = document.getElementById("auth_mode");
  const mobileMenu = document.getElementById("mobileMenu");
  const modal = document.getElementById("customModal");
  const modalContent = document.getElementById("modalContent");
  const studentIdInput = document.getElementById("student_id");
  const errorDisplay = document.getElementById("student-id-error");
  const submitBtn = document.getElementById("submit_btn");

  // Handle hamburger toggle
  hamburger?.addEventListener("click", () => {
    hamburger.classList.toggle("active");
    mobileMenu.classList.toggle("open");
  });

  ["sign_in_desktop", "sign_in_mobile"].forEach((id) => {
    const btn = document.getElementById(id);
    if (btn?.textContent === "Sign In") {
      localStorage.removeItem("student_id");
    }
    btn?.addEventListener("click", () => {
      if (hamburger && mobileMenu.classList.contains("open")) {
        hamburger.classList.remove("active");
        mobileMenu.classList.remove("open");
      }
      openModal();
    });
  });

  // Open and close modal
  function openModal() {
    modal.classList.remove("hidden");
    setTimeout(() => {
      modalContent.classList.remove("scale-90", "opacity-0");
      modalContent.classList.add("scale-100", "opacity-100");
      studentIdInput.focus();
    }, 10);
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    modalContent.classList.remove("scale-100", "opacity-100");
    modalContent.classList.add("scale-90", "opacity-0");
    setTimeout(() => {
      modal.classList.add("hidden");
      document.body.style.overflow = "";
    }, 300);
  }

  modal.addEventListener("click", (e) => {
    if (!modalContent.contains(e.target)) closeModal();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !modal.classList.contains("hidden")) {
      closeModal();
    }
  });

  // Initial transition setup
  registerFields.classList.add(
    "transition-all",
    "duration-500",
    "ease-in-out",
    "overflow-hidden"
  );

  window.toggleForm = function (mode) {
    authMode.value = mode;

    if (mode === "signup") {
      submitBtn.textContent = "Sign Up";
      registerFields.classList.remove("max-h-0", "opacity-0");
      registerFields.classList.add("max-h-[500px]", "opacity-100");

      signUpBtn.classList.add("text-blue-600", "font-semibold");
      signUpBtn.classList.remove("text-gray-500");

      signInBtn.classList.remove("text-blue-600", "font-semibold");
      signInBtn.classList.add("text-gray-500");
    } else {
      submitBtn.textContent = "Login";
      registerFields.classList.remove("max-h-[500px]", "opacity-100");
      registerFields.classList.add("max-h-0", "opacity-0");

      signInBtn.classList.add("text-blue-600", "font-semibold");
      signInBtn.classList.remove("text-gray-500");

      signUpBtn.classList.remove("text-blue-600", "font-semibold");
      signUpBtn.classList.add("text-gray-500");
    }
  };

  signInBtn.addEventListener("click", () => toggleForm("signin"));
  signUpBtn.addEventListener("click", () => toggleForm("signup"));
  // Hide error message when user starts typing again
  ["student_id", "password", "name", "email", "phone_number"].forEach((id) => {
    const input = document.getElementById(id);
    if (input) {
      input.addEventListener("input", () => {
        errorDisplay.classList.add("hidden");
        errorDisplay.textContent = "";
      });
    }
  });

  submitBtn.addEventListener("click", (e) => {
    e.preventDefault();

    const student_id = document.getElementById("student_id").value.trim();
    const password = document.getElementById("password").value.trim();
    const name = document.getElementById("name")?.value?.trim();
    const email = document.getElementById("email")?.value?.trim();
    const phone_number = document.getElementById("phone_number")?.value?.trim();
    const mode = authMode.value;
    const csrftoken = getCookie("csrftoken");

    // Validate input
    if (!student_id || !password) {
      return showError("Student ID and Password are required.");
    }

    if (mode === "signup" && (!name || !email || !phone_number)) {
      showError("All registration fields are required.");
      return;
    }

    const payload = {
      student_id,
      password,
      mode,
      ...(mode === "signup" && { name, email, phone_number }),
    };
    if (mode == "signin") {
      submitBtn.textContent = "Logging in...";
      submitBtn.disabled = true;
    } else {
      submitBtn.textContent = "Signing Up...";
      submitBtn.disabled = true;
    }

    fetch("/student_auth", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify(payload),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          localStorage.setItem("student_id", student_id);
          window.location.href = "/my_account";
        } else {
          showError(data.message || "An error occurred.");
          return;
        }
      })
      .catch((err) => {
        console.error(err);
        showError("Something went wrong. Try again.");
      });
  });

  function showError(message) {
    errorDisplay.textContent = message;
    errorDisplay.classList.remove("hidden");
    submitBtn.textContent = "Submit";
    submitBtn.disabled = false;
  }
});
