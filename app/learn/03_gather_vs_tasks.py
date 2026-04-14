"""
==========================================================
  LESSON 1.3 — asyncio.gather() vs asyncio.create_task()
==========================================================

KEY CONCEPTS:
  1. `asyncio.gather()` — Run multiple coroutines concurrently,
     wait for ALL of them, and collect results in order.
  2. `asyncio.create_task()` — Schedule a coroutine to run "in the
     background" on the event loop. You decide when to await it.
  3. `asyncio.TaskGroup` (Python 3.11+) — The modern, safer
     replacement for `gather()` with structured concurrency.

  Analogy:
    - gather()      = "Hey team, do these 3 things. Nobody leaves
                       until everyone is done."
    - create_task() = "Start working on this. I'll check on you later."
    - TaskGroup     = gather() but with a safety net — if one fails,
                       ALL get cancelled automatically.

==========================================================
"""

import asyncio
import time


# ─── Helper: a simple async task ────────────────────────

async def fetch_data(source: str, duration: float) -> dict:
    """Simulate fetching data from a source."""
    print(f"  ⏳ Fetching from {source}...")
    await asyncio.sleep(duration)
    print(f"  ✅ Got data from {source}")
    return {"source": source, "data": f"result from {source}", "took": duration}


# ─── PART 1: asyncio.gather() ──────────────────────────

async def demo_gather():
    """
    gather() runs coroutines concurrently and returns results IN ORDER.
    It waits for ALL tasks to complete before returning.
    """
    print("\n📌 PART 1: asyncio.gather()\n")
    print("  Runs all coroutines concurrently, returns results in order.\n")

    start = time.perf_counter()

    # All three start at the same time!
    results = await asyncio.gather(
        fetch_data("GitHub API", 1.0),
        fetch_data("Database", 0.5),
        fetch_data("Cache", 0.2),
    )

    elapsed = time.perf_counter() - start

    print(f"\n  Results (in order of arguments, NOT completion):")
    for r in results:
        print(f"    {r}")

    print(f"\n  ⏱️  Total: {elapsed:.2f}s (limited by slowest: ~1.0s)")
    print("  💡 Results are ordered by how you passed them, not finish time.\n")


# ─── PART 2: gather() with error handling ──────────────

async def failing_task(name: str) -> str:
    """A task that raises an exception."""
    await asyncio.sleep(0.5)
    raise ValueError(f"{name} failed!")


async def demo_gather_errors():
    """
    By default, gather() raises the FIRST exception.
    With return_exceptions=True, exceptions become return values.
    """
    print("\n📌 PART 2: gather() error handling\n")

    # ── Without return_exceptions (default) ──
    print("  2a) Default: First exception propagates\n")
    try:
        results = await asyncio.gather(
            fetch_data("Good API", 0.3),
            failing_task("Bad API"),
            fetch_data("Another API", 0.4),
        )
    except ValueError as e:
        print(f"  🚨 Caught exception: {e}")
        print("  ⚠️  The other tasks may still be running/completed,")
        print("  but we lost their results!\n")

    # ── With return_exceptions=True ──
    print("  2b) return_exceptions=True: Exceptions become values\n")

    results = await asyncio.gather(
        fetch_data("Good API", 0.3),
        failing_task("Bad API"),
        fetch_data("Another API", 0.4),
        return_exceptions=True,  # ← KEY: exceptions don't crash gather()
    )

    print(f"\n  Results:")
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            print(f"    [{i}] ❌ Exception: {r}")
        else:
            print(f"    [{i}] ✅ {r}")

    print("\n  💡 return_exceptions=True lets you handle partial failures.\n")


# ─── PART 3: asyncio.create_task() ─────────────────────

async def demo_create_task():
    """
    create_task() schedules a coroutine on the event loop immediately.
    You get a Task object back that you can await later (or not).
    """
    print("\n📌 PART 3: asyncio.create_task()\n")
    print("  Schedule tasks and decide when to await them.\n")

    start = time.perf_counter()

    # Create tasks — they start running IMMEDIATELY
    task1 = asyncio.create_task(fetch_data("API Server", 1.0))
    task2 = asyncio.create_task(fetch_data("Database", 0.5))
    task3 = asyncio.create_task(fetch_data("Redis Cache", 0.2))

    print("  → All tasks created! They're already running.")
    print(f"  → task1 done? {task1.done()}")
    print(f"  → task2 done? {task2.done()}")
    print(f"  → task3 done? {task3.done()}")
    print()

    # We can do OTHER work here while tasks run...
    print("  → Doing other work while tasks run...")
    await asyncio.sleep(0.3)  # simulate other work
    print(f"  → After 0.3s — task3 done? {task3.done()} (it only needed 0.2s)")
    print()

    # Now await each task to get its result
    result1 = await task1
    result2 = await task2
    result3 = await task3

    elapsed = time.perf_counter() - start
    print(f"\n  Results: {result1['source']}, {result2['source']}, {result3['source']}")
    print(f"  ⏱️  Total: {elapsed:.2f}s")
    print("  💡 Tasks started running the moment create_task() was called,")
    print("  not when we awaited them.\n")


