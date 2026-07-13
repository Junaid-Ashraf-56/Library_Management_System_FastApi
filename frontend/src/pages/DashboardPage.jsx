import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BookOpen, ClipboardList, Library, PlusCircle } from "lucide-react";
import { api } from "../api/client.js";
import { useAuth } from "../state/AuthContext.jsx";
import { Badge } from "../components/Badge.jsx";
import { LoadingState } from "../components/Status.jsx";

export function DashboardPage() {
  const { user, isAuthenticated, isLibrarian } = useAuth();
  const [books, setBooks] = useState([]);
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [bookData, loanData] = await Promise.all([
          api.listBooks(),
          isAuthenticated ? api.listLoans(false) : Promise.resolve([]),
        ]);
        setBooks(bookData);
        setLoans(loanData);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [isAuthenticated]);

  if (loading) return <LoadingState label="Preparing your dashboard" />;

  const activeLoans = loans.filter(l => l.status === "BORROWED").length;
  const available = books.filter(b => b.stock > 0).length;

  return (
    <section className="page-section">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Dashboard</p>
          <h1>{isAuthenticated ? `Welcome back, ${user?.name?.split(" ")[0]}` : "Library dashboard"}</h1>
          <p className="muted">
            {isLibrarian
              ? "Catalog and circulation overview."
              : isAuthenticated
                ? "Browse, borrow, and track your loans."
                : "Browse the catalog and sign in to manage your loans."}
          </p>
        </div>
        {isAuthenticated && <Badge tone={isLibrarian ? "warning" : "info"}>{user?.role}</Badge>}
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <Library size={22} />
          <span>Total books</span>
          <strong>{books.length}</strong>
        </div>
        <div className="stat-card">
          <BookOpen size={22} />
          <span>Available titles</span>
          <strong>{available}</strong>
        </div>
        <div className="stat-card">
          <ClipboardList size={22} />
          <span>{isLibrarian ? "Active loans" : isAuthenticated ? "Your active loans" : "Member loans"}</span>
          <strong>{isAuthenticated ? activeLoans : "Sign in"}</strong>
        </div>
      </div>

      <div className="action-grid">
        <Link className="action-tile" to="/books">
          <BookOpen size={24} />
          <strong>Explore catalog</strong>
          <span>Search the live book inventory.</span>
        </Link>
        <Link className="action-tile" to={isAuthenticated ? "/loans" : "/login"}>
          <ClipboardList size={24} />
          <strong>{isLibrarian ? "Review all loans" : isAuthenticated ? "View my loans" : "Member sign in"}</strong>
          <span>{isAuthenticated ? "Track due dates and returns." : "Sign in to view borrowing activity."}</span>
        </Link>
        {isLibrarian && (
          <Link className="action-tile" to="/manage/books">
            <PlusCircle size={24} />
            <strong>Manage catalog</strong>
            <span>Add, edit, and remove books.</span>
          </Link>
        )}
      </div>
    </section>
  );
}
