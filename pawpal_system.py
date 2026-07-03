"""PawPal+ system classes.

Skeleton generated from diagrams/uml.mmd. Implement the method bodies
incrementally — for now most are stubs so the structure matches the UML.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class Priority(IntEnum):
    """Task priority. IntEnum so tasks can be sorted directly by importance."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    """A single pet care task (e.g., a walk, feeding, or medication)."""

    name: str
    duration_minutes: int
    priority: Priority
    # Back-reference to the pet this task belongs to. repr/compare disabled to
    # avoid infinite recursion with Pet.tasks.
    pet: "Pet | None" = field(default=None, repr=False, compare=False)


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    # Back-reference to the owner. repr/compare disabled to avoid infinite
    # recursion with Owner.pets.
    owner: "Owner" = field(repr=False, compare=False)
    tasks: list[Task] = field(default_factory=list)
    age: int = 0
    breed: str = ""
    sex: str = ""
    weight: float = 0.0
    accommodations: list[str] = field(default_factory=list)


class Scheduler:
    """Turns a set of tasks plus constraints into an ordered daily plan."""

    def generate_plan(
        self, tasks: list[Task], available_minutes: int
    ) -> list[Task]:
        """Return tasks ordered into a daily plan that fits the time available."""
        raise NotImplementedError


@dataclass
class Owner:
    """A pet owner, their pets, and their scheduling constraints."""

    name: str
    pets: list[Pet] = field(default_factory=list)
    available_minutes: int = 0
    preferences: list[str] = field(default_factory=list)
    scheduler: Scheduler = field(default_factory=Scheduler)

    def request_plan(self) -> list[Task]:
        """Gather every pet's tasks and ask the scheduler to build a plan."""
        all_tasks = [task for pet in self.pets for task in pet.tasks]
        return self.scheduler.generate_plan(all_tasks, self.available_minutes)
