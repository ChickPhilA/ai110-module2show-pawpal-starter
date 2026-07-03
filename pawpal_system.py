"""PawPal+ system classes.

Skeleton generated from diagrams/uml.mmd. Implement the method bodies
incrementally — for now they are stubs so the structure matches the UML.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet care task (e.g., a walk, feeding, or medication)."""

    name: str
    duration_minutes: int
    priority: str


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    owner: "Owner"
    tasks: list[Task] = field(default_factory=list)
    age: int = 0
    breed: str = ""
    sex: str = ""
    weight: float = 0.0
    accommodations: list[str] = field(default_factory=list)


@dataclass
class Owner:
    """A pet owner, their pets, and their scheduling constraints."""

    name: str
    pets: list[Pet] = field(default_factory=list)
    available_minutes: int = 0
    preferences: list[str] = field(default_factory=list)

    def request_plan(self) -> list[Task]:
        """Ask the scheduler to build a daily plan for this owner's tasks."""
        raise NotImplementedError


class Scheduler:
    """Turns a set of tasks plus constraints into an ordered daily plan."""

    def generate_plan(
        self, tasks: list[Task], available_minutes: int
    ) -> list[Task]:
        """Return tasks ordered into a daily plan that fits the time available."""
        raise NotImplementedError
