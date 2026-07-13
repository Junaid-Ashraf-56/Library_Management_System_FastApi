import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { UserPlus } from "lucide-react";
import { useAuth } from "../state/AuthContext.jsx";
import { useToast } from "../state/ToastContext.jsx";

export function RegisterPage() {
  const [form, setForm] = useState({ name: "", email: "", phone_number: "", password: "" });
  const [submitting, setSubmitting] = useState(false);
  const { register } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const set = (key) => (e) => setForm(f => ({ ...f, [key]: e.target.value }));

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await register(form);
      showToast("Account created! You can sign in now.", "success");
      navigate("/login");
    } catch (err) {
      showToast(err.message || "Registration failed", "error");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <div className="form-heading">
          <span className="icon-disc"><UserPlus size={22} /></span>
          <div>
            <h1>Create account</h1>
            <p>Sign up to borrow from our catalog.</p>
          </div>
        </div>

        <label>Full name
          <input id="reg-name" value={form.name} onChange={set("name")} required placeholder="Jane Doe" />
        </label>
        <label>Email address
          <input id="reg-email" type="email" value={form.email} onChange={set("email")} required placeholder="you@example.com" />
        </label>
        <label>Phone number
          <input id="reg-phone" value={form.phone_number} onChange={set("phone_number")} required placeholder="+1 555 000 0000" />
        </label>
        <label>Password
          <input id="reg-password" type="password" value={form.password} onChange={set("password")} required minLength={6} placeholder="Min. 6 characters" />
        </label>

        <button id="reg-submit" className="button full" disabled={submitting}>
          {submitting ? "Creating account…" : "Create account"}
        </button>

        <p className="form-footnote">
          Already registered? <Link to="/login">Sign in</Link>
        </p>
      </form>
    </section>
  );
}
