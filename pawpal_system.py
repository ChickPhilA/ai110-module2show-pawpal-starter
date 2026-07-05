"""PawPal+ system classes.

The "brain" of PawPal+. These classes model owners, pets, and care tasks,
and the Scheduler organizes those tasks into a daily plan. Built CLI-first:
this logic is meant to work and be testable on its own, before any UI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import IntEnum


class Priority(IntEnum):
    """Task priority. IntEnum so tasks can be sorted directly by importance."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Frequency(IntEnum):
    """How often a task recurs."""

    ONCE = 0
    DAILY = 1
    WEEKLY = 2


@dataclass
class Task:
    """A single pet care activity (e.g., a walk, feeding, or medication)."""

    name: str
    duration_minutes: int
    priority: Priority
    frequency: Frequency = Frequency.DAILY
    # When the task should start, as a 24-hour "HH:MM" string (e.g. "08:30").
    # Kept zero-padded so it can be sorted and compared reliably.
    start_time: str = "00:00"
    # The calendar day this task is due. Defaults to today; recurring tasks
    # advance this when their next occurrence is created.
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    # Back-reference to the pet this task belongs to. repr/compare disabled to
    # avoid infinite recursion with Pet.tasks.
    pet: "Pet | None" = field(default=None, repr=False, compare=False)

    def mark_complete(self) -> None:
        """Mark this task as completed.

        If the task recurs (DAILY or WEEKLY) and is linked to a pet, a fresh,
        incomplete copy is automatically added to that pet for the next
        occurrence. ONCE tasks simply complete and are not regenerated.
        """
        self.completed = True
        if self.frequency in (Frequency.DAILY, Frequency.WEEKLY) and self.pet is not None:
            self.pet.add_task(self._next_occurrence())

    def _next_occurrence(self) -> "Task":
        """Build a fresh, incomplete copy of this task for its next occurrence.

        Carries over everything that defines the task (name, duration,
        priority, frequency, start_time) but resets completion and advances the
        due date: DAILY -> +1 day, WEEKLY -> +7 days. timedelta handles month
        and year rollovers (and leap years) accurately. The pet link is left
        unset here; Pet.add_task() wires it up when the copy is attached.
        """
        if self.frequency == Frequency.WEEKLY:
            next_due = self.due_date + timedelta(weeks=1)
        else:  # DAILY
            next_due = self.due_date + timedelta(days=1)

        return Task(
            name=self.name,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            start_time=self.start_time,
            due_date=next_due,
            completed=False,
        )

    def mark_incomplete(self) -> None:
        """Mark this task as not yet completed."""
        self.completed = False


@dataclass
class Pet:
    """A pet, its details, and the care tasks that belong to it."""

    name: str
    # Back-reference to the owner. Set via Owner.add_pet(). repr/compare
    # disabled to avoid infinite recursion with Owner.pets.
    owner: "Owner | None" = field(default=None, repr=False, compare=False)
    tasks: list[Task] = field(default_factory=list)
    age: int = 0
    breed: str = ""
    sex: str = ""
    weight: float = 0.0
    accommodations: list[str] = field(default_factory=list)

    def add_task(self, task: Task) -> Task:
        """Attach a task to this pet and link it back to the pet."""
        task.pet = self
        self.tasks.append(task)
        return task

    def pending_tasks(self) -> list[Task]:
        """Return this pet's tasks that are not yet completed."""
        return [task for task in self.tasks if not task.completed]


@dataclass
class Owner:
    """A pet owner. Manages multiple pets and exposes all of their tasks."""

    name: str
    pets: list[Pet] = field(default_factory=list)
    available_minutes: int = 0
    preferences: list[str] = field(default_factory=list)
    scheduler: "Scheduler" = field(default_factory=lambda: Scheduler())

    def add_pet(self, pet: Pet) -> Pet:
        """Add a pet to this owner and link it back to the owner."""
        pet.owner = self
        self.pets.append(pet)
        return pet

    def get_all_tasks(self, include_completed: bool = False) -> list[Task]:
        """Flatten every pet's tasks into one list.

        By default only pending (not-yet-completed) tasks are returned, since
        those are what the scheduler needs to plan.
        """
        all_tasks: list[Task] = []
        for pet in self.pets:
            for task in pet.tasks:
                if include_completed or not task.completed:
                    all_tasks.append(task)
        return all_tasks

    def request_plan(self) -> list[Task]:
        """Gather every pet's pending tasks and ask the scheduler for a plan."""
        return self.scheduler.generate_plan(
            self.get_all_tasks(), self.available_minutes
        )


