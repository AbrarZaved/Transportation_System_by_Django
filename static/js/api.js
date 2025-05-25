import { getCookie } from "/static/js/utils.js";

export async function csrfFetch(url, options = {}) {
  const csrftoken = getCookie("csrftoken");

  const defaultHeaders = {
    "Content-Type": "application/json",
    "X-CSRFToken": csrftoken,
  };

  options.headers = {
    ...defaultHeaders,
    ...(options.headers || {}),
  };

  const response = await fetch(url, options);
  return response.json();
}
