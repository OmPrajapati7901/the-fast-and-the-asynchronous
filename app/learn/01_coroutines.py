"""
==========================================================
  LESSON 1.1 — Coroutines & await
==========================================================

KEY CONCEPTS:
  1. A regular function returns a value when called.
  2. An `async def` function returns a COROUTINE OBJECT when called — it does NOT execute.
  3. To actually RUN a coroutine, you must either:
       a) `await` it (from inside another coroutine)
       b) Pass it to `asyncio.run()` (the entry point from sync code)

  Think of a coroutine like a recipe card. Calling the function
  gives you the card. `await` is what makes someone actually cook it.

==========================================================
"""

import asyncio


# ─── PART 1: What IS a coroutine? ───────────────────────

async def say_hello() -> str:
    """A simple coroutine. `async def` makes it async."""
    print("  → Inside say_hello()")
    return "Hello from a coroutine!"


def demo_coroutine_object():
    """Show that calling an async function returns a coroutine object, not the result."""
    print("\n📌 PART 1: What is a coroutine object?\n")

    # Calling say_hello() does NOT print anything!
    # It just creates a coroutine object.
    coro = say_hello()
    print(f"  Type of say_hello(): {type(coro)}")
    print(f"  Value: {coro}")
    print("  ⚠️  Notice: 'Inside say_hello()' was NOT printed!")
    print("  The coroutine hasn't executed yet — it's just an object.\n")

    # We must close it to avoid a RuntimeWarning
    coro.close()


# ─── PART 2: Running a coroutine with asyncio.run() ────

async def demo_await():
    """Show that `await` actually executes the coroutine."""
    print("\n📌 PART 2: Running a coroutine with `await`\n")

    # NOW it executes — `await` drives the coroutine to completion
    result = await say_hello()
    print(f"  Result: {result}")
    print("  ✅ The coroutine executed because we awaited it!\n")


# ─── PART 3: Chaining coroutines ───────────────────────

async def step_1() -> str:
    print("  → Step 1: Gathering ingredients...")
    return "ingredients"


async def step_2(ingredients: str) -> str:
    print(f"  → Step 2: Cooking with {ingredients}...")
    return "cooked meal"


async def step_3(meal: str) -> str:
    print(f"  → Step 3: Serving {meal}...")
    return "served!"


async def demo_chaining():
    """Chain 3 coroutines — each awaits the previous one."""
    print("\n📌 PART 3: Chaining coroutines\n")
    print("  Coroutines execute in order when you `await` them sequentially:\n")

    result_1 = await step_1()
    result_2 = await step_2(result_1)
    result_3 = await step_3(result_2)

    print(f"\n  Final result: {result_3}")
    print("  ✅ Each step waited for the previous one to complete.\n")


# ─── PART 4: What happens WITHOUT await ─────────────────

async def demo_forgot_await():
    """Common mistake: forgetting to await."""
    print("\n📌 PART 4: What happens if you forget `await`?\n")

    # This is WRONG — we get a coroutine object, not the result
    result = say_hello()  # ← No await!
    print(f"  result = say_hello()  →  {type(result)}")
    print("  ⚠️  We got a coroutine object, not 'Hello from a coroutine!'")
    print("  Python will also show a RuntimeWarning about this.\n")

    # Clean up
    result.close()

    # This is RIGHT
    result = await say_hello()
    print(f"  result = await say_hello()  →  {result!r}")
    print("  ✅ With await, we get the actual return value.\n")


# ─── RUN ALL DEMOS ──────────────────────────────────────

async def main():
    """Run all demonstrations."""
    print("=" * 60)
    print("  LESSON 1.1 — Coroutines & await")
    print("=" * 60)

    # Part 1 is synchronous (to show the coroutine object without running it)
    demo_coroutine_object()

    # Parts 2-4 are async
    await demo_await()
    await demo_chaining()
    await demo_forgot_await()

    print("=" * 60)
    print("  KEY TAKEAWAYS")
    print("=" * 60)
    print("""
  1. `async def` defines a coroutine function
  2. Calling it returns a coroutine OBJECT (not the result)
  3. `await` drives the coroutine to completion and returns its result
  4. `asyncio.run()` is the bridge from sync → async world
  5. Forgetting `await` is the #1 beginner mistake
    """)


if __name__ == "__main__":
    asyncio.run(main())
