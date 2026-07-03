"""PawPal+ system classes.

The "brain" of PawPal+. These classes model owners, pets, and care tasks,
and the Scheduler organizes those tasks into a daily plan. Built CLI-first:
this logic is meant to work and be testable on its own, before any UI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
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
    completed: bool = False
    # Back-reference to the pet this task belongs to. repr/compare disabled to
    # avoid infinite recursion with Pet.tasks.
    pet: "Pet | None" = field(default=None, repr=False, compare=False)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

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
    