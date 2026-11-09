import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../services/auth";
import "./Login.css";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  // Extract the user's role from common API response structures.
  const getUserRole = (response) => {
    const user =
      response?.user ||
      response?.data?.user ||
      response?.data ||
      response;

    return (
      user?.role ||
      user?.user_role ||
      user?.userType ||
      response?.role ||
      ""
    );
  };

  // Decide which dashboard to open based on the user's role.
  const getDashboardRoute = (role) => {
    const normalizedRole = String(role)
      .trim()
      .toLowerCase()
      .replace(/[\s-]+/g, "_");

    const roleRoutes = {
      student: "/student",
      staff: "/staff",
      department: "/department",
      department_head: "/department",
      dept_head: "/department",
      admin: "/admin",
      super_admin: "/super-admin",
    };

    return roleRoutes[normalizedRole] || null;
  };

  const handleLogin = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!email.trim() || !password) {
      setError("Please enter both email and password.");
      return;
    }

    setLoading(true);

    try {
      const response = await login(email.trim(), password);

      const role = getUserRole(response);
      const dashboardRoute = getDashboardRoute(role);

      if (!dashboardRoute) {
        setError(
          "Login successful, but your account role could not be identified. Please contact your campus administrator."
        );
        return;
      }

      setSuccess("Login successful! Redirecting...");

      navigate(dashboardRoute, { replace: true });

    } catch (error) {
      setError(
        error?.message || "Unable to log in. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-page">
      <section className="login-campus-panel">
        <div className="campus-photo" aria-hidden="true" />

        <div className="campus-overlay">
          <div className="campus-brand">
            <div className="campus-brand-mark">SC</div>
            <span>SMART CAMPUS</span>
          </div>

          <div className="campus-intro">
            <p className="campus-eyebrow">YOUR CAMPUS, CONNECTED</p>

            <h1>A better campus starts with you.</h1>

            <p className="campus-description">
              One place to report concerns, follow updates, and help
              make our campus a better place for everyone.
            </p>

            <div className="campus-features">
              <div className="campus-feature">
                <span className="feature-mark">✓</span>
                <span>Report campus issues easily</span>
              </div>

              <div className="campus-feature">
                <span className="feature-mark">✓</span>
                <span>Track your reports and updates</span>
              </div>

              <div className="campus-feature">
                <span className="feature-mark">✓</span>
                <span>Help build a safer campus</span>
              </div>
            </div>
          </div>

          <p className="campus-footer">
            Your voice matters. Let's improve campus life together.
          </p>
        </div>
      </section>

      <section className="login-form-panel">
        <div className="login-form-wrap">
          <div className="mobile-brand">
            <div className="campus-brand-mark">SC</div>
            <span>SMART CAMPUS</span>
          </div>

          <div className="login-heading">
            <p className="login-eyebrow">WELCOME BACK</p>
            <h2>Sign in to your account</h2>
            <p>Enter your details to access your campus dashboard.</p>
          </div>

          <form className="login-form" onSubmit={handleLogin}>
            {error && (
              <p className="login-message login-error" role="alert">
                {error}
              </p>
            )}

            {success && (
              <p className="login-message login-success" role="status">
                {success}
              </p>
            )}

            <div className="login-field">
              <label htmlFor="email">Email address</label>

              <input
                id="email"
                name="email"
                type="email"
                placeholder="you@university.edu"
                autoComplete="username"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
                disabled={loading}
              />
            </div>

            <div className="login-field">
              <div className="password-label-row">
                <label htmlFor="password">Password</label>
                <span className="password-hint">Keep it secure</span>
              </div>

              <input
                id="password"
                name="password"
                type="password"
                placeholder="Enter your password"
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
                disabled={loading}
              />
            </div>

            <div className="login-options">
              <label className="remember-option">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(event) =>
                    setRememberMe(event.target.checked)
                  }
                  disabled={loading}
                />

                <span>Remember me</span>
              </label>

              <span className="forgot-password">
                Forgot password?
              </span>
            </div>

            <button
              className="login-submit"
              type="submit"
              disabled={loading}
            >
              {loading ? "Signing in..." : "Sign in"}

              {!loading && (
                <span aria-hidden="true">→</span>
              )}
            </button>

            <p className="login-help">
              Having trouble signing in? Contact your campus administrator.
            </p>
          </form>

          <p className="login-privacy">
            Secure access for the campus community
          </p>
        </div>
      </section>
    </main>
  );
}

export default Login;