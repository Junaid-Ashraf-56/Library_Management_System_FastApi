import { Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/Layout.jsx";
import { ProtectedRoute } from "./components/ProtectedRoute.jsx";
import { BookDetailsPage } from "./pages/BookDetailsPage.jsx";
import { BooksPage } from "./pages/BooksPage.jsx";
import { DashboardPage } from "./pages/DashboardPage.jsx";
import { LandingPage } from "./pages/LandingPage.jsx";
import { LibrarianBooksPage } from "./pages/LibrarianBooksPage.jsx";
import { LoansPage } from "./pages/LoansPage.jsx";
import { LoginPage } from "./pages/LoginPage.jsx";
import { ProfilePage } from "./pages/ProfilePage.jsx";
import { RegisterPage } from "./pages/RegisterPage.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<LandingPage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="librarian/login" element={<LoginPage librarianOnly />} />
        <Route path="register" element={<RegisterPage />} />
        <Route path="books" element={<BooksPage />} />
        <Route path="books/:bookId" element={<BookDetailsPage />} />
        <Route path="dashboard" element={<DashboardPage />} />

        <Route element={<ProtectedRoute />}>
          <Route path="loans" element={<LoansPage />} />
          <Route path="profile" element={<ProfilePage />} />
        </Route>

        <Route element={<ProtectedRoute librarianOnly />}>
          <Route path="manage/books" element={<LibrarianBooksPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