# ─── PART 4: Fire-and-forget pattern ──────────────────

async def log_event(event: str) -> None:
    """A background task we don't need the result from."""
    await asyncio.sleep(0.1)  # simulate writing to log
    print(f"  📝 Logged: {event}")


async def demo_fire_and_forget():
    """
    create_task() for tasks where you don't care about the result.
    WARNING: You must keep a reference or the task may be garbage collected!
    """
    print("\n📌 PART 4: Fire-and-forget with create_task()\n")

    # Keep references to prevent garbage collection!
    background_tasks: set[asyncio.Task] = set()

    for i in range(5):
        task = asyncio.create_task(log_event(f"User action #{i}"))
        background_tasks.add(task)
        # Remove task from set when it completes (cleanup)
        task.add_done_callback(background_tasks.discard)

    print(f"  Created {len(background_tasks)} background tasks")
    print("  Main code continues immediately...\n")

    # Give background tasks time to complete
    await asyncio.sleep(0.5)

    print(f"\n  Background tasks remaining: {len(background_tasks)}")
    print("  💡 Keep task references! Otherwise Python may garbage-collect them.\n")


# ─── PART 5: TaskGroup (Python 3.11+) ─────────────────

async def demo_taskgroup():
    """
    TaskGroup is the modern replacement for gather().
    Key difference: if ANY task fails, ALL others are cancelled.
    This is called "structured concurrency."
    """
    print("\n📌 PART 5: asyncio.TaskGroup (Python 3.11+)\n")
    print("  Structured concurrency: if one fails, all get cancelled.\n")

    start = time.perf_counter()

    # ── Success case ──
    print("  5a) All tasks succeed:\n")
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_data("Service A", 0.5))
        task2 = tg.create_task(fetch_data("Service B", 0.3))
        task3 = tg.create_task(fetch_data("Service C", 0.7))

    # When we exit the `async with`, all tasks are guaranteed complete
    elapsed = time.perf_counter() - start
    print(f"\n  Results: {task1.result()['source']}, {task2.result()['source']}, {task3.result()['source']}")
    print(f"  ⏱️  Total: {elapsed:.2f}s\n")

    # ── Failure case ──
    print("  5b) One task fails → all get cancelled:\n")
    try:
        async with asyncio.TaskGroup() as tg:
            task1 = tg.create_task(fetch_data("Good Service", 1.0))
            task2 = tg.create_task(failing_task("Bad Service"))
    except* ValueError as eg:
        print(f"\n  🚨 Caught ExceptionGroup: {eg.exceptions}")
        print(f"  → task1 cancelled? {task1.cancelled()}")
        print("  💡 TaskGroup cancelled the good task when the bad one failed!")
        print("  This prevents dangling tasks — much safer than gather().\n")


# ─── PART 6: gather() vs create_task() vs TaskGroup ───

async def demo_comparison():
    """Side-by-side comparison of all three approaches."""
    print("\n📌 PART 6: When to use what?\n")
    print("""
  ┌───────────────────────┬──────────────────────────────────────────┐
  │ Method                │ Use when...                              │
  ├───────────────────────┼──────────────────────────────────────────┤
  │ asyncio.gather()      │ You need ALL results, ordered.           │
  │                       │ Good for: parallel API calls.            │
  │                       │ Error handling: return_exceptions=True   │
  ├───────────────────────┼──────────────────────────────────────────┤
  │ asyncio.create_task() │ You want to start work NOW but await     │
  │                       │ it LATER. Or fire-and-forget.            │
  │                       │ Good for: background logging, preloading │
  ├───────────────────────┼──────────────────────────────────────────┤
  │ asyncio.TaskGroup     │ You want structured concurrency.         │
  │ (Python 3.11+)        │ If one fails, cancel all. SAFEST option. │
  │                       │ Good for: anything critical.             │
  └───────────────────────┴──────────────────────────────────────────┘

  RULE OF THUMB:
    → Use TaskGroup by default (Python 3.11+)
    → Use gather() when you need return_exceptions=True
    → Use create_task() for fire-and-forget or delayed awaiting
    """)


# ─── RUN ALL DEMOS ──────────────────────────────────────

async def main():
    print("=" * 60)
    print("  LESSON 1.3 — gather() vs create_task() vs TaskGroup")
    print("=" * 60)

    await demo_gather()
    await demo_gather_errors()
    await demo_create_task()
    await demo_fire_and_forget()
    await demo_taskgroup()
    await demo_comparison()

    print("=" * 60)
    print("  KEY TAKEAWAYS")
    print("=" * 60)
    print("""
  1. gather()      — Concurrent execution, ordered results, waits for all
  2. create_task() — Schedule now, await later (or never)
  3. TaskGroup     — Structured concurrency with automatic cancellation
  4. All three run on a SINGLE THREAD via the event loop
  5. Keep references to tasks to prevent garbage collection
  6. Use `except*` (ExceptionGroup) with TaskGroup errors
    """)


if __name__ == "__main__":
    asyncio.run(main())
