# Learning Async in FastAPI & Python — In Depth

> A hands-on, progressive learning plan. Each TODO is a mini-exercise you'll build inside your `the-fast-and-the-asynchronous` project.

---

## Phase 1: Python Async Fundamentals

> Before touching FastAPI, you need to deeply understand Python's `async`/`await` machinery.

### 1.1 — Coroutines & `await`
- [ ] Create `app/learn/01_coroutines.py` — Write a plain coroutine with `async def`, call it with `asyncio.run()`, observe that it returns a coroutine object if not awaited
- [ ] Demonstrate the difference between calling `my_func()` (returns coroutine) vs `await my_func()` (executes it)
- [ ] Chain 3 coroutines that `await` each other and print execution order

### 1.2 — `asyncio.sleep()` vs `time.sleep()`
- [ ] Create `app/learn/02_sleep_comparison.py` — Run 3 tasks with `time.sleep(1)` sequentially (~3s total)
- [ ] Refactor to use `asyncio.sleep(1)` with `asyncio.gather()` (~1s total)
- [ ] Add timing with `time.perf_counter()` to prove the difference
- [ ] **Key insight to document:** `time.sleep()` blocks the entire thread. `asyncio.sleep()` yields control back to the event loop.

### 1.3 — `asyncio.gather()` vs `asyncio.create_task()`
- [ ] Create `app/learn/03_gather_vs_tasks.py`
- [ ] Show `gather()` running multiple coroutines concurrently and collecting results
- [ ] Show `create_task()` for fire-and-forget patterns
- [ ] Demonstrate `gather(return_exceptions=True)` for error handling
- [ ] Show `TaskGroup` (Python 3.11+) as the modern alternative to `gather()`

### 1.4 — The Event Loop
- [ ] Create `app/learn/04_event_loop.py`
- [ ] Visualize the event loop: print timestamps showing how tasks interleave during `await` points
- [ ] Demonstrate that CPU-bound work inside `async def` blocks the loop (use a tight `for` loop)
- [ ] Show `asyncio.get_running_loop()` introspection

---

## Phase 2: Async Patterns & Pitfalls

### 2.1 — Blocking the Event Loop (The #1 Mistake)
- [ ] Create `app/learn/05_blocking_danger.py`
- [ ] Write an `async def` that does CPU-heavy work (e.g., compute Fibonacci recursively) — show it blocks other tasks
- [ ] Fix it with `loop.run_in_executor()` to offload to a thread pool
- [ ] Fix it with `asyncio.to_thread()` (Python 3.9+ shorthand)
- [ ] **Key insight:** Async is for I/O-bound work. CPU-bound work needs threads or processes.

### 2.2 — Async Iterators & Generators
- [ ] Create `app/learn/06_async_iterators.py`
- [ ] Build an `async for` loop using `__aiter__` / `__anext__`
- [ ] Build an async generator with `async def` + `yield`
- [ ] Show a practical use case: paginating through an API

### 2.3 — Async Context Managers
- [ ] Create `app/learn/07_async_context_managers.py`
- [ ] Build an `async with` resource using `__aenter__` / `__aexit__`
- [ ] Use `@asynccontextmanager` from `contextlib` as shorthand
- [ ] Practical example: managing a database connection pool

### 2.4 — Semaphores & Rate Limiting
- [ ] Create `app/learn/08_semaphores.py`
- [ ] Use `asyncio.Semaphore` to limit concurrent HTTP requests to 5 at a time
- [ ] Show what happens without rate limiting (overwhelming an API)

### 2.5 — Timeouts & Cancellation
- [ ] Create `app/learn/09_timeouts.py`
- [ ] Use `asyncio.wait_for()` with a timeout
- [ ] Use `asyncio.timeout()` context manager (Python 3.11+)
- [ ] Handle `asyncio.CancelledError` gracefully
- [ ] Show task cancellation with `task.cancel()`

---

## Phase 3: FastAPI — `async def` vs `def`

> [!IMPORTANT]
> This is the most critical phase. FastAPI treats `async def` and `def` endpoints **completely differently** under the hood.

