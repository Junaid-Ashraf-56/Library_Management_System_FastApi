import { Link } from "react-router-dom";
import { Banknote, BookOpen, Calendar, Layers } from "lucide-react";
import { formatCurrency } from "../utils/format.js";
import { Badge } from "./Badge.jsx";

export function BookCard({ book }) {
  const available = book.stock > 0;
  return (
    <article className="card book-card">
      <div className="book-cover" aria-hidden="true">
        <BookOpen size={36} />
      </div>
      <div className="book-card-body">
        <div className="card-title-row">
          <h3>{book.title}</h3>
          <Badge tone={available ? "success" : "danger"}>
            {available ? "In Stock" : "Out"}
          </Badge>
        </div>
        <p className="muted" style={{ fontSize: "0.8rem" }}>by {book.author}</p>
        <div className="meta-grid">
          <span><Layers size={13} />{book.category}</span>
          <span><Calendar size={13} />{book.publish_year}</span>
          <span><Banknote size={13} />{formatCurrency(book.price)}</span>
          <span><BookOpen size={13} />{book.stock} left</span>
        </div>
      </div>
      <Link className="button full secondary" to={`/books/${book.book_id}`}>
        View details
      </Link>
    </article>
  );
}