class Scheduler:
    """The brain: organizes tasks into a daily plan that fits the time budget."""

    def generate_plan(
        self, tasks: list[Task], available_minutes: int
    ) -> list[Task]:
        """Return an ordered daily plan.

        Strategy:
          1. Sort tasks by priority (high first), breaking ties by shorter
             duration so more high-value tasks can fit.
          2. Greedily include tasks in that order while they fit within the
             available time budget; skip any task that would overflow it.
        """
        ordered = self.sort_tasks(tasks)

        plan: list[Task] = []
        remaining = available_minutes
        for task in ordered:
            if task.duration_minutes <= remaining:
                plan.append(task)
                remaining -= task.duration_minutes
        return plan

    @staticmethod
    def sort_tasks(tasks: list[Task]) -> list[Task]:
        """Sort by priority (high first), then by shorter duration first."""
        return sorted(
            tasks,
            key=lambda task: (-task.priority, task.duration_minutes),
        )

    @staticmethod
    def sort_by_time(tasks: list[Task]) -> list[Task]:
        """Return tasks ordered chronologically by their "HH:MM" start_time.

        The key splits "HH:MM" into an (hour, minute) tuple of ints, so times
        sort correctly even if a value isn't zero-padded (e.g. "9:00" still
        comes before "13:00"). Returns a new list; the input is not mutated.
        """
        return sorted(
            tasks,
            key=lambda task: tuple(int(part) for part in task.start_time.split(":")),
        )

    @staticmethod
    def filter_by_pet(tasks: list[Task], pet_name: str) -> list[Task]:
        """Return only the tasks belonging to the pet with the given name.

        Matching is case-insensitive. Tasks with no linked pet are skipped.
        """
        target = pet_name.strip().lower()
        return [
            task
            for task in tasks
            if task.pet is not None and task.pet.name.lower() == target
        ]

    @staticmethod
    def filter_by_status(tasks: list[Task], completed: bool) -> list[Task]:
        """Return only the tasks matching the given completion status.

        Pass completed=False for pending tasks, completed=True for done ones.
        """
        return [task for task in tasks if task.completed == completed]

    @staticmethod
    def _minutes_since_midnight(hhmm: str) -> int | None:
        """Convert an "HH:MM" time string into minutes since midnight.

        Returns None if the value isn't a parseable "HH:MM" time, so callers
        can skip it instead of crashing on bad input.
        """
        try:
            hours, minutes = (int(part) for part in hhmm.split(":"))
        except (ValueError, AttributeError):
            return None
        return hours * 60 + minutes

    @staticmethod
    def detect_conflicts(tasks: list[Task]) -> list[tuple[Task, Task]]:
        """Return every pair of tasks that overlap in time on the same day.

        Two tasks conflict when they share a due_date and their time windows
        overlap, where a task occupies [start, start + duration). The overlap
        test (start_a < end_b and start_b < end_a) treats back-to-back tasks
        (one ending exactly as the next begins) as NOT conflicting.

        Conflicts are detected across all tasks regardless of pet: a single
        owner cannot carry out two overlapping tasks at once. Tasks whose
        start_time can't be parsed are skipped rather than raising.
        """
        conflicts: list[tuple[Task, Task]] = []
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                first, second = tasks[i], tasks[j]
                if first.due_date != second.due_date:
                    continue
                start_a = Scheduler._minutes_since_midnight(first.start_time)
                start_b = Scheduler._minutes_since_midnight(second.start_time)
                if start_a is None or start_b is None:
                    continue  # skip unparseable times instead of crashing
                end_a = start_a + first.duration_minutes
                end_b = start_b + second.duration_minutes
                if start_a < end_b and start_b < end_a:
                    conflicts.append((first, second))
        return conflicts

    @staticmethod
    def conflict_warnings(tasks: list[Task]) -> list[str]:
        """Return human-readable warning messages for any scheduling conflicts.

        A lightweight wrapper over detect_conflicts(): instead of raw task
        pairs it returns friendly strings suitable for printing in the CLI or
        showing in the UI. An empty list means no conflicts were found.
        """
        warnings: list[str] = []
        for first, second in Scheduler.detect_conflicts(tasks):
            pet_a = first.pet.name if first.pet else "Unknown pet"
            pet_b = second.pet.name if second.pet else "Unknown pet"
            warnings.append(
                f"⚠️ Conflict on {first.due_date}: "
                f"'{first.name}' at {first.start_time} ({pet_a}) overlaps "
                f"'{second.name}' at {second.start_time} ({pet_b})."
            )
        return warnings