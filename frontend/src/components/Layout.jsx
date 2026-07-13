import { useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { BookOpen, ClipboardList, Home, Library, LogOut, Menu, Search, User, X } from "lucide-react";
import { useAuth } from "../state/AuthContext.jsx";

export function AppLayout() {
  const [open, setOpen] = useState(false);
  const { user, isAuthenticated, isLibrarian, logout } = useAuth();
  const navigate = useNavigate();
  const close = () => setOpen(false);

  return (
    <div className="app-shell">
      <header className="topbar">
        <Link className="brand" to="/" onClick={close}>
          <span className="brand-mark"><Library size={20} /></span>
          <span>LibraCore</span>
        </Link>

        <button
          className="icon-button mobile-menu ghost"
          onClick={() => setOpen(v => !v)}
          aria-label="Toggle navigation"
        >
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>

        <nav className={open ? "open" : ""}>
          <NavLink to="/dashboard" onClick={close}><Home size={16} />Dashboard</NavLink>
          <NavLink to="/books" onClick={close}><Search size={16} />Catalog</NavLink>
          {isAuthenticated && (
            <NavLink to="/loans" onClick={close}>
              <ClipboardList size={16} />{isLibrarian ? "All loans" : "My loans"}
            </NavLink>
          )}
          {isLibrarian && (
            <NavLink to="/manage/books" onClick={close}><BookOpen size={16} />Manage books</NavLink>
          )}
          {isAuthenticated && (
            <NavLink to="/profile" onClick={close}><User size={16} />Profile</NavLink>
          )}
        </nav>

        <div className="topbar-actions">
          {user ? (
            <>
              <span className="user-pill">{user.role}</span>
              <button
                className="button secondary compact"
                onClick={() => { logout(); navigate("/"); }}
              >
                <LogOut size={15} />Logout
              </button>
            </>
          ) : (
            <>
              <Link className="button secondary compact" to="/login">Login</Link>
              <Link className="button compact" to="/librarian/login">Librarian</Link>
            </>
          )}
        </div>
      </header>

      <main><Outlet /></main>
    </div>
  );
}
