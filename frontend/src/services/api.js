import API_BASE_URL from "../config/api";

async function apiRequest(endpoint, options = {}) {
  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    options
  );

  if (!response.ok) {
    let message = `API request failed: ${response.status}`;

    try {
      const errorData = await response.json();

      if (errorData?.message) {
        message = errorData.message;
      }

      if (errorData?.detail) {
        message = errorData.detail;
      }
    } catch {
      // Keep default error message
    }

    throw new Error(message);
  }

  return await response.json();
}


// ============================================================
// SYSTEM
// ============================================================

export async function getHealth() {
  return apiRequest("/health");
}

export async function getAnalysis() {
  return apiRequest("/analysis");
}


// ============================================================
// PROCESS / BOTTLENECK
// ============================================================

export async function getProcess() {
  return apiRequest("/process");
}

export async function getBottleneck() {
  return apiRequest("/bottleneck");
}


// ============================================================
// ROOT CAUSE
// ============================================================

export async function getRootCause() {
  return apiRequest("/root-cause");
}


// ============================================================
// PRODUCTION / ECONOMICS
// ============================================================

export async function getProduction() {
  return apiRequest("/production");
}

export async function getImpact() {
  return apiRequest("/impact");
}


// ============================================================
// VISION INSPECTION
// ============================================================

export async function runInspection(file) {
  const formData = new FormData();

  formData.append("file", file);

  return apiRequest("/inspection", {
    method: "POST",
    body: formData,
  });
}


// ============================================================
// SIMULATION
// ============================================================

export async function runSimulation(payload) {
  return apiRequest("/simulation", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export async function loginEmployee(employeeId, password) {
  return apiRequest("/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      employee_id: employeeId,
      password,
    }),
  });
}