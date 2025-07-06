import { getCookie } from "/static/js/utils.js";
function getCSRFToken() {
  const cookies = document.cookie.split(";");
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split("=");
    if (name === "csrftoken") return decodeURIComponent(value);
  }
  return null;
}
export async function csrfFetch(url, options = {}) {
  const csrftoken = getCookie("csrftoken");

  const defaultHeaders = {
    "Content-Type": "application/json",
    "X-CSRFToken": getCSRFToken(),
  };

  options.headers = {
    ...defaultHeaders,
    ...(options.headers || {}),
  };

  const response = await fetch(url, options);
  return response.json();
}
