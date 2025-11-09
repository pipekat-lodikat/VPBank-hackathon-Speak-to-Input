import { useState } from "react";
import {
  LogIn,
  UserPlus,
  HelpCircle,
  KeyRound,
  Eye,
  EyeOff,
} from "lucide-react";
import icon from "../icon.png";
import { API_ENDPOINTS } from "../config/api";

interface LoginProps {
  onLoginSuccess: (tokens: {
    access_token: string;
    id_token: string;
    refresh_token: string;
  }) => void;
}

export default function Login({ onLoginSuccess }: LoginProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Modal states
  const [showRegister, setShowRegister] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [showSupport, setShowSupport] = useState(false);

  // Register form state
  const [regUsername, setRegUsername] = useState("");
  const [regEmail, setRegEmail] = useState("");
  const [regPhone, setRegPhone] = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [regConfirmPassword, setRegConfirmPassword] = useState("");
  const [regLoading, setRegLoading] = useState(false);
  const [regError, setRegError] = useState("");
  const [regSuccess, setRegSuccess] = useState("");

  // Forgot password state
  const [forgotStep, setForgotStep] = useState(1); // 1: nhập email, 2: nhập code + password mới
  const [forgotEmail, setForgotEmail] = useState("");
  const [forgotCode, setForgotCode] = useState("");
  const [forgotNewPassword, setForgotNewPassword] = useState("");
  const [forgotConfirmPassword, setForgotConfirmPassword] = useState("");
  const [forgotLoading, setForgotLoading] = useState(false);
  const [forgotError, setForgotError] = useState("");
  const [forgotSuccess, setForgotSuccess] = useState("");

  // Format phone number: +84389876420 -> 0389876420
  const formatPhoneNumber = (phone: string): string => {
    if (!phone) return phone;

    // Remove all spaces and special characters except +
    let cleaned = phone.replace(/[\s\-()]/g, "");

    // Convert +84 to 0
    if (cleaned.startsWith("+84")) {
      cleaned = "0" + cleaned.substring(3);
    }

    return cleaned;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch(API_ENDPOINTS.AUTH.LOGIN, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (data.success) {
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("id_token", data.id_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        onLoginSuccess(data);
      } else {
        setError(data.message || "Login failed");
      }
    } catch (err) {
      setError("Network error. Please try again.");
      console.error("Login error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setRegLoading(true);
    setRegError("");
    setRegSuccess("");

    // Validation
    if (regPassword !== regConfirmPassword) {
      setRegError("Passwords do not match");
      setRegLoading(false);
      return;
    }

    if (regPassword.length < 8) {
      setRegError("Password must be at least 8 characters");
      setRegLoading(false);
      return;
    }

    try {
      const response = await fetch(API_ENDPOINTS.AUTH.REGISTER, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: regUsername,
          password: regPassword,
          email: regEmail,
          phone_number: formatPhoneNumber(regPhone),
          name: regUsername,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setRegSuccess("Registration successful! You can login now.");
        // Clear form
        setRegUsername("");
        setRegEmail("");
        setRegPhone("");
        setRegPassword("");
        setRegConfirmPassword("");
        // Auto close modal after 2 seconds
        setTimeout(() => {
          setShowRegister(false);
          setRegSuccess("");
        }, 2000);
      } else {
        setRegError(data.message || "Registration failed");
      }
    } catch (err) {
      setRegError("Network error. Please try again.");
      console.error("Register error:", err);
    } finally {
      setRegLoading(false);
    }
  };

  const handleForgotPasswordStep1 = async (e: React.FormEvent) => {
    e.preventDefault();
    setForgotLoading(true);
    setForgotError("");
    setForgotSuccess("");

    try {
      const response = await fetch(API_ENDPOINTS.AUTH.FORGOT_PASSWORD, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: forgotEmail,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setForgotSuccess("Recovery code has been sent to your email!");
        setForgotStep(2); // Chuyển sang bước 2
      } else {
        setForgotError(data.message || "Email does not exist in the system");
      }
    } catch (err) {
      setForgotError("Network error. Please try again.");
      console.error("Forgot password error:", err);
    } finally {
      setForgotLoading(false);
    }
  };

  const handleForgotPasswordStep2 = async (e: React.FormEvent) => {
    e.preventDefault();
    setForgotLoading(true);
    setForgotError("");

    // Validation
    if (forgotNewPassword !== forgotConfirmPassword) {
      setForgotError("Passwords do not match");
      setForgotLoading(false);
      return;
    }

    if (forgotNewPassword.length < 8) {
      setForgotError("Password must be at least 8 characters");
      setForgotLoading(false);
      return;
    }

    try {
      const response = await fetch(API_ENDPOINTS.AUTH.RESET_PASSWORD, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: forgotEmail,
          code: forgotCode,
          new_password: forgotNewPassword,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setForgotSuccess("Password reset successful! You can login now.");
        // Reset form và đóng modal
        setTimeout(() => {
          setShowForgotPassword(false);
          setForgotStep(1);
          setForgotEmail("");
          setForgotCode("");
          setForgotNewPassword("");
          setForgotConfirmPassword("");
          setForgotSuccess("");
        }, 2000);
      } else {
        setForgotError(
          data.message || "Verification code is incorrect or expired"
        );
      }
    } catch (err) {
      setForgotError("Network error. Please try again.");
      console.error("Reset password error:", err);
    } finally {
      setForgotLoading(false);
    }
  };

  const resetForgotPasswordModal = () => {
    setShowForgotPassword(false);
    setForgotStep(1);
    setForgotEmail("");
    setForgotCode("");
    setForgotNewPassword("");
    setForgotConfirmPassword("");
    setForgotError("");
    setForgotSuccess("");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-6">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-6">
            <div className="flex items-center justify-center gap-2 mb-4">
              <img src={icon} alt="Voice Agent" className="w-8 h-8" />
              <h1 className="text-2xl font-bold text-gray-900">Voice Agent</h1>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Account Number/Phone Number
              </label>
              <div className="relative">
                <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">
                  <LogIn className="w-5 h-5" />
                </div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-12 pr-4 py-3.5 rounded-lg focus:outline-none transition-all text-gray-900 placeholder-gray-400"
                  style={{
                    backgroundColor: "#f1f5f9",
                    border: "1px solid #e5e7eb",
                  }}
                  onFocus={(e) => (e.target.style.borderColor = "#00b14f")}
                  onBlur={(e) => (e.target.style.borderColor = "#e5e7eb")}
                  placeholder="username"
                  required
                  disabled={loading}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                    />
                  </svg>
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-12 pr-12 py-3.5 rounded-lg focus:outline-none transition-all text-gray-900 placeholder-gray-400"
                  style={{
                    backgroundColor: "#f1f5f9",
                    border: "1px solid #e5e7eb",
                  }}
                  onFocus={(e) => (e.target.style.borderColor = "#00b14f")}
                  onBlur={(e) => (e.target.style.borderColor = "#e5e7eb")}
                  placeholder="Password"
                  required
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-green-400 transition-colors cursor-pointer"
                >
                  {showPassword ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>

            {error && (
              <div
                className="p-3 rounded-lg"
                style={{
                  backgroundColor: "rgba(239, 68, 68, 0.1)",
                  borderLeft: "3px solid #ef4444",
                }}
              >
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-lg font-semibold text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ backgroundColor: loading ? "#7ed957" : "#00b14f" }}
              onMouseEnter={(e) =>
                !loading && (e.currentTarget.style.backgroundColor = "#009944")
              }
              onMouseLeave={(e) =>
                !loading && (e.currentTarget.style.backgroundColor = "#00b14f")
              }
            >
              {loading ? "Logging in..." : "Login"}
            </button>

            <div className="flex items-center justify-between text-sm pt-4">
              <button
                type="button"
                onClick={() => setShowRegister(true)}
                className="flex items-center gap-1.5 text-green-600 hover:text-green-700 transition-all cursor-pointer"
              >
                <UserPlus className="w-4 h-4" />
                Register
              </button>
              <button
                type="button"
                onClick={() => setShowSupport(true)}
                className="flex items-center gap-1.5 text-green-600 hover:text-green-700 transition-all cursor-pointer"
              >
                <HelpCircle className="w-4 h-4" />
                Support
              </button>
              <button
                type="button"
                onClick={() => setShowForgotPassword(true)}
                className="flex items-center gap-1.5 text-green-600 hover:text-green-700 transition-all cursor-pointer"
              >
                <KeyRound className="w-4 h-4" />
                Forgot Password
              </button>
            </div>
          </form>

          <p className="text-center text-xs text-gray-500 mt-6">
            Secured by{" "}
            <span className="text-gray-700 font-semibold">AWS Cognito</span>
          </p>
        </div>
      </div>

      {/* Register Modal */}
      {showRegister && (
        <div className="fixed inset-0 bg-gray-100 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">
                  Register Account
                </h2>
                <button
                  onClick={() => setShowRegister(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>
              <form onSubmit={handleRegister} className="space-y-4">
                <input
                  type="text"
                  placeholder="Username"
                  value={regUsername}
                  onChange={(e) => setRegUsername(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg focus:outline-none transition-all text-gray-900 placeholder-gray-400"
                  style={{
                    backgroundColor: "#f1f5f9",
                    border: "1px solid #e5e7eb",
                  }}
                  onFocus={(e) => (e.target.style.borderColor = "#00b14f")}
                  onBlur={(e) => (e.target.style.borderColor = "#e5e7eb")}
                  required
                  disabled={regLoading}
                />
                <input
                  type="email"
                  placeholder="Email (required)"
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg focus:outline-none transition-all text-gray-900 placeholder-gray-400"
                  style={{
                    backgroundColor: "#f1f5f9",
                    border: "1px solid #e5e7eb",
                  }}
                  onFocus={(e) => (e.target.style.borderColor = "#00b14f")}
                  onBlur={(e) => (e.target.style.borderColor = "#e5e7eb")}
                  required
                  disabled={regLoading}
                />
                <input
                  type="tel"
                  placeholder="Phone Number (optional)"
                  value={regPhone}
                  onChange={(e) => {
                    const formatted = formatPhoneNumber(e.target.value);
                    setRegPhone(formatted);
                  }}
                  className="w-full px-4 py-3 rounded-lg focus:outline-none transition-all text-gray-900 placeholder-gray-400"
                  style={{
                    backgroundColor: "#f1f5f9",
                    border: "1px solid #e5e7eb",
                  }}
                  onFocus={(e) => (e.target.style.borderColor = "#00b14f")}
                  onBlur={(e) => (e.target.style.borderColor = "#e5e7eb")}
                  disabled={regLoading}
                />
                <input
                  type="password"
                  placeholder="Password (at least 8 characters)"
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg focus:outline-none transition-all text-gray-900 placeholder-gray-400"
                  style={{
                    backgroundColor: "#f1f5f9",
                    border: "1px solid #e5e7eb",
                  }}
                  onFocus={(e) => (e.target.style.borderColor = "#00b14f")}
                  onBlur={(e) => (e.target.style.borderColor = "#e5e7eb")}
                  required
                  disabled={regLoading}
                />
                <input
                  type="password"
                  placeholder="Confirm Password"
                  value={regConfirmPassword}
                  onChange={(e) => setRegConfirmPassword(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg focus:outline-none transition-all text-gray-900 placeholder-gray-400"
                  style={{
                    backgroundColor: "#f1f5f9",
                    border: "1px solid #e5e7eb",
                  }}
                  onFocus={(e) => (e.target.style.borderColor = "#00b14f")}
                  onBlur={(e) => (e.target.style.borderColor = "#e5e7eb")}
                  required
                  disabled={regLoading}
                />

                {regError && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
                    {regError}
                  </div>
                )}

                {regSuccess && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-600">
                    {regSuccess}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={regLoading}
                  className="w-full py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {regLoading ? "Registering..." : "Register"}
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Forgot Password Modal */}
      {showForgotPassword && (
        <div className="fixed inset-0 bg-gray-100 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">
                  {forgotStep === 1 ? "Forgot Password" : "Reset Password"}
                </h2>
                <button
                  onClick={resetForgotPasswordModal}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>

              {forgotStep === 1 ? (
                <>
                  <p className="text-gray-600 mb-4">
                    Enter your email to receive a recovery code
                  </p>
                  <form
                    onSubmit={handleForgotPasswordStep1}
                    className="space-y-4"
                  >
                    <input
                      type="email"
                      placeholder="example@email.com"
                      value={forgotEmail}
                      onChange={(e) => setForgotEmail(e.target.value)}
                      className="w-full px-4 py-3 rounded-lg focus:outline-none transition-all text-gray-900 placeholder-gray-400"
                      style={{
                        backgroundColor: "#f1f5f9",
                        border: "1px solid #e5e7eb",
                      }}
                      onFocus={(e) => (e.target.style.borderColor = "#00b14f")}
                      onBlur={(e) => (e.target.style.borderColor = "#e5e7eb")}
                      required
                      disabled={forgotLoading}
                    />

                    {forgotError && (
                      <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
                        {forgotError}
                      </div>
                    )}

                    {forgotSuccess && (
                      <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-600">
                        {forgotSuccess}
                      </div>
                    )}

                    <button
                      type="submit"
                      disabled={forgotLoading}
                      className="w-full py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {forgotLoading ? "Sending..." : "Send Recovery Code"}
                    </button>
                  </form>
                </>
              ) : (
                <>
                  <p className="text-gray-600 mb-4">
                    Enter the verification code sent to{" "}
                    <strong>{forgotEmail}</strong>
                  </p>
                  <form
                    onSubmit={handleForgotPasswordStep2}
                    className="space-y-4"
                  >
                    <input
                      type="text"
                      placeholder="Verification Code (6 digits)"
                      value={forgotCode}
                      onChange={(e) => setForgotCode(e.target.value)}
                      className="w-full px-4 py-3 rounded-lg focus:outline-none transition-all text-gray-900 placeholder-gray-400 text-center text-lg tracking-widest"
                      style={{
                        backgroundColor: "#f1f5f9",
                        border: "1px solid #e5e7eb",
                      }}
                      onFocus={(e) => (e.target.style.borderColor = "#00b14f")}
                      onBlur={(e) => (e.target.style.borderColor = "#e5e7eb")}
                      required
                      disabled={forgotLoading}
                      maxLength={6}
                    />
                    <input
                      type="password"
                      placeholder="New Password (at least 8 characters)"
                      value={forgotNewPassword}
                      onChange={(e) => setForgotNewPassword(e.target.value)}
                      className="w-full px-4 py-3 rounded-lg focus:outline-none transition-all text-gray-900 placeholder-gray-400"
                      style={{
                        backgroundColor: "#f1f5f9",
                        border: "1px solid #e5e7eb",
                      }}
                      onFocus={(e) => (e.target.style.borderColor = "#00b14f")}
                      onBlur={(e) => (e.target.style.borderColor = "#e5e7eb")}
                      required
                      disabled={forgotLoading}
                    />
                    <input
                      type="password"
                      placeholder="Confirm New Password"
                      value={forgotConfirmPassword}
                      onChange={(e) => setForgotConfirmPassword(e.target.value)}
                      className="w-full px-4 py-3 rounded-lg focus:outline-none transition-all text-gray-900 placeholder-gray-400"
                      style={{
                        backgroundColor: "#f1f5f9",
                        border: "1px solid #e5e7eb",
                      }}
                      onFocus={(e) => (e.target.style.borderColor = "#00b14f")}
                      onBlur={(e) => (e.target.style.borderColor = "#e5e7eb")}
                      required
                      disabled={forgotLoading}
                    />

                    {forgotError && (
                      <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
                        {forgotError}
                      </div>
                    )}

                    {forgotSuccess && (
                      <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-600">
                        {forgotSuccess}
                      </div>
                    )}

                    <div className="flex gap-3">
                      <button
                        type="button"
                        onClick={() => setForgotStep(1)}
                        className="flex-1 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                        disabled={forgotLoading}
                      >
                        Back
                      </button>
                      <button
                        type="submit"
                        disabled={forgotLoading}
                        className="flex-1 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {forgotLoading ? "Processing..." : "Reset Password"}
                      </button>
                    </div>
                  </form>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Support Modal */}
      {showSupport && (
        <div className="fixed inset-0 bg-white bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">Support</h2>
                <button
                  onClick={() => setShowSupport(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>
              <div className="space-y-4">
                <div className="p-4 bg-green-50 rounded-lg">
                  <h3 className="font-semibold text-green-800 mb-2">
                    📞 Hotline
                  </h3>
                  <p className="text-green-700">1900 545 415</p>
                  <p className="text-sm text-green-600">24/7 - Free</p>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-semibold text-blue-800 mb-2">
                    💬 Live Chat
                  </h3>
                  <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors">
                    Start Chat
                  </button>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-semibold text-gray-800 mb-2">📧 Email</h3>
                  <p className="text-gray-700">support@vpbank.com.vn</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
