import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api";

export default function Login() {
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showForgot, setShowForgot] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showResend, setShowResend] = useState(false);
  const [resendEmail, setResendEmail] = useState("");
  const [countdown, setCountdown] = useState(0);
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setShowForgot(false);
    setLoading(true);
    try {
      const response = await api.post("/login", form);

      if (response.data && response.data.message === "Login successful.") {
        setSuccess("Login successful!");
        if (response.data.access_token) {
          localStorage.setItem("token", response.data.access_token);
          localStorage.setItem("user", JSON.stringify(response.data.user));
          setTimeout(() => {
            navigate("/main");
          }, 1000);
        }
      } else if (response.data && response.data.error) {
        setError(response.data.error);
        if (
          response.data.status === 403 &&
          response.data.resend_verification &&
          response.data.email
        ) {
          setShowResend(true);
          setResendEmail(response.data.email);
        } else {
          setShowResend(false);
          setShowForgot(true);
        }
      } else {
        setError("Login failed.");
        setShowResend(false);
      }
    } catch (err: any) {
      setError(err?.response?.data?.error || "Login failed.");
      setShowForgot(true);
    }
    setLoading(false);
  };

  const handleForgotPassword = async () => {
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      await api.post("/forgot-password", { username: form.username });
      setSuccess("Password reset email sent!");
    } catch (err: any) {
      setError(err?.response?.data?.error || "Failed to send reset email.");
    }
    setLoading(false);
  };

  const handleResendVerification = async () => {
    if (!resendEmail) return;
    // Get username from form or localStorage
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    const username = user.username || form.username;
    try {
      const response = await api.post("/resend-verification-email", {
        email: resendEmail,
        username,
      });
      const data = response.data;
      setSuccess(data.message || "Verification email resent!");
      setShowResend(false);
      setCountdown(60);
      setTimeout(() => setSuccess(""), 5000);
      // Start countdown timer
      let seconds = 60;
      const interval = setInterval(() => {
        seconds -= 1;
        setCountdown(seconds);
        if (seconds <= 0) {
          clearInterval(interval);
          setShowResend(true);
        }
      }, 1000);
    } catch (error: any) {
      setError(error?.response?.data?.error || "Error sending request.");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-white px-4">
      <div className="w-full max-w-md bg-white shadow p-6 rounded-lg">
        <h2 className="text-2xl font-bold text-center mb-6">
          Login to CuraVia
        </h2>
        <form onSubmit={handleLogin}>
          <input
            type="text"
            name="username"
            placeholder="Username"
            value={form.username}
            onChange={handleChange}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 mb-4"
            required
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={form.password}
            onChange={handleChange}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 mb-6"
            required
          />
          {error && (
            <div className="text-red-500 text-sm mb-2 text-center">{error}</div>
          )}
          {success && (
            <div className="text-green-500 text-sm mb-2 text-center">
              {success}
            </div>
          )}
          {showResend && (
            <div className="flex flex-col items-center gap-2 mt-2 mb-4">
              <button
                type="button"
                className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
                onClick={handleResendVerification}
              >
                Resend Verification Email
              </button>
            </div>
          )}
          {countdown > 0 && (
            <div className="flex flex-col items-center gap-2 mb-4">
              <span className="text-gray-600 font-semibold text-sm">
                You can resend in {countdown} seconds
              </span>
            </div>
          )}
          <div className="flex flex-col items-center gap-2 mb-2">
            {showForgot && (
              <button
                onClick={handleForgotPassword}
                className="text-blue-600 hover:underline"
              >
                Forgot Password?
              </button>
            )}
          </div>
          <button
            className="w-full bg-blue-600 text-white rounded-lg py-2 font-semibold"
            type="submit"
            disabled={loading}
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
        <p className="text-center text-sm text-gray-500 mt-4">
          Don't have an account?{" "}
          <Link to="/signup" className="text-blue-600 hover:underline">
            Sign up
          </Link>
        </p>
        <p className="text-center text-sm text-gray-500 mt-4">
          Or{" "}
          <Link to="/main" className="text-blue-600 hover:underline">
            enter as Guest
          </Link>
        </p>
      </div>
    </div>
  );
}
