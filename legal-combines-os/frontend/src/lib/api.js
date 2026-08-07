const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class APIError extends Error {
  constructor(message, status, detail) {
    super(message);
    this.name = "APIError";
    this.status = status;
    this.detail = detail;
  }
}

async function handleResponse(response) {
  const data = await response.json();

  if (!response.ok) {
    const error = new APIError(
      data.detail || `Request failed with status ${response.status}`,
      response.status,
      data.detail
    );
    throw error;
  }

  return data;
}

function getHeaders() {
  const headers = {
    "Content-Type": "application/json",
  };

  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  return headers;
}

export const authAPI = {
  async login({ email, password }) {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    return handleResponse(response);
  },

  async register(userData) {
    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(userData),
    });
    return handleResponse(response);
  },

  async logout() {
    const response = await fetch(`${API_BASE_URL}/api/auth/logout`, {
      method: "POST",
      headers: getHeaders(),
    });
    return handleResponse(response);
  },

  async verifyOTP(userId, otp) {
    const response = await fetch(`${API_BASE_URL}/api/auth/otp/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, otp }),
    });
    return handleResponse(response);
  },

  async initOTP(email) {
    const response = await fetch(`${API_BASE_URL}/api/auth/otp/init`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    return handleResponse(response);
  },

  async resendOTP(email) {
    const response = await fetch(`${API_BASE_URL}/api/auth/otp/resend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    return handleResponse(response);
  },

  async refresh(refreshToken) {
    const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    return handleResponse(response);
  },

  async me() {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      method: "GET",
      headers: getHeaders(),
    });
    return handleResponse(response);
  },

  async changePassword(oldPassword, newPassword) {
    const response = await fetch(`${API_BASE_URL}/api/auth/password/change`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({
        old_password: oldPassword,
        new_password: newPassword,
      }),
    });
    return handleResponse(response);
  },

  async requestPasswordReset(email) {
    const response = await fetch(`${API_BASE_URL}/api/auth/password/reset`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    return handleResponse(response);
  },

  async getOTPSetupQR() {
    const response = await fetch(`${API_BASE_URL}/api/auth/otp/setup-qr`, {
      method: "GET",
      headers: getHeaders(),
    });
    return handleResponse(response);
  },
};

export const isAuthenticated = () => {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("access_token");
};

export const getCurrentUser = () => {
  if (typeof window === "undefined") return null;
  const user = localStorage.getItem("user");
  return user ? JSON.parse(user) : null;
};

export const logout = () => {
  if (typeof window !== "undefined") {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
  }
};

export async function loadRazorpay() {
  if (typeof window === "undefined") return null;

  return new Promise((resolve) => {
    if (window.Razorpay) {
      resolve(window.Razorpay);
      return;
    }

    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.onload = () => {
      resolve(window.Razorpay);
    };
    script.onerror = () => {
      console.error("Failed to load Razorpay SDK");
      resolve(null);
    };
    document.body.appendChild(script);
  });
}

export const paymentAPI = {
  async getPlans() {
    const response = await fetch(`${API_BASE_URL}/api/payments/plans`, {
      headers: getHeaders(),
    });
    return handleResponse(response);
  },

  async getPlan(planId) {
    const response = await fetch(`${API_BASE_URL}/api/payments/plans/${planId}`, {
      headers: getHeaders(),
    });
    return handleResponse(response);
  },

  async getCurrentSubscription() {
    const response = await fetch(`${API_BASE_URL}/api/payments/subscriptions/current`, {
      headers: getHeaders(),
    });
    return handleResponse(response);
  },

  async cancelSubscription(immediate = false) {
    const response = await fetch(`${API_BASE_URL}/api/payments/subscriptions/cancel`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ immediate }),
    });
    return handleResponse(response);
  },

  async reactivateSubscription() {
    const response = await fetch(`${API_BASE_URL}/api/payments/subscriptions/reactivate`, {
      method: "POST",
      headers: getHeaders(),
    });
    return handleResponse(response);
  },

  async upgradeSubscription(planId) {
    const response = await fetch(`${API_BASE_URL}/api/payments/subscriptions/upgrade`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ plan_id: planId }),
    });
    return handleResponse(response);
  },

  async getPaymentHistory() {
    const response = await fetch(`${API_BASE_URL}/api/payments/history`, {
      headers: getHeaders(),
    });
    return handleResponse(response);
  },
};
