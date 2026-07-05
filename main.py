"""PawPal+ CLI demo.

A temporary testing ground to verify the scheduling logic in the terminal
before wiring it up to the Streamlit UI. Run with:  python main.py
"""

# 1) Import our classes from the PawPal+ system module.
from pawpal_system import Owner, Pet, Task, Priority, Scheduler


def build_demo_owner() -> Owner:
    """Set up a sample owner with two pets and several tasks.

    Tasks are deliberately added out of chronological order so we can see the
    sort_by_time() method actually reorder them.
    """
    # 2) Create an owner and at least two pets.
    owner = Owner(name="Alex", available_minutes=90)
    biscuit = owner.add_pet(Pet(name="Biscuit", breed="Golden Retriever"))
    mochi = owner.add_pet(Pet(name="Mochi", breed="Tabby Cat"))

    # 3) Add tasks with start times, intentionally NOT in time order.
    biscuit.add_task(Task("Enrichment play", 45, Priority.LOW, start_time="17:30"))
    biscuit.add_task(Task("Morning walk", 30, Priority.HIGH, start_time="08:00"))
    biscuit.add_task(Task("Breakfast", 10, Priority.HIGH, start_time="07:00"))

    # Give medication at 08:15 deliberately overlaps Biscuit's 08:00-08:30 walk,
    # so we can see conflict detection fire (a conflict across two pets).
    mochi.add_task(Task("Give medication", 5, Priority.HIGH, start_time="08:15"))
    mochi.add_task(Task("Litter box cleaning", 15, Priority.MEDIUM, start_time="12:00"))

    # Mark one task done so we can demonstrate filtering by status.
    biscuit.tasks[2].mark_complete()  # Breakfast

    return owner


def print_tasks(title: str, tasks: list[Task]) -> None:
    """Print a titled list of tasks in the order given."""
    print("=" * 44)
    print(title)
    print("=" * 44)
    if not tasks:
        print("  (none)")
    else:
        for task in tasks:
            status = "done" if task.completed else "pending"
            pet_name = task.pet.name if task.pet else "?"
            print(
                f"  {task.start_time}  {task.name} "
                f"({task.duration_minutes} min) [{task.priority.name}] "
                f"for {pet_name} - {status}"
            )
    print()


def main() -> None:
    owner = build_demo_owner()
    all_tasks = owner.get_all_tasks(include_completed=True)

    # Show them as-entered (out of order) vs. sorted by time.
    print_tasks("All tasks (as entered, unsorted)", all_tasks)
    print_tasks("All tasks sorted by time", Scheduler.sort_by_time(all_tasks))

    # Filter by pet, then sort that subset by time.
    biscuit_tasks = Scheduler.filter_by_pet(all_tasks, "Biscuit")
    print_tasks(
        "Biscuit's tasks sorted by time",
        Scheduler.sort_by_time(biscuit_tasks),
    )

    # Filter by status.
    pending = Scheduler.filter_by_status(all_tasks, completed=False)
    print_tasks("Pending tasks sorted by time", Scheduler.sort_by_time(pending))

    completed = Scheduler.filter_by_status(all_tasks, completed=True)
    print_tasks("Completed tasks", completed)

    # Conflict detection: warn about any tasks scheduled at overlapping times.
    print("=" * 44)
    print("Schedule conflicts")
    print("=" * 44)
    warnings = Scheduler.conflict_warnings(all_tasks)
    if warnings:
        for warning in warnings:
            print(f"  {warning}")
    else:
        print("  No conflicts found.")
    print()


if __name__ == "__main__":
    main()
