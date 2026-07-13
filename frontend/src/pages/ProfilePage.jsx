import { useEffect, useState } from "react";
import { Mail, Phone, User } from "lucide-react";
import { api } from "../api/client.js";
import { useAuth } from "../state/AuthContext.jsx";
import { Badge } from "../components/Badge.jsx";
import { LoadingState } from "../components/Status.jsx";
import { formatDate, isOverdue } from "../utils/format.js";

export function ProfilePage() {
  const { user, isLibrarian } = useAuth();
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listLoans(false)
      .then(setLoans)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const initials = user?.name
    ? user.name.split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase()
    : "?";

  return (
    <section className="page-section">
      <p className="eyebrow"><User size={13} />Account</p>
      <h1 style={{ marginBottom: "1.5rem" }}>My profile</h1>

      <div className="profile-card">
        <div className="avatar">{initials}</div>
        <div className="profile-info">
          <h2>{user?.name}</h2>
          <Badge tone={isLibrarian ? "warning" : "info"}>{user?.role}</Badge>
          <div className="profile-meta">
            <span><Mail size={14} />{user?.email}</span>
            <span><Phone size={14} />{user?.phone_number}</span>
          </div>
        </div>
      </div>

      <h2 style={{ marginBottom: "1rem" }}>Loan history</h2>

      {loading && <LoadingState label="Loading your loans" />}

      {!loading && loans.length === 0 && (
        <p className="muted">No loan history yet. Browse the catalog to borrow a book.</p>
      )}

      {!loading && loans.length > 0 && (
        <div className="loans-list">
          {loans.map(loan => {
            const overdue = isOverdue(loan.due_date, loan.returned_at, loan.status);
            const tone = loan.status === "RETURNED" ? "success" : overdue ? "danger" : "warning";
            const label = loan.status === "RETURNED" ? "Returned" : overdue ? "Overdue" : "Borrowed";
            return (
              <div className={`loan-card ${overdue ? "overdue" : ""}`} key={loan.loan_id}>
                <div className="loan-info">
                  <h3>{loan.book?.title}</h3>
                  <p>by {loan.book?.author}</p>
                  <p style={{ marginTop: 4, fontSize: "0.8rem", color: "var(--text-muted)" }}>
                    Due: {formatDate(loan.due_date)}
                    {loan.returned_at && <> &middot; Returned: {formatDate(loan.returned_at)}</>}
                  </p>
                </div>
                <Badge tone={tone}>{label}</Badge>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
