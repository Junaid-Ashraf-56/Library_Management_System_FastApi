const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const TOKEN_KEY = "library_access_token";

let onUnauthorized = null;

export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler;
}

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function storeToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearStoredToken() {
  localStorage.removeItem(TOKEN_KEY);
}

async function request(path, options = {}) {
  const token = getStoredToken();
  const headers = new Headers(options.headers);

  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearStoredToken();
    onUnauthorized?.();
  }

  if (!response.ok) {
    let payload = {};
    try {
      payload = await response.json();
    } catch {
      payload = { message: "Request failed" };
    }
    throw new Error(payload.detail || payload.message || "Request failed");
  }

  if (response.status === 204) {
    return undefined;
  }

  return response.json();
}

export const api = {
  assetUrl(path) {
    if (!path || /^https?:\/\//.test(path)) return path;
    return `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
  },
  login(email, password) {
    return request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },
  loginLibrarian(email, password) {
    return request("/auth/librarian/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },
  register(data) {
    return request("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  me() {
    return request("/auth/me");
  },
  listBooks() {
    return request("/books");
  },
  searchBooks(query) {
    return request(`/books/search?query=${encodeURIComponent(query)}`);
  },
  getBook(bookId) {
    return request(`/books/${bookId}`);
  },
  createBook(data) {
    return request("/books", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  updateBook(bookId, data) {
    return request(`/books/${bookId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },
  deleteBook(bookId) {
    return request(`/books/${bookId}`, {
      method: "DELETE",
    });
  },
  createLoan(bookId, days, memberId) {
    return request("/loans", {
      method: "POST",
      body: JSON.stringify({ book_id: bookId, days, member_id: memberId || null }),
    });
  },
  listLoans(activeOnly = false) {
    return request(`/loans?active_only=${activeOnly}`);
  },
  returnLoan(loanId) {
    return request(`/loans/${loanId}/return`, {
      method: "POST",
    });
  },
  getReceiptJobStatus(jobId) {
    return request(`/loans/receipt-jobs/${encodeURIComponent(jobId)}`);
  },
};
