import { AlertCircle, Inbox, Loader2 } from "lucide-react";

export function LoadingState({ label = "Loading" }) {
  return (
    <div className="status-panel">
      <Loader2 className="spin" size={28} />
      <p>{label}</p>
    </div>
  );
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="status-panel error-panel">
      <AlertCircle size={32} />
      <p>{message}</p>
      {onRetry && (
        <button className="button secondary" onClick={onRetry}>Try again</button>
      )}
    </div>
  );
}

export function EmptyState({ title, message }) {
  return (
    <div className="status-panel">
      <Inbox size={36} style={{ color: "var(--text-faint)" }} />
      <h3>{title}</h3>
      <p>{message}</p>
    </div>
  );
}

export function SkeletonGrid() {
  return (
    <div className="grid cards-grid">
      {Array.from({ length: 6 }, (_, i) => (
        <div className="card skeleton-card" key={i}>
          <div className="skeleton block" />
          <div className="skeleton line wide" />
          <div className="skeleton line" />
          <div className="skeleton line short" />
        </div>
      ))}
    </div>
  );
}
