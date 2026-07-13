import { Link } from "react-router-dom";
import { ArrowRight, BookOpen, Clock, ShieldCheck, Sparkles } from "lucide-react";
import { useAuth } from "../state/AuthContext.jsx";

export function LandingPage() {
  const { isAuthenticated } = useAuth();
  return (
    <>
      <section className="hero">
        <div className="hero-content">
          <p className="eyebrow"><Sparkles size={14} />Modern library management</p>
          <h1>LibraCore</h1>
          <p className="hero-copy">
            A polished catalog, borrowing, returns, and loan tracking experience
            built on a FastAPI backend with JWT auth.
          </p>
          <div className="hero-actions">
            <Link className="button large" to={isAuthenticated ? "/dashboard" : "/register"}>
              {isAuthenticated ? "Open dashboard" : "Join as member"}
              <ArrowRight size={18} />
            </Link>
            <Link className="button secondary large" to="/books">Browse catalog</Link>
          </div>
        </div>

        <div className="hero-panel">
          <div className="hero-stat">
            <BookOpen size={22} />
            <div>
              <strong>Live catalog</strong>
              <span>Search by title, author or category</span>
            </div>
          </div>
          <div className="hero-stat">
            <Clock size={22} />
            <div>
              <strong>Loan tracking</strong>
              <span>Due dates, returns &amp; overdue alerts</span>
            </div>
          </div>
          <div className="hero-stat">
            <ShieldCheck size={22} />
            <div>
              <strong>Role-aware</strong>
              <span>Member and librarian views</span>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
