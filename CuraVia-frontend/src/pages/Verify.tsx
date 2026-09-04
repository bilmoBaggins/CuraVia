import React, { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import api from "../api";

type VerifyResponse = {
  message?: string;
  detail?: string;
};

const VerifyEmail: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [message, setMessage] = useState<string>("Verifying...");
  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading",
  );
  const [showResend, setShowResend] = useState<boolean>(false);
  const [email, setEmail] = useState<string>("");
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    const token = searchParams.get("token");
    if (!token) {
      setMessage("No token found in URL.");
      setStatus("error");
      setShowResend(true);
      return;
    }

    const verifyEmail = async () => {
      setError("");
      setSuccess("");
      try {
        const response = await api.get(
          `/verify?token=${token}&email=${searchParams.get("email")}`,
        );
        const data: VerifyResponse = response.data;

        if (response.data && response.data.message) {
          setMessage(response.data.message || "Email verified successfully!");
          setSuccess(response.data.message);
          setStatus("success");
          setTimeout(() => {
            navigate("/login");
          }, 3000);
        } else if (response.data && response.data.error) {
          setMessage(response.data.error || "Verification failed.");
          setError(response.data.error);
          setStatus("error");
          setShowResend(true);
          setEmail(searchParams.get("email") || "");
        } else {
          setMessage(response.data.error || "Verification failed.");
          setError(response.data.error);
          setStatus("error");
          setShowResend(true);
          setEmail(searchParams.get("email") || "");
        }
      } catch (err: any) {
        if (err.response && err.response.data && err.response.data.error) {
          setMessage(err.response.data.error);
          setError(err.response.data.error);
          setStatus("error");
          setShowResend(true);
        } else {
          setMessage(err.response.data.error || "Verification failed.");
          setError(err.response.data.error);
          setStatus("error");
          setShowResend(true);
        }
      }
    };

    verifyEmail();
  }, [searchParams, navigate]);

  const handleResend = async () => {
    if (!email) {
      setMessage("No email available to resend verification.");
      return;
    }

    try {
      const response = await api.post("/send-verification-email", { email });
      const data: VerifyResponse = response.data;
      setMessage(data.message || "Verification email resent!");
      setSuccess(response.data.message);
      setStatus("success");
      setShowResend(false);
    } catch (error) {
      setMessage("Failed to resend verification email.");
      setError((error as any).response.data.error);
      setStatus("error");
      console.error(error);
    }
  };

  const getColor = () => {
    if (status === "success") return "green";
    if (status === "error") return "red";
    return "black";
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        backgroundColor: "#f0f2f5",
      }}
    >
      <div
        style={{
          padding: "40px",
          backgroundColor: "white",
          borderRadius: "12px",
          boxShadow: "0 4px 20px rgba(0,0,0,0.1)",
          textAlign: "center",
          width: "90%",
          maxWidth: "400px",
        }}
      >
        <h1>Email Verification</h1>
        {status === "loading" && (
          <div style={{ margin: "20px 0" }}>
            <div className="spinner" />
            <p>Verifying your email...</p>
          </div>
        )}
        <p style={{ color: getColor(), fontWeight: "bold", marginTop: "20px" }}>
          {message}
        </p>

        {showResend && (
          <button
            onClick={handleResend}
            style={{
              marginTop: "20px",
              padding: "10px 20px",
              backgroundColor: "#3498db",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
            }}
          >
            Resend Verification Email
          </button>
        )}
      </div>
      <style>
        {`
          .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
          }
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

export default VerifyEmail;
