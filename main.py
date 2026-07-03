"""PawPal+ CLI demo.

A temporary testing ground to verify the scheduling logic in the terminal
before wiring it up to the Streamlit UI. Run with:  python main.py
"""

# 1) Import our classes from the PawPal+ system module.
from pawpal_system import Owner, Pet, Task, Priority


def build_demo_owner() -> Owner:
    """Set up a sample owner with two pets and several tasks."""
    # 2) Create an owner and at least two pets.
    owner = Owner(name="Alex", available_minutes=90)
    biscuit = owner.add_pet(Pet(name="Biscuit", breed="Golden Retriever"))
    mochi = owner.add_pet(Pet(name="Mochi", breed="Tabby Cat"))

    # 3) Add at least three tasks with different durations to those pets.
    biscuit.add_task(Task("Morning walk", 30, Priority.HIGH))
    biscuit.add_task(Task("Breakfast", 10, Priority.HIGH))
    biscuit.add_task(Task("Enrichment play", 45, Priority.LOW))

    mochi.add_task(Task("Give medication", 5, Priority.HIGH))
    mochi.add_task(Task("Litter box cleaning", 15, Priority.MEDIUM))

    return owner


def print_schedule(owner: Owner) -> None:
    """Ask the scheduler for a plan and print Today's Schedule."""
    plan = owner.request_plan()

    print("=" * 40)
    print(f"Today's Schedule for {owner.name}")
    print(f"(Time available: {owner.available_minutes} min)")
    print("=" * 40)

    if not plan:
        print("  No tasks scheduled.")
    else:
        total = 0
        for task in plan:
            total += task.duration_minutes
            print(
                f"  - {task.name} ({task.duration_minutes} min) "
                f"[{task.priority.name}] for {task.pet.name}"
            )
        print("-" * 40)
        print(f"  Total scheduled time: {total} min")


def main() -> None:
    owner = build_demo_owner()
    print_schedule(owner)


if __name__ == "__main__":
    main()
