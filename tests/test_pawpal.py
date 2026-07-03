"""Tests for PawPal+ core behaviors."""

from pawpal_system import Pet, Task, Priority


def test_task_starts_incomplete():
    """A new task should default to not completed."""
    task = Task("Morning walk", 30, Priority.HIGH)
    assert task.completed is False


def test_mark_complete_sets_completed_true():
    """Calling mark_complete() should flip the task's status to completed."""
    task = Task("Morning walk", 30, Priority.HIGH)

    task.mark_complete()

    assert task.completed is True


def test_mark_incomplete_sets_completed_false():
    """Calling mark_incomplete() should flip a completed task back to pending."""
    task = Task("Morning walk", 30, Priority.HIGH, completed=True)

    task.mark_incomplete()

    assert task.completed is False


def test_add_task_increases_pet_task_count():
    """Adding a task to a pet should increase that pet's task count by one."""
    pet = Pet("Biscuit")
    assert len(pet.tasks) == 0  # a new pet starts with no tasks

    pet.add_task(Task("Morning walk", 30, Priority.HIGH))

    assert len(pet.tasks) == 1

    pet.add_task(Task("Feeding", 10, Priority.HIGH))

    assert len(pet.tasks) == 2
