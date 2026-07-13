import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../state/AuthContext.jsx";
import { LoadingState } from "./Status.jsx";

export function ProtectedRoute({ librarianOnly = false }) {
  const { loading, isAuthenticated, isLibrarian } = useAuth();
  const location = useLocation();

  if (loading) {
    return <LoadingState label="Checking your session" />;
  }

  if (!isAuthenticated) {
    return <Navigate to={librarianOnly ? "/librarian/login" : "/login"} replace state={{ from: location }} />;
  }

  if (librarianOnly && !isLibrarian) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
