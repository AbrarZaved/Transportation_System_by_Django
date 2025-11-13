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
  ["sign_in_desktop", "sign_in_mobile", "login-button"].forEach((id) => {
    const btn = document.getElementById(id);
    btn?.addEventListener("click", () => {
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
