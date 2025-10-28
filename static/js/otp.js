import { showToast } from "./utils.js";
import { csrfFetch } from "./api.js";
document.addEventListener("DOMContentLoaded", function () {
  const inputs = document.querySelectorAll(".otp-input");

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

  document.getElementById("verifyOtpBtn")?.addEventListener("click", (e) => {
    e.preventDefault();
    const otp = Array.from(inputs)
      .map((input) => input.value)
      .join("");
    if (otp.length < 6) {
      showToast("Invalid OTP", "Please enter a 6-digit OTP.");
    } else {
      const response = csrfFetch("/verify_otp", {
        method: "POST",
        body: JSON.stringify({ otp }),
      });
      console.log(response);
      if (response) {
        window.location.href = "/my_account";
      }
    }
  });
});
