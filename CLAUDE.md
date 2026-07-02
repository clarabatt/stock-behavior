# CLAUDE.md — Stock Behavior

S&P 500 stock behavior explorer. Pulls stock price data, presents it in tabular and chart form, supports annotated notes per (date, company), and includes an AI-assisted analysis layer.

---

## Stack

**Backend:** Python 3.12, FastAPI, SQLModel, PostgreSQL 15, Alembic, `uv`
**Frontend:** React 19, TypeScript, Zustand, React Router, Radix UI, SCSS
**Infra:** Docker + Docker Compose

---

## Dev commands

```bash
make dev                # start full stack (docker compose up)
make test-db-up         # start isolated test DB on :5434
make test               # run pytest suite against test DB
make test-db-reset      # wipe and restart test DB after schema changes
```

| Service  | URL                        |
| -------- | -------------------------- |
| Frontend | http://localhost:5173      |
| Backend  | http://localhost:8000      |
| Swagger  | http://localhost:8000/docs |
| Postgres | localhost:5433             |

To run tests manually:

```bash
TEST_DATABASE_URL=postgresql://stock:stock@localhost:5433/stock_test uv run pytest -v
```

---

## Code guidelines

### Typing and enums over strings

- Always use Python enums (defined in `backend/database/models.py`) for any field with a fixed set of values. Never use raw strings for status fields, categories, roles, or types.
- In TypeScript, import and use the enums or string-literal unions defined in `frontend/src/stores/`. Never compare against string literals when an enum exists.
- Declare explicit types for all function arguments, return values, and store state. Avoid `any`.

### Component-first frontend

- **Prefer extracting components over growing pages.** If a section of a view has its own state, title, or reusable surface, it belongs in `frontend/src/components/`.
- `frontend/src/views/` contains only page-level route components. Business logic and UI sections live in components.
- Before creating a new component, search `frontend/src/components/` for something that already covers the need. Reuse or extend before creating.
- Shared primitives (buttons, dialogs, spinners, badges) live in `frontend/src/components/ui/`. Add to this library rather than inlining one-off styles.

**Extract to `components/` when any of these are true:**

- The section has its own props interface.
- It contains more than a few lines of JSX markup.
- It could be reused on another view, even hypothetically.
- It manages its own local state.

### State management

| State type                                    | Where                      |
| --------------------------------------------- | -------------------------- |
| Auth / current user                           | `stores/auth.ts`           |
| Toast notifications                           | `stores/toast.ts`          |
| Form inputs, loading flags, modal open/closed | Component-local `useState` |

Do not add new Zustand stores unless the state is genuinely shared across multiple views.

### General

- No comments unless the _why_ is non-obvious. Don't comment what the code already says.
- Keep route handlers thin — delegate to repositories and services, not inline logic.
- Migrations are the source of truth for schema. Never mutate the DB outside of Alembic.

---

## Testing

### Philosophy

Integration tests that mirror real usage. Favor fewer, high-confidence tests over broad coverage.

### No-mock policy

- **Backend:** Test against a real PostgreSQL database. Never mock repository methods or services.
- **Allowed mocks (edge only):**
  - External AI APIs (Anthropic)
  - Google OAuth callbacks

### Backend (Pytest + SQLModel)

- Each test starts with a clean database (tables truncated by `clean_tables` fixture in `conftest.py`).
- Use factories from `backend/tests/factories.py` to seed data — do not create records inline.
- Test the API contract via `TestClient`. Assert DB side-effects by querying through the repository layer.
- Test files mirror the source tree under `backend/tests/`.

**Factories — pass desired state as kwargs, never mutate after creation:**

```python
# correct
user = UserFactory(is_active=False)

# wrong
user = UserFactory()
user.is_active = False
session.add(user)
session.commit()
```

**DB assertions — query through repositories:**

```python
# correct
from backend.database.repositories import UserRepository
persisted = UserRepository(session).get_by_email("test@example.com")
assert persisted is not None

# wrong
session.refresh(user)
assert user.email == "test@example.com"
```

### Workflow for new features

1. Define Given/When/Then scenarios before writing any code.
2. Write the tests first and get approval.
3. Only then implement the feature.
