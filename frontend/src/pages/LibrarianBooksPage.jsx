import { useEffect, useState } from "react";
import { BookOpen, Edit2, Plus, Trash2, X } from "lucide-react";
import { api } from "../api/client.js";
import { useToast } from "../state/ToastContext.jsx";
import { EmptyState, ErrorState, LoadingState } from "../components/Status.jsx";
import { formatCurrency } from "../utils/format.js";

const EMPTY_FORM = { title: "", author: "", category: "", price: "", publish_year: "", stock: "" };

export function LibrarianBooksPage() {
  const { showToast } = useToast();
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [modal, setModal] = useState(null); // null | "add" | {book}
  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(null);

  async function loadBooks() {
    setLoading(true);
    setError("");
    try {
      setBooks(await api.listBooks());
    } catch (err) {
      setError(err.message || "Unable to load books");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadBooks(); }, []);

  function openAdd() { setForm(EMPTY_FORM); setModal("add"); }
  function openEdit(book) {
    setForm({
      title: book.title, author: book.author, category: book.category,
      price: String(book.price), publish_year: String(book.publish_year), stock: String(book.stock),
    });
    setModal(book);
  }
  function closeModal() { setModal(null); }

  const set = (key) => (e) => setForm(f => ({ ...f, [key]: e.target.value }));

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    const payload = {
      title: form.title, author: form.author, category: form.category,
      price: parseFloat(form.price), publish_year: parseInt(form.publish_year), stock: parseInt(form.stock),
    };
    try {
      if (modal === "add") {
        await api.createBook(payload);
        showToast("Book added to catalog.", "success");
      } else {
        await api.updateBook(modal.book_id, payload);
        showToast("Book updated.", "success");
      }
      closeModal();
      loadBooks();
    } catch (err) {
      showToast(err.message || "Save failed", "error");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(book) {
    if (!window.confirm(`Delete "${book.title}"? This cannot be undone.`)) return;
    setDeleting(book.book_id);
    try {
      await api.deleteBook(book.book_id);
      showToast("Book removed.", "success");
      loadBooks();
    } catch (err) {
      showToast(err.message || "Delete failed", "error");
    } finally {
      setDeleting(null);
    }
  }

  if (loading) return <LoadingState label="Loading catalog" />;

  return (
    <section className="page-section">
      <div className="page-heading">
        <div>
          <p className="eyebrow"><BookOpen size={13} />Librarian</p>
          <h1>Manage catalog</h1>
          <p className="muted">Add, edit, and remove books from the library.</p>
        </div>
        <button id="add-book-btn" className="button" onClick={openAdd}>
          <Plus size={17} />Add book
        </button>
      </div>

      {error && <ErrorState message={error} onRetry={loadBooks} />}
      {!error && books.length === 0 && (
        <EmptyState title="No books yet" message="Add the first book to get started." />
      )}

      {!error && books.length > 0 && (
        <div className="books-table-wrap">
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th>Author</th>
                <th>Category</th>
                <th>Year</th>
                <th>Price</th>
                <th>Stock</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {books.map(book => (
                <tr key={book.book_id}>
                  <td><strong>{book.title}</strong></td>
                  <td>{book.author}</td>
                  <td>{book.category}</td>
                  <td>{book.publish_year}</td>
                  <td>{formatCurrency(book.price)}</td>
                  <td>{book.stock}</td>
                  <td>
                    <div className="table-actions">
                      <button className="icon-button" title="Edit" onClick={() => openEdit(book)}>
                        <Edit2 size={15} />
                      </button>
                      <button
                        className="icon-button"
                        title="Delete"
                        style={{ color: "var(--red)" }}
                        disabled={deleting === book.book_id}
                        onClick={() => handleDelete(book)}
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {modal && (
        <div className="modal-backdrop" onClick={e => e.target === e.currentTarget && closeModal()}>
          <form className="modal" onSubmit={handleSave}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h2 className="modal-title">{modal === "add" ? "Add new book" : "Edit book"}</h2>
              <button type="button" className="icon-button ghost" onClick={closeModal}><X size={18} /></button>
            </div>
            <label>Title<input value={form.title} onChange={set("title")} required /></label>
            <label>Author<input value={form.author} onChange={set("author")} required /></label>
            <label>Category<input value={form.category} onChange={set("category")} required /></label>
            <label>Publication year<input type="number" value={form.publish_year} onChange={set("publish_year")} required min={1000} max={2100} /></label>
            <label>Price (PKR)<input type="number" step="0.01" value={form.price} onChange={set("price")} required min={0} /></label>
            <label>Stock<input type="number" value={form.stock} onChange={set("stock")} required min={0} /></label>
            <div className="modal-actions">
              <button type="button" className="button secondary" onClick={closeModal}>Cancel</button>
              <button type="submit" className="button" disabled={saving}>
                {saving ? "Saving…" : modal === "add" ? "Add book" : "Save changes"}
              </button>
            </div>
          </form>
        </div>
      )}
    </section>
  );
}
