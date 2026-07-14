import { Link } from "react-router-dom";
import { ArrowRight, BookOpen, Clock, ShieldCheck } from "lucide-react";
import { useAuth } from "../state/AuthContext.jsx";

export function LandingPage() {
  const { isAuthenticated } = useAuth();
  return (
    <>
      <section className="hero">
        <div className="hero-content">
          <p className="eyebrow">Your community library</p>
          <h1>Find your next book.</h1>
          <p className="hero-copy">
            Browse the catalog, borrow a title, and keep track of your loans in one place.
          </p>
          <div className="hero-actions">
            <Link className="button large" to={isAuthenticated ? "/dashboard" : "/register"}>
              {isAuthenticated ? "Open dashboard" : "Create an account"}
              <ArrowRight size={18} />
            </Link>
            <Link className="button secondary large" to="/books">Browse catalog</Link>
          </div>
        </div>

        <div className="hero-panel">
          <div className="hero-stat">
            <BookOpen size={22} />
            <div>
              <strong>Browse books</strong>
              <span>Search by title, author, or category</span>
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
              <strong>Simple to manage</strong>
              <span>Clear tools for members and librarians</span>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
