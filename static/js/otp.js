import { showToast } from "./utils.js";
import { csrfFetch } from "./api.js";
document.addEventListener("DOMContentLoaded", function () {
  const inputs = document.querySelectorAll(".otp-input");
  showToast("Info", "Please enter the 6-digit OTP sent to your email.");
  inputs.forEach((input, index) => {
    input.addEventListener("input", (e) => {
      const value = e.target.value;
      if (/[^0-9]/.test(value)) {
        e.target.value = ""; // allow only digits
        return;
      }
      if (value && index < inputs.length - 1) {
        inputs[index + 1].focus();
      }
    });

    input.addEventListener("keydown", (e) => {
      if (e.key === "Backspace" && !input.value && index > 0) {
        inputs[index - 1].focus();
      }
    });

    input.addEventListener("paste", (e) => {
      e.preventDefault();
      const pasteData = e.clipboardData.getData("text").trim().split("");
      pasteData.forEach((char, i) => {
        if (inputs[index + i]) inputs[index + i].value = char;
      });
      const nextIndex = Math.min(index + pasteData.length, inputs.length - 1);
      inputs[nextIndex].focus();
    });
  });

  inputs[0].focus();

  document
    .getElementById("verifyOtpBtn")
    ?.addEventListener("click", async (e) => {
      e.preventDefault();
      const otp = Array.from(inputs)
        .map((input) => input.value)
        .join("");
      if (otp.length < 6) {
        showToast("Invalid OTP", "Please enter a 6-digit OTP.");
      } else {
        try {
          const response = await csrfFetch("/verify_otp", {
            method: "POST",
            body: JSON.stringify({ otp }),
          });
          if (response) {
            // Wait a moment for session to be set, then redirect
            setTimeout(() => {
              window.location.href = `${window.location.origin}`;
            }, 100);
          } else {
            showToast("Invalid OTP", data.message || "Please try again.");
          }
        } catch (error) {
          console.error("OTP verification error:", error);
          showToast("Error", "Something went wrong. Please try again.");
        }
      }
    });

  // Resend OTP functionality
  document
    .getElementById("resendOtpBtn")
    ?.addEventListener("click", async (e) => {
      e.preventDefault();
      const resendBtn = e.target;
      const originalText = resendBtn.textContent;

      // Disable button and show loading state
      resendBtn.textContent = "Sending...";
      resendBtn.classList.add("opacity-50", "cursor-not-allowed");
      resendBtn.style.pointerEvents = "none";

      try {
        const response = await csrfFetch("/resend_otp", {
          method: "POST",
        });

       

        if (response) {
          showToast("Success", response.message || "New OTP sent successfully!");

          // Clear all OTP inputs
          inputs.forEach((input) => (input.value = ""));
          inputs[0].focus();

          // Start countdown timer (60 seconds)
          let countdown = 60;
          const updateTimer = () => {
            if (countdown > 0) {
              resendBtn.textContent = `Resend (${countdown}s)`;
              countdown--;
              setTimeout(updateTimer, 1000);
            } else {
              resendBtn.textContent = originalText;
              resendBtn.classList.remove("opacity-50", "cursor-not-allowed");
              resendBtn.style.pointerEvents = "auto";
            }
          };
          updateTimer();
        } else {
          showToast(
            "Error",
            data.message || "Failed to resend OTP. Please try again."
          );
          resendBtn.textContent = originalText;
          resendBtn.classList.remove("opacity-50", "cursor-not-allowed");
          resendBtn.style.pointerEvents = "auto";
        }
      } catch (error) {
        console.error("Resend OTP error:", error);
        showToast("Error", "Something went wrong. Please try again.");
        resendBtn.textContent = originalText;
        resendBtn.classList.remove("opacity-50", "cursor-not-allowed");
        resendBtn.style.pointerEvents = "auto";
      }
    });
});
