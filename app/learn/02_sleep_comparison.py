"""
==========================================================
  LESSON 1.2 — asyncio.sleep() vs time.sleep()
==========================================================

KEY CONCEPTS:
  1. `time.sleep()` BLOCKS the entire thread. Nothing else runs.
  2. `asyncio.sleep()` YIELDS control back to the event loop.
     While one task sleeps, others can run.
  3. This is the core superpower of async: cooperative multitasking.

  Analogy:
    - `time.sleep()` = You stand at the oven staring at your pizza
      for 10 minutes. Nobody else can use the kitchen.
    - `asyncio.sleep()` = You put the pizza in the oven, SET A TIMER,
      and go do laundry. When the timer rings, you come back.

==========================================================
"""

import asyncio
import time


# ─── PART 1: Sequential with time.sleep() (SLOW) ───────

def sync_task(name: str, duration: int) -> str:
    """A blocking task that uses time.sleep()."""
    print(f"  ⏳ [{name}] Starting... (will block for {duration}s)")
    time.sleep(duration)  # ← BLOCKS the entire thread!
    print(f"  ✅ [{name}] Done after {duration}s")
    return f"{name} result"


def demo_sequential_blocking():
    """Run 3 blocking tasks — they execute one after another."""
    print("\n📌 PART 1: Sequential blocking with time.sleep()")
    print("  Each task BLOCKS — nothing else can run until it finishes.\n")

    start = time.perf_counter()

    sync_task("Download file", 1)
    sync_task("Query database", 1)
    sync_task("Call external API", 1)

    elapsed = time.perf_counter() - start
    print(f"\n  ⏱️  Total time: {elapsed:.2f}s (expected ~3s)")
    print("  💡 Each task waited for the previous one to finish.\n")


# ─── PART 2: Concurrent with asyncio.sleep() (FAST) ────

async def async_task(name: str, duration: int) -> str:
    """A non-blocking task that uses asyncio.sleep()."""
    print(f"  ⏳ [{name}] Starting... (will sleep for {duration}s)")
    await asyncio.sleep(duration)  # ← YIELDS control to event loop!
    print(f"  ✅ [{name}] Done after {duration}s")
    return f"{name} result"


async def demo_concurrent_async():
    """Run 3 async tasks concurrently — they overlap!"""
    print("\n📌 PART 2: Concurrent with asyncio.sleep() + gather()")
    print("  All tasks start together — while one sleeps, others run.\n")

    start = time.perf_counter()

    # asyncio.gather() runs all three coroutines CONCURRENTLY
    results = await asyncio.gather(
        async_task("Download file", 1),
        async_task("Query database", 1),
        async_task("Call external API", 1),
    )

    elapsed = time.perf_counter() - start
    print(f"\n  ⏱️  Total time: {elapsed:.2f}s (expected ~1s)")
    print(f"  📦 Results: {results}")
    print("  💡 All 3 tasks ran at the SAME TIME!\n")


# ─── PART 3: The WRONG way — blocking inside async ─────

async def bad_async_task(name: str, duration: int) -> str:
    """WRONG: Using time.sleep() inside async def."""
    print(f"  ⏳ [{name}] Starting...")
    time.sleep(duration)  # ← BLOCKS the event loop! Other tasks can't run!
    print(f"  ✅ [{name}] Done after {duration}s")
    return f"{name} result"


async def demo_blocking_inside_async():
    """Show what happens when you use time.sleep() inside async def."""
    print("\n📌 PART 3: THE WRONG WAY — time.sleep() inside async def")
    print("  ⚠️  Even with gather(), tasks run sequentially because")
    print("  time.sleep() blocks the event loop!\n")

    start = time.perf_counter()

    results = await asyncio.gather(
        bad_async_task("Download file", 1),
        bad_async_task("Query database", 1),
        bad_async_task("Call external API", 1),
    )

    elapsed = time.perf_counter() - start
    print(f"\n  ⏱️  Total time: {elapsed:.2f}s (expected ~3s, NOT ~1s!)")
    print(f"  📦 Results: {results}")
    print("  🚨 time.sleep() BLOCKED the event loop — no concurrency!\n")


# ─── PART 4: Visualizing the timeline ──────────────────

async def timed_task(name: str, duration: float, start_time: float) -> None:
    """Show exact timestamps to visualize interleaving."""
    t = time.perf_counter() - start_time
    print(f"  [{t:5.2f}s] {name}: started")

    await asyncio.sleep(duration)

    t = time.perf_counter() - start_time
    print(f"  [{t:5.2f}s] {name}: finished")


async def demo_timeline():
    """Visualize how tasks interleave on the event loop."""
    print("\n📌 PART 4: Visualizing the timeline")
    print("  Watch the timestamps — tasks overlap!\n")

    start = time.perf_counter()

    await asyncio.gather(
        timed_task("Task A (0.5s)", 0.5, start),
        timed_task("Task B (1.0s)", 1.0, start),
        timed_task("Task C (1.5s)", 1.5, start),
    )

    elapsed = time.perf_counter() - start
    print(f"\n  ⏱️  Total time: {elapsed:.2f}s (expected ~1.5s, not 3.0s)")
    print("""
  Timeline visualization:

  0.0s    0.5s    1.0s    1.5s
  |-------|-------|-------|
  [=Task A=]
  [=====Task B=====]
  [========Task C========]

  All three ran on a SINGLE thread! No threads, no processes.
  The event loop switched between them at each `await` point.
    """)


# ─── RUN ALL DEMOS ──────────────────────────────────────

async def main():
    print("=" * 60)
    print("  LESSON 1.2 — asyncio.sleep() vs time.sleep()")
    print("=" * 60)

    # Part 1: blocking (sync)
    demo_sequential_blocking()

    # Part 2: concurrent (async, correct)
    await demo_concurrent_async()

    # Part 3: the WRONG way (async with blocking sleep)
    await demo_blocking_inside_async()

    # Part 4: visualize the timeline
    await demo_timeline()

    print("=" * 60)
    print("  KEY TAKEAWAYS")
    print("=" * 60)
    print("""
  1. time.sleep()    → BLOCKS the thread. Nothing else runs.
  2. asyncio.sleep() → YIELDS to the event loop. Other tasks run.
  3. asyncio.gather() runs multiple coroutines CONCURRENTLY.
  4. NEVER use time.sleep() inside async def — it defeats
     the entire purpose and blocks ALL other async tasks.

  ┌────────────────────────────────────────────────────────┐
  │  THE RULE: Inside `async def`, every I/O operation     │
  │  must be `await`-ed using an async-compatible library. │
  │  If it's not async-compatible, it will BLOCK.          │
  └────────────────────────────────────────────────────────┘

  This is why FastAPI cares about `def` vs `async def` — but
  we'll get to that in Phase 3!
    """)


if __name__ == "__main__":
    asyncio.run(main())
