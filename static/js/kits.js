import { getCookie } from "/static/js/utils.js";

document.addEventListener("DOMContentLoaded", function () {
  const signInBtn = document.getElementById("sign_in");
  const signUpBtn = document.getElementById("sign_up");
  const registerFields = document.getElementById("register_fields");
  const authMode = document.getElementById("auth_mode");

  if (!signInBtn || !signUpBtn || !registerFields || !authMode) return;

  // Set initial styles
  registerFields.classList.add(
    "transition-all",
    "duration-500",
    "ease-in-out",
    "overflow-hidden"
  );

  window.toggleForm = function (mode) {
    authMode.value = mode;

    if (mode === "signup") {
      registerFields.style.display = "block";

      signUpBtn.classList.add("text-blue-600", "font-semibold");
      signUpBtn.classList.remove("text-gray-500");

      signInBtn.classList.remove("text-blue-600", "font-semibold");
      signInBtn.classList.add("text-gray-500");
    } else {
      registerFields.style.display = "none";

      signInBtn.classList.add("text-blue-600", "font-semibold");
      signInBtn.classList.remove("text-gray-500");

      signUpBtn.classList.remove("text-blue-600", "font-semibold");
      signUpBtn.classList.add("text-gray-500");
    }
  };

  // Bind click handlers
  signInBtn.addEventListener("click", () => toggleForm("signin"));
  signUpBtn.addEventListener("click", () => toggleForm("signup"));
});
