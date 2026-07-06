# Library Management System

A command-line Library Management System backed by PostgreSQL running in Docker.

## Features

- Add, list, search, and remove books.
- Register members.
- Record book loans and returns with stock updates.
- Persist all books, members, and loan history in PostgreSQL.
- Run lint and PostgreSQL integration tests in GitHub Actions.

## Run Locally

Start PostgreSQL:

```bash
docker compose up -d postgres
```

The Compose file maps PostgreSQL to host port `5433` by default to avoid
conflicts with a local Postgres installation. The CLI defaults to:

```text
postgresql://library_user:12345678@localhost:5433/library_management_fast_api
```

Initialize the schema:

```bash
uv run library init-db
```

Use the CLI:

```bash
uv run library add-book --title "Clean Architecture" --author "Robert C. Martin" --category Software --price 34.50 --publish-year 2017 --stock 2
uv run library list-books
uv run library search-books clean
uv run library register-member --name "Ayesha Khan" --email ayesha@example.com --phone 555-0101
uv run library loan-book --book-id 1 --member-id 1 --days 14
uv run library return-book 1
uv run library list-loans
uv run library remove-book 1
```

## Configuration

Copy `.env.example` to `.env` for Docker Compose defaults. If you run the CLI
against another database, set `DATABASE_URL`.

Inside Docker, `DATABASE_URL` should use the service host:

```text
postgresql://library_user:12345678@postgres:5432/library_management_fast_api
```

From the host, use:

```text
postgresql://library_user:12345678@localhost:5433/library_management_fast_api
```

## Verification

Run lint:

```bash
uv run ruff check .
```

Run tests against Docker PostgreSQL:

```bash
DATABASE_URL=postgresql://library_user:12345678@localhost:5433/library_management_fast_api uv run pytest
```
