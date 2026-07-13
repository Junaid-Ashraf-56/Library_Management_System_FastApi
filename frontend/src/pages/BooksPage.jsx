import { useEffect, useState } from "react";
import { Search, X } from "lucide-react";
import { api } from "../api/client.js";
import { BookCard } from "../components/BookCard.jsx";
import { EmptyState, ErrorState, SkeletonGrid } from "../components/Status.jsx";

export function BooksPage() {
  const [books, setBooks] = useState([]);
  const [query, setQuery] = useState("");
  const [activeQuery, setActiveQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadBooks(term = "") {
    setLoading(true);
    setError("");
    try {
      const data = term.trim() ? await api.searchBooks(term.trim()) : await api.listBooks();
      setBooks(data);
    } catch (err) {
      setError(err.message || "Unable to load books");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadBooks(""); }, []);

  function handleSearch(e) {
    e.preventDefault();
    setActiveQuery(query);
    loadBooks(query);
  }

  function clearSearch() {
    setQuery("");
    setActiveQuery("");
    loadBooks("");
  }

  return (
    <section className="page-section">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Catalog</p>
          <h1>Find the right book</h1>
          <p className="muted">Search by title, author, or category.</p>
        </div>
      </div>

      <form className="search-bar" onSubmit={handleSearch}>
        <Search size={18} />
        <input
          id="catalog-search"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search catalog…"
        />
        {activeQuery && (
          <button className="icon-button ghost" type="button" onClick={clearSearch} aria-label="Clear search">
            <X size={16} />
          </button>
        )}
        <button className="button compact" type="submit">Search</button>
      </form>

      {loading && <SkeletonGrid />}
      {!loading && error && <ErrorState message={error} onRetry={() => loadBooks(activeQuery)} />}
      {!loading && !error && books.length === 0 && (
        <EmptyState title="No books found" message="Try a different title, author, or category." />
      )}
      {!loading && !error && books.length > 0 && (
        <div className="grid cards-grid">
          {books.map(book => <BookCard book={book} key={book.book_id} />)}
        </div>
      )}
    </section>
  );
}
