import { useEffect, useState } from "react";
import { ClipboardList } from "lucide-react";
import { useLocation } from "react-router-dom";
import { api } from "../api/client.js";
import { useAuth } from "../state/AuthContext.jsx";
import { useToast } from "../state/ToastContext.jsx";
import { Badge } from "../components/Badge.jsx";
import { EmptyState, ErrorState, LoadingState } from "../components/Status.jsx";
import { formatDate, isOverdue } from "../utils/format.js";

export function LoansPage() {
  const { isLibrarian } = useAuth();
  const { showToast } = useToast();
  const location = useLocation();
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeOnly, setActiveOnly] = useState(false);
  const [returning, setReturning] = useState(null);
  const [receiptJob, setReceiptJob] = useState(null);

  async function loadLoans(active = activeOnly) {
    setLoading(true);
    setError("");
    try {
      setLoans(await api.listLoans(active));
    } catch (err) {
      setError(err.message || "Unable to load loans");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadLoans(false); }, []);

  useEffect(() => {
    const jobId = location.state?.receiptJobId;
    if (!jobId) return undefined;

    let cancelled = false;
    let timerId;

    async function pollReceipt() {
      try {
        const result = await api.getReceiptJobStatus(jobId);
        if (cancelled) return;

        setReceiptJob(result);
        if (result.task_status === "SUCCESS") {
          showToast(result.message, "success");
          return;
        }
        if (result.task_status === "FAILURE") {
          showToast(result.message, "error");
          return;
        }

        timerId = window.setTimeout(pollReceipt, 1500);
      } catch (err) {
        if (!cancelled) {
          showToast(err.message || "Unable to check receipt status", "error");
        }
      }
    }

    pollReceipt();
    return () => {
      cancelled = true;
      window.clearTimeout(timerId);
    };
  }, [location.state?.receiptJobId, showToast]);

  function toggleFilter(active) {
    setActiveOnly(active);
    loadLoans(active);
  }

  async function handleReturn(loanId) {
    setReturning(loanId);
    try {
      const result = await api.returnLoan(loanId);
      showToast(result.message, "success");
      loadLoans(activeOnly);
    } catch (err) {
      showToast(err.message || "Unable to return book", "error");
    } finally {
      setReturning(null);
    }
  }

  if (loading) return <LoadingState label="Loading loans" />;

  return (
    <section className="page-section">
      <div className="page-heading">
        <div>
          <p className="eyebrow"><ClipboardList size={13} />{isLibrarian ? "All loans" : "My loans"}</p>
          <h1>Loan history</h1>
          <p className="muted">Track borrowing, due dates, and returns.</p>
        </div>
      </div>

      <div className="filter-tabs">
        <button className={`filter-tab ${!activeOnly ? "active" : ""}`} onClick={() => toggleFilter(false)}>
          All loans
        </button>
        <button className={`filter-tab ${activeOnly ? "active" : ""}`} onClick={() => toggleFilter(true)}>
          Active only
        </button>
      </div>

      {receiptJob && (
        <div className="borrow-panel">
          <span>{receiptJob.message}</span>
          {receiptJob.pdf_download_url && (
            <a
              className="button compact"
              href={api.assetUrl(receiptJob.pdf_download_url)}
              target="_blank"
              rel="noreferrer"
            >
              Download receipt
            </a>
          )}
        </div>
      )}

      {error && <ErrorState message={error} onRetry={() => loadLoans()} />}
      {!error && loans.length === 0 && (
        <EmptyState title="No loans found" message={activeOnly ? "No active loans at the moment." : "No loan history yet."} />
      )}

      {!error && loans.length > 0 && (
        <div className="loans-list">
          {loans.map(loan => {
            const overdue = isOverdue(loan.due_date, loan.returned_at, loan.status);
            const statusTone = loan.status === "RETURNED" ? "success" : overdue ? "danger" : "warning";
            const statusLabel = loan.status === "RETURNED" ? "Returned" : overdue ? "Overdue" : "Borrowed";
            return (
              <div className={`loan-card ${overdue ? "overdue" : ""}`} key={loan.loan_id}>
                <div className="loan-info">
                  <h3>{loan.book?.title}</h3>
                  <p>
                    by {loan.book?.author}
                    {isLibrarian && <> &mdash; <strong>{loan.member?.name}</strong></>}
                  </p>
                  <p style={{ marginTop: 4 }}>
                    Due: {formatDate(loan.due_date)}
                    {loan.returned_at && <> &middot; Returned: {formatDate(loan.returned_at)}</>}
                  </p>
                </div>
                <div className="loan-meta">
                  <Badge tone={statusTone}>{statusLabel}</Badge>
                  {loan.status === "BORROWED" && (
                    <button
                      className="button secondary compact"
                      disabled={returning === loan.loan_id}
                      onClick={() => handleReturn(loan.loan_id)}
                    >
                      {returning === loan.loan_id ? "Returning…" : "Return"}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
