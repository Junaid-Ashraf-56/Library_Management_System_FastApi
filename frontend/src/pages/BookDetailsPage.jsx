import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Banknote, BookMarked, CalendarDays, Layers, PackageCheck } from "lucide-react";
import { api } from "../api/client.js";
import { Badge } from "../components/Badge.jsx";
import { ErrorState, LoadingState } from "../components/Status.jsx";
import { useAuth } from "../state/AuthContext.jsx";
import { useToast } from "../state/ToastContext.jsx";
import { formatCurrency } from "../utils/format.js";

export function BookDetailsPage() {
  const { bookId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, isLibrarian } = useAuth();
  const { showToast } = useToast();
  const [book, setBook] = useState(null);
  const [days, setDays] = useState(14);
  const [loading, setLoading] = useState(true);
  const [borrowing, setBorrowing] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        setBook(await api.getBook(Number(bookId)));
      } catch (err) {
        setError(err.message || "Unable to load book");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [bookId]);

  async function handleBorrow(e) {
    e.preventDefault();
    if (!book) return;
    if (!isAuthenticated) {
      navigate("/login", { state: { from: { pathname: `/books/${book.book_id}` } } });
      return;
    }
    setBorrowing(true);
    try {
      await api.createLoan(book.book_id, days);
      showToast("Book borrowed successfully!", "success");
      navigate("/loans");
    } catch (err) {
      showToast(err.message || "Unable to borrow book", "error");
    } finally {
      setBorrowing(false);
    }
  }

  if (loading) return <LoadingState label="Loading book details" />;
  if (error) return <ErrorState message={error} />;
  if (!book) return null;

  const available = book.stock > 0;

  return (
    <section className="page-section">
      <Link className="back-link" to="/books">
        <ArrowLeft size={16} />Back to catalog
      </Link>

      <div className="details-layout">
        <div className="detail-cover">
          <BookMarked size={72} />
        </div>

        <div className="detail-content">
          <div className="card-title-row">
            <div>
              <p className="eyebrow">Book details</p>
              <h1>{book.title}</h1>
              <p className="muted">by {book.author}</p>
            </div>
            <Badge tone={available ? "success" : "danger"}>
              {available ? "Available" : "Out of stock"}
            </Badge>
          </div>

          <div className="info-grid">
            <div><Layers size={16} /><span>Category</span><strong>{book.category}</strong></div>
            <div><CalendarDays size={16} /><span>Published</span><strong>{book.publish_year}</strong></div>
            <div><Banknote size={16} /><span>Price</span><strong>{formatCurrency(book.price)}</strong></div>
            <div><PackageCheck size={16} /><span>In stock</span><strong>{book.stock}</strong></div>
          </div>

          {!isLibrarian ? (
            <form className="borrow-panel" onSubmit={handleBorrow}>
              <label>
                Loan duration (days)
                <input
                  id="borrow-days"
                  type="number" min={1} max={90}
                  value={days}
                  onChange={e => setDays(Number(e.target.value))}
                />
              </label>
              <button id="borrow-submit" className="button" disabled={!available || borrowing}>
                {borrowing ? "Borrowing…" : "Borrow book"}
              </button>
            </form>
          ) : (
            <Link className="button" to="/manage/books">Manage catalog</Link>
          )}
        </div>
      </div>
    </section>
  );
}
