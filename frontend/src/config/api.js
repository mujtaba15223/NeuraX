const API_BASE_URL = (
  import.meta.env.VITE_API_URL ||
  "http://localhost:8080"
).replace(/\/$/, "");

export default API_BASE_URL;