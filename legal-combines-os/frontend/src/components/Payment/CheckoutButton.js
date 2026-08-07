"use client";

import { useState, useEffect } from "react";
import { loadRazorpay } from "@/lib/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function CheckoutButton({ planId, planName, amount, onSuccess, onError }) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePayment = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        throw new Error("Please login to subscribe");
      }

      const orderResponse = await fetch(`${API_BASE_URL}/api/payments/subscriptions/create-order`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ plan_id: planId }),
      });

      if (!orderResponse.ok) {
        const errorData = await orderResponse.json();
        throw new Error(errorData.detail || "Failed to create order");
      }

      const orderData = await orderResponse.json();

      const razorpay = await loadRazorpay();

      const options = {
        key: orderData.key_id,
        amount: orderData.amount,
        currency: orderData.currency,
        name: "Legal Combines OS",
        description: `Subscription to ${planName}`,
        order_id: orderData.order_id,
        prefill: {
          name: JSON.parse(localStorage.getItem("user") || "{}").full_name || "",
          email: JSON.parse(localStorage.getItem("user") || "{}").email || "",
        },
        theme: {
          color: "#2563eb",
        },
        handler: async function (response) {
          try {
            const confirmResponse = await fetch(`${API_BASE_URL}/api/payments/subscriptions/confirm`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
              },
              body: JSON.stringify({
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_order_id: response.razorpay_order_id,
              }),
            });

            if (!confirmResponse.ok) {
              throw new Error("Failed to confirm subscription");
            }

            const confirmData = await confirmResponse.json();
            
            if (onSuccess) {
              onSuccess(confirmData);
            }

            localStorage.setItem("subscription", JSON.stringify(confirmData.subscription));
          } catch (err) {
            if (onError) {
              onError(err);
            }
            setError("Payment successful but failed to confirm subscription. Please contact support.");
          }
        },
        modal: {
          ondismiss: function () {
            setIsLoading(false);
          },
        },
      };

      const rzp = new razorpay(options);
      rzp.on("payment.failed", function (response) {
        setError(response.error.description || "Payment failed");
        if (onError) {
          onError(new Error(response.error.description));
        }
      });

      rzp.open();
    } catch (err) {
      setError(err.message || "An error occurred");
      if (onError) {
        onError(err);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full">
      <button
        onClick={handlePayment}
        disabled={isLoading}
        className={`w-full py-3 px-4 rounded-lg font-semibold text-white transition-all ${
          isLoading
            ? "bg-blue-400 cursor-not-allowed"
            : "bg-blue-600 hover:bg-blue-700 shadow-lg hover:shadow-xl"
        }`}
      >
        {isLoading ? (
          <span className="flex items-center justify-center">
            <svg
              className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            Processing...
          </span>
        ) : (
          `Subscribe Now - ₹${amount}`
        )}
      </button>
      {error && (
        <p className="mt-2 text-sm text-red-600 text-center">{error}</p>
      )}
    </div>
  );
}