### 3.1 — How FastAPI Handles Endpoints
- [ ] Create `app/routes/sync_vs_async.py` with a router
- [ ] Write a `def` endpoint that calls `time.sleep(2)` — measure concurrent request handling
- [ ] Write an `async def` endpoint that calls `asyncio.sleep(2)` — measure concurrent request handling
- [ ] **Write the WRONG way:** `async def` with `time.sleep(2)` — observe it blocks ALL other requests
- [ ] Document findings in comments:
  - `def` → FastAPI runs it in a **threadpool** automatically (safe for blocking I/O)
  - `async def` → FastAPI runs it on the **event loop** directly (you MUST not block)
  - `async def` + blocking call = **disaster** (blocks the entire server)

### 3.2 — When to Use `def` vs `async def`
- [ ] Create `app/routes/decision_guide.py`
- [ ] Endpoint using `def` + synchronous DB library (e.g., `sqlite3`) — **correct**
- [ ] Endpoint using `async def` + async HTTP client (`httpx.AsyncClient`) — **correct**
- [ ] Endpoint using `async def` + `run_in_executor` for sync library — **correct but complex**
- [ ] Add docstrings explaining the decision tree

### 3.3 — Background Tasks
- [ ] Create `app/routes/background.py`
- [ ] Use `BackgroundTasks` to send an email / write a log after returning a response
- [ ] Show both sync and async background task functions
- [ ] Demonstrate that the response returns immediately while the task runs

---

## Phase 4: Async HTTP Clients in FastAPI

### 4.1 — `httpx.AsyncClient` Basics
- [ ] Install `httpx` (`uv add httpx`)
- [ ] Create `app/routes/external_api.py`
- [ ] Make an endpoint that fetches data from a public API using `httpx.AsyncClient`
- [ ] Show the **wrong way** (creating a new client per request) vs **right way** (shared client via lifespan)

### 4.2 — Lifespan Events for Resource Management
- [ ] Refactor `app/main.py` to use `@asynccontextmanager` lifespan
- [ ] Create a shared `httpx.AsyncClient` in lifespan startup, close it in shutdown
- [ ] Store it in `app.state` and access it from endpoints
- [ ] **Key insight:** Lifespan replaces the old `@app.on_event("startup")` / `@app.on_event("shutdown")`

### 4.3 — Parallel External API Calls
- [ ] Create `app/routes/parallel_calls.py`
- [ ] Endpoint that fetches from 3 different APIs sequentially — measure time
- [ ] Refactor to use `asyncio.gather()` — measure speedup
- [ ] Add error handling: what if one API fails?

---

## Phase 5: Async Database Access

### 5.1 — SQLAlchemy Async Engine
- [ ] Install `sqlalchemy[asyncio]` and `aiosqlite` (`uv add sqlalchemy[asyncio] aiosqlite`)
- [ ] Create `app/db/engine.py` — set up `create_async_engine` with SQLite
- [ ] Create `app/db/models.py` — define a simple `Item` model
- [ ] Create `app/db/session.py` — async session factory with `async_sessionmaker`

### 5.2 — Async CRUD Operations
- [ ] Create `app/routes/items.py`
- [ ] `POST /items` — create an item using async session
- [ ] `GET /items` — list items with async query
- [ ] `GET /items/{id}` — get single item
- [ ] `PUT /items/{id}` — update item
- [ ] `DELETE /items/{id}` — delete item
- [ ] Use `async with session.begin()` for transaction management

### 5.3 — Dependency Injection with Async
- [ ] Create `app/dependencies.py`
- [ ] Write an async dependency `get_db()` that yields an async session
- [ ] Use `Depends(get_db)` in your CRUD endpoints
- [ ] Show that FastAPI properly handles async generators as dependencies

---

## Phase 6: Concurrency vs Parallelism (Advanced)

### 6.1 — Understanding the GIL
- [ ] Create `app/learn/10_gil.py`
- [ ] Benchmark CPU-bound work with threading vs multiprocessing
- [ ] Show that threads don't speed up CPU-bound work (GIL)
- [ ] Show that `ProcessPoolExecutor` does

### 6.2 — Mixing Sync and Async in FastAPI
- [ ] Create `app/routes/mixed.py`
- [ ] Call a sync function from an async endpoint using `run_in_executor`
- [ ] Call a sync function using `asyncio.to_thread()`
- [ ] Show `starlette.concurrency.run_in_threadpool` (what FastAPI uses internally for `def` endpoints)

