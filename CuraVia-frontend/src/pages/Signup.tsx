import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api";

export default function Signup() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    firstName: "",
    lastName: "",
    username: "",
    email: "",
    password: "",
    retypePassword: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    if (form.password !== form.retypePassword) {
      setError("Passwords do not match.");
      return;
    }
    setLoading(true);
    try {
      const response = await api.post("/signup", {
        username: form.username,
        password: form.password,
        first_name: form.firstName,
        last_name: form.lastName,
        email: form.email,
        location: null,
      });

      if (response.data && response.data.message) {
          setSuccess(
            "Signup successful! Please check your email for a verification link."
          );
          setForm({
            firstName: "",
            lastName: "",
            username: "",
            email: "",
            password: "",
            retypePassword: "",
          });
      } else if (response.data && response.data.error) {
        setError(response.data.error);
      } else {
        setError("Signup failed.");
      }
    } catch (err: any) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError("Signup failed.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-white px-4">
      <div className="w-full max-w-md bg-white shadow p-6 rounded-lg">
        <h2 className="text-2xl font-bold text-center mb-6">
          Sign Up for CuraVia
        </h2>
        <form onSubmit={handleSubmit}>
          <div className="flex gap-4 mb-4">
            <input
              type="text"
              name="firstName"
              placeholder="First Name"
              value={form.firstName}
              onChange={handleChange}
              className="w-1/2 border border-gray-300 rounded-lg px-4 py-2"
            />
            <input
              type="text"
              name="lastName"
              placeholder="Last Name"
              value={form.lastName}
              onChange={handleChange}
              className="w-1/2 border border-gray-300 rounded-lg px-4 py-2"
            />
          </div>
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
            type="email"
            name="email"
            placeholder="Email"
            value={form.email}
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
            className="w-full border border-gray-300 rounded-lg px-4 py-2 mb-4"
            required
          />
          <input
            type="password"
            name="retypePassword"
            placeholder="Retype Password"
            value={form.retypePassword}
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
          <button
            className="w-full bg-blue-600 text-white rounded-lg py-2 font-semibold"
            type="submit"
            disabled={loading}
          >
            {loading ? "Signing Up..." : "Sign Up"}
          </button>
        </form>
        <p className="text-center text-sm text-gray-500 mt-4">
          Already have an account?{" "}
          <Link to="/login" className="text-blue-600 hover:underline">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}
