import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { LogIn } from "lucide-react";
import { useAuth } from "../state/AuthContext.jsx";
import { useToast } from "../state/ToastContext.jsx";

export function LoginPage({ librarianOnly = false }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { login } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname
    || (librarianOnly ? "/manage/books" : "/dashboard");

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await login(email, password, librarianOnly);
      showToast(librarianOnly ? "Librarian access granted." : "Welcome back!", "success");
      navigate(from, { replace: true });
    } catch (err) {
      showToast(err.message || "Login failed", "error");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <div className="form-heading">
          <span className="icon-disc"><LogIn size={22} /></span>
          <div>
            <h1>{librarianOnly ? "Librarian sign in" : "Sign in"}</h1>
            <p>{librarianOnly
              ? "Use an authorized librarian account to manage the catalog."
              : "Use your library account credentials."}</p>
          </div>
        </div>

        <label>
          Email address
          <input id="login-email" type="email" value={email}
            onChange={e => setEmail(e.target.value)} required placeholder="you@example.com" />
        </label>

        <label>
          Password
          <input id="login-password" type="password" value={password}
            onChange={e => setPassword(e.target.value)} required placeholder="••••••••" />
        </label>

        <button id="login-submit" className="button full" disabled={submitting}>
          {submitting ? "Signing in…" : librarianOnly ? "Open librarian dashboard" : "Sign in"}
        </button>

        {librarianOnly ? (
          <p className="form-footnote">Member account? <Link to="/login">Use member sign in</Link></p>
        ) : (
          <p className="form-footnote">
            New member? <Link to="/register">Create an account</Link>
            {" · "}<Link to="/librarian/login">Librarian sign in</Link>
          </p>
        )}
      </form>
    </section>
  );
}
