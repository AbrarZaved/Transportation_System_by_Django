document.addEventListener("DOMContentLoaded", function () {
  const hamburger = document.getElementById("hamburgerBtn");
  const mobileMenu = document.getElementById("mobileMenu");
  const modal = document.getElementById("customModal");
  const modalContent = document.getElementById("modalContent");
  const signInBtn = document.getElementById("signInBtn");
  const signUpBtn = document.getElementById("signUpBtn");
  const signInForm = document.getElementById("signInForm");
  const signUpForm = document.getElementById("signUpForm");
  if (signInBtn) {
    localStorage.clear();
  }
  /* --- Modal Controls --- */
  function openModal() {
    modal.classList.remove("hidden");
    setTimeout(() => {
      modalContent.classList.remove("scale-90", "opacity-0");
      modalContent.classList.add("scale-100", "opacity-100");
      const firstInput = modal.querySelector("form:not(.hidden) input");
      firstInput?.focus();
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
    if (e.key === "Escape" && !modal.classList.contains("hidden")) closeModal();
  });

  /* --- Open Modal Buttons --- */
  ["sign_in_desktop", "sign_in_mobile"].forEach((id) => {
    const btn = document.getElementById(id);
    btn?.addEventListener("click", () => {
      if (hamburger && mobileMenu.classList.contains("open")) {
        hamburger.classList.remove("active");
        mobileMenu.classList.remove("open");
      }
      openModal();
    });
  });

  // Handle login buttons with class-based selection
  document.querySelectorAll(".login-button").forEach((btn) => {
    btn?.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (hamburger && mobileMenu.classList.contains("open")) {
        hamburger.classList.remove("active");
        mobileMenu.classList.remove("open");
      }
      openModal();
    });
  });

  /* --- Hamburger --- */
  hamburger?.addEventListener("click", () => {
    hamburger.classList.toggle("active");
    mobileMenu.classList.toggle("open");
  });

  /* --- Smooth Form Toggle with Tailwind --- */
  function switchTo(mode) {
    if (mode === "signin") {
      signInBtn.classList.add("text-blue-600", "border-b-2", "border-blue-600");
      signUpBtn.classList.remove(
        "text-blue-600",
        "border-b-2",
        "border-blue-600"
      );
      signUpBtn.classList.add("text-gray-500");

      // Animate Sign Up → Sign In
      signUpForm.classList.add("opacity-0", "scale-95");
      setTimeout(() => {
        signUpForm.classList.add("hidden");
        signInForm.classList.remove("hidden");
        setTimeout(() => {
          signInForm.classList.remove("opacity-0", "scale-95");
          signInForm.classList.add("opacity-100", "scale-100");
        }, 20);
      }, 200);
    } else {
      signUpBtn.classList.add("text-blue-600", "border-b-2", "border-blue-600");
      signInBtn.classList.remove(
        "text-blue-600",
        "border-b-2",
        "border-blue-600"
      );
      signInBtn.classList.add("text-gray-500");

      // Animate Sign In → Sign Up
      signInForm.classList.add("opacity-0", "scale-95");
      setTimeout(() => {
        signInForm.classList.add("hidden");
        signUpForm.classList.remove("hidden");
        setTimeout(() => {
          signUpForm.classList.remove("opacity-0", "scale-95");
          signUpForm.classList.add("opacity-100", "scale-100");
        }, 20);
      }, 200);
    }

    setTimeout(() => {
      const visibleForm = document.querySelector("form:not(.hidden) input");
      visibleForm?.focus();
    }, 400);
  }
  switchTo("signin");
  signInBtn.addEventListener("click", () => switchTo("signin"));
  signUpBtn.addEventListener("click", () => switchTo("signup"));

  /* --- Password Toggle Functionality --- */
  const toggleLoginPassword = document.getElementById("toggleLoginPassword");
  const loginPassword = document.getElementById("loginPassword");
  const showLoginIcon = document.getElementById("showLoginIcon");
  const hideLoginIcon = document.getElementById("hideLoginIcon");

  const toggleRegisterPassword = document.getElementById(
    "toggleRegisterPassword"
  );
  const registerPassword = document.getElementById("registerPassword");
  const showRegisterIcon = document.getElementById("showRegisterIcon");
  const hideRegisterIcon = document.getElementById("hideRegisterIcon");

  // Login password toggle
  if (toggleLoginPassword) {
    toggleLoginPassword.addEventListener("click", function () {
      const type =
        loginPassword.getAttribute("type") === "password" ? "text" : "password";
      loginPassword.setAttribute("type", type);

      if (type === "text") {
        showLoginIcon.classList.add("hidden");
        hideLoginIcon.classList.remove("hidden");
      } else {
        showLoginIcon.classList.remove("hidden");
        hideLoginIcon.classList.add("hidden");
      }
    });
  }

  // Register password toggle
  if (toggleRegisterPassword) {
    toggleRegisterPassword.addEventListener("click", function () {
      const type =
        registerPassword.getAttribute("type") === "password"
          ? "text"
          : "password";
      registerPassword.setAttribute("type", type);

      if (type === "text") {
        showRegisterIcon.classList.add("hidden");
        hideRegisterIcon.classList.remove("hidden");
      } else {
        showRegisterIcon.classList.remove("hidden");
        hideRegisterIcon.classList.add("hidden");
      }
    });
  }

  /* --- Password Strength Validation --- */
  if (registerPassword) {
    const passwordStrength = document.getElementById("passwordStrength");

    registerPassword.addEventListener("input", function () {
      const password = this.value;
      const submitBtn = document.querySelector(
        '#signUpForm button[type="submit"]'
      );

      if (password.length > 0 && password.length < 6) {
        this.classList.add("border-red-500");
        this.classList.remove("border-green-500");
        passwordStrength.classList.remove("hidden");
        passwordStrength.innerHTML =
          '<span class="text-red-500">Password must be at least 6 characters long</span>';
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.classList.add("opacity-50", "cursor-not-allowed");
        }
      } else if (password.length >= 6) {
        this.classList.remove("border-red-500");
        this.classList.add("border-green-500");
        passwordStrength.innerHTML =
          '<span class="text-green-500">Password strength: Good</span>';
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.classList.remove("opacity-50", "cursor-not-allowed");
        }
      } else {
        this.classList.remove("border-red-500", "border-green-500");
        passwordStrength.classList.add("hidden");
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.classList.remove("opacity-50", "cursor-not-allowed");
        }
      }
    });
  }

  /* --- Form Validation --- */
  if (signInForm) {
    signInForm.addEventListener("submit", function (e) {
      const studentId = this.querySelector(
        'input[name="student_id"]'
      ).value.trim();
      const password = this.querySelector(
        'input[name="password"]'
      ).value.trim();

      if (!studentId || !password) {
        e.preventDefault();
        alert("Please fill in all fields");
        return false;
      }
    });
  }

  if (signUpForm) {
    signUpForm.addEventListener("submit", function (e) {
      const inputs = this.querySelectorAll("input[required]");
      let isValid = true;

      inputs.forEach((input) => {
        if (!input.value.trim()) {
          isValid = false;
          input.classList.add("border-red-500");
        } else {
          input.classList.remove("border-red-500");
        }
      });

      if (!isValid) {
        e.preventDefault();
        alert("Please fill in all required fields");
        return false;
      }

      const password = this.querySelector('input[name="password"]').value;
      if (password.length < 6) {
        e.preventDefault();
        alert("Password must be at least 6 characters long");
        return false;
      }
    });
  }

  /* --- Hide Error Messages When Typing --- */
  ["student_id", "password", "name", "email", "phone_number"].forEach((id) => {
    document.querySelectorAll(`[name="${id}"]`).forEach((input) => {
      input.addEventListener("input", () => {
        const errorDisplay = document.getElementById("student-id-error");
        if (errorDisplay) {
          errorDisplay.classList.add("hidden");
          errorDisplay.textContent = "";
        }
      });
    });
  });
});