### 6.3 — Streaming Responses
- [ ] Create `app/routes/streaming.py`
- [ ] `StreamingResponse` with an async generator — stream large data
- [ ] Server-Sent Events (SSE) with async generator
- [ ] Show how this enables real-time features without WebSockets

### 6.4 — WebSockets (Async Native)
- [ ] Create `app/routes/websocket.py`
- [ ] Build a simple WebSocket echo server
- [ ] Add a broadcast chat room using `asyncio.Queue` or a set of connections
- [ ] Handle connection/disconnection lifecycle

---

## Phase 7: Testing Async Code

### 7.1 — Pytest + `pytest-asyncio`
- [ ] Install `pytest` and `pytest-asyncio` (`uv add --dev pytest pytest-asyncio`)
- [ ] Create `tests/test_async_basics.py`
- [ ] Write tests with `@pytest.mark.asyncio` for your coroutine exercises
- [ ] Test async generators and context managers

### 7.2 — Testing FastAPI Async Endpoints
- [ ] Install `httpx` for test client (`uv add --dev httpx`)
- [ ] Create `tests/test_endpoints.py`
- [ ] Use `httpx.AsyncClient` with `ASGITransport` for async tests
- [ ] Test background tasks, streaming responses, and WebSocket endpoints
- [ ] Mock external API calls with `respx` or `unittest.mock`

---

## Phase 8: Production Patterns

### 8.1 — Middleware (Async)
- [ ] Create `app/middleware.py`
- [ ] Build custom middleware that logs request duration (async-aware)
- [ ] Add CORS middleware configuration
- [ ] Show how middleware interacts with the async lifecycle

### 8.2 — Error Handling in Async
- [ ] Create `app/routes/error_handling.py`
- [ ] Custom exception handlers that work with async
- [ ] Graceful timeout handling for slow endpoints
- [ ] Retry patterns with exponential backoff (async)

### 8.3 — Performance Monitoring
- [ ] Create `app/learn/11_profiling.py`
- [ ] Use `asyncio.get_event_loop().slow_callback_duration` to detect blocking calls
- [ ] Add logging to find endpoints that accidentally block the event loop
- [ ] Benchmark: sync vs async endpoints under load using `wrk` or `hey`

---

## Suggested File Structure (End State)

```
the-fast-and-the-asynchronous/
├── app/
│   ├── main.py                    # App entry point with lifespan
│   ├── dependencies.py            # Async dependencies
│   ├── middleware.py               # Custom async middleware
│   ├── db/
│   │   ├── engine.py              # Async SQLAlchemy engine
│   │   ├── models.py              # ORM models
│   │   └── session.py             # Async session factory
│   ├── routes/
│   │   ├── sync_vs_async.py       # Phase 3 exercises
│   │   ├── decision_guide.py      # def vs async def
│   │   ├── background.py          # Background tasks
│   │   ├── external_api.py        # httpx async client
│   │   ├── parallel_calls.py      # asyncio.gather in action
│   │   ├── items.py               # Async CRUD
│   │   ├── mixed.py               # Sync/async mixing
│   │   ├── streaming.py           # SSE & streaming
│   │   ├── websocket.py           # WebSocket endpoints
│   │   └── error_handling.py      # Async error patterns
│   └── learn/
│       ├── 01_coroutines.py
│       ├── 02_sleep_comparison.py
│       ├── 03_gather_vs_tasks.py
│       ├── 04_event_loop.py
│       ├── 05_blocking_danger.py
│       ├── 06_async_iterators.py
│       ├── 07_async_context_managers.py
│       ├── 08_semaphores.py
│       ├── 09_timeouts.py
│       ├── 10_gil.py
│       └── 11_profiling.py
├── tests/
│   ├── test_async_basics.py
│   └── test_endpoints.py
└── pyproject.toml
```

## Open Questions

1. **Depth preference** — Do you want me to implement each TODO step-by-step with you (pair programming), or would you prefer I scaffold the files with commented instructions and you fill them in yourself?
2. **Database** — The plan uses SQLite (simplest). Do you want to target PostgreSQL with `asyncpg` instead (more production-realistic)?
3. **Pace** — Want to start from Phase 1 (pure Python async) or jump straight to Phase 3 (FastAPI-specific)?
