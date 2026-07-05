"""Tests for PawPal+ core behaviors."""

from datetime import date

from pawpal_system import (
    Frequency,
    Owner,
    Pet,
    Priority,
    Scheduler,
    Task,
)


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


# ---------------------------------------------------------------------------
# Recurring tasks: mark_complete() and _next_occurrence()
# ---------------------------------------------------------------------------


def test_daily_task_regenerates_next_day():
    """Completing a DAILY task should spawn a fresh copy due one day later."""
    pet = Pet("Biscuit")
    task = pet.add_task(
        Task(
            "Morning walk",
            30,
            Priority.HIGH,
            frequency=Frequency.DAILY,
            due_date=date(2024, 1, 1),
        )
    )

    task.mark_complete()

    assert len(pet.tasks) == 2
    original, regenerated = pet.tasks
    assert original.completed is True
    assert regenerated.completed is False
    assert regenerated.due_date == date(2024, 1, 2)
    assert regenerated.name == "Morning walk"
    assert regenerated.pet is pet


def test_weekly_task_regenerates_seven_days_later():
    """Completing a WEEKLY task should spawn a copy due seven days later."""
    pet = Pet("Biscuit")
    task = pet.add_task(
        Task(
            "Bath",
            45,
            Priority.MEDIUM,
            frequency=Frequency.WEEKLY,
            due_date=date(2024, 1, 1),
        )
    )

    task.mark_complete()

    regenerated = pet.tasks[1]
    assert regenerated.due_date == date(2024, 1, 8)


def test_once_task_does_not_regenerate():
    """Completing a ONCE task should not create a follow-up occurrence."""
    pet = Pet("Biscuit")
    task = pet.add_task(
        Task("Vet visit", 60, Priority.HIGH, frequency=Frequency.ONCE)
    )

    task.mark_complete()

    assert len(pet.tasks) == 1
    assert pet.tasks[0].completed is True


def test_recurring_task_without_pet_does_not_crash():
    """A DAILY task with no linked pet completes without spawning a copy."""
    task = Task("Morning walk", 30, Priority.HIGH, frequency=Frequency.DAILY)

    task.mark_complete()  # should not raise

    assert task.completed is True


def test_daily_task_regeneration_handles_leap_year():
    """DAILY rollover across a leap day should land on Feb 29."""
    pet = Pet("Biscuit")
    task = pet.add_task(
        Task(
            "Feeding",
            10,
            Priority.HIGH,
            frequency=Frequency.DAILY,
            due_date=date(2024, 2, 28),
        )
    )

    task.mark_complete()

    assert pet.tasks[1].due_date == date(2024, 2, 29)


# ---------------------------------------------------------------------------
# Pet task queries
# ---------------------------------------------------------------------------


def test_pending_tasks_excludes_completed():
    """pending_tasks() should return only not-yet-completed tasks."""
    pet = Pet("Biscuit")
    done = pet.add_task(Task("Walk", 30, Priority.HIGH, frequency=Frequency.ONCE))
    pet.add_task(Task("Feed", 10, Priority.MEDIUM))
    done.mark_complete()

    pending = pet.pending_tasks()

    assert len(pending) == 1
    assert pending[0].name == "Feed"


def test_pet_with_no_tasks_returns_empty():
    """A pet with no tasks should report no pending tasks."""
    pet = Pet("Biscuit")

    assert pet.pending_tasks() == []


# ---------------------------------------------------------------------------
# Owner aggregation
# ---------------------------------------------------------------------------


def test_get_all_tasks_flattens_across_pets():
    """get_all_tasks() should gather pending tasks from every pet."""
    owner = Owner("Ada")
    dog = owner.add_pet(Pet("Biscuit"))
    cat = owner.add_pet(Pet("Mochi"))
    dog.add_task(Task("Walk", 30, Priority.HIGH))
    cat.add_task(Task("Litter", 5, Priority.MEDIUM))

    all_tasks = owner.get_all_tasks()

    assert len(all_tasks) == 2


def test_get_all_tasks_excludes_completed_by_default():
    """By default get_all_tasks() omits completed tasks."""
    owner = Owner("Ada")
    dog = owner.add_pet(Pet("Biscuit"))
    done = dog.add_task(Task("Walk", 30, Priority.HIGH, frequency=Frequency.ONCE))
    dog.add_task(Task("Feed", 10, Priority.MEDIUM))
    done.mark_complete()

    assert len(owner.get_all_tasks()) == 1
    assert len(owner.get_all_tasks(include_completed=True)) >= 2


def test_owner_with_no_pets_has_no_tasks():
    """An owner with no pets should aggregate to an empty task list."""
    owner = Owner("Ada")

    assert owner.get_all_tasks() == []


# ---------------------------------------------------------------------------
# Scheduler: sorting
# ---------------------------------------------------------------------------


def test_sort_tasks_high_priority_first():
    """sort_tasks() should place higher-priority tasks before lower ones."""
    low = Task("Groom", 20, Priority.LOW)
    high = Task("Meds", 5, Priority.HIGH)

    ordered = Scheduler.sort_tasks([low, high])

    assert ordered[0] is high
    assert ordered[1] is low


def test_sort_tasks_breaks_ties_by_shorter_duration():
    """Within the same priority, shorter tasks should come first."""
    long_task = Task("Long walk", 60, Priority.HIGH)
    short_task = Task("Quick feed", 10, Priority.HIGH)

    ordered = Scheduler.sort_tasks([long_task, short_task])

    assert ordered[0] is short_task
    assert ordered[1] is long_task


def test_sort_tasks_does_not_mutate_input():
    """sort_tasks() should return a new list, leaving the input untouched."""
    tasks = [Task("Groom", 20, Priority.LOW), Task("Meds", 5, Priority.HIGH)]
    original_order = list(tasks)

    Scheduler.sort_tasks(tasks)

    assert tasks == original_order


def test_sort_by_time_handles_non_padded_times():
    """sort_by_time() should order by clock time, not string comparison."""
    afternoon = Task("Walk", 30, Priority.HIGH, start_time="13:00")
    morning = Task("Feed", 10, Priority.HIGH, start_time="9:00")

    ordered = Scheduler.sort_by_time([afternoon, morning])

    assert ordered[0] is morning
    assert ordered[1] is afternoon


# ---------------------------------------------------------------------------
# Scheduler: generate_plan (time budget)
# ---------------------------------------------------------------------------


def test_generate_plan_includes_tasks_that_fit():
    """A plan should include tasks whose total duration fits the budget."""
    scheduler = Scheduler()
    tasks = [
        Task("Walk", 30, Priority.HIGH),
        Task("Feed", 10, Priority.MEDIUM),
    ]

    plan = scheduler.generate_plan(tasks, available_minutes=60)

    assert len(plan) == 2


def test_generate_plan_task_equal_to_budget_is_included():
    """A task exactly filling the remaining budget should be included (<=)."""
    scheduler = Scheduler()
    tasks = [Task("Walk", 30, Priority.HIGH)]

    plan = scheduler.generate_plan(tasks, available_minutes=30)

    assert plan == tasks


def test_generate_plan_skips_oversized_but_keeps_later_fitting_tasks():
    """A task too big is skipped, but smaller later tasks still fit (greedy)."""
    scheduler = Scheduler()
    big = Task("Long hike", 120, Priority.HIGH)
    small = Task("Feed", 10, Priority.HIGH)

    plan = scheduler.generate_plan([big, small], available_minutes=30)

    assert big not in plan
    assert small in plan


def test_generate_plan_zero_budget_returns_empty():
    """With no available minutes, the plan should be empty."""
    scheduler = Scheduler()
    tasks = [Task("Walk", 30, Priority.HIGH)]

    assert scheduler.generate_plan(tasks, available_minutes=0) == []


def test_generate_plan_prioritizes_high_under_tight_budget():
    """With a tight budget, higher-priority tasks should win the slot."""
    scheduler = Scheduler()
    low = Task("Groom", 30, Priority.LOW)
    high = Task("Meds", 30, Priority.HIGH)

    # low is listed first, but only one 30-min task fits.
    plan = scheduler.generate_plan([low, high], available_minutes=30)

    assert plan == [high]


# ---------------------------------------------------------------------------
# Scheduler: filtering
# ---------------------------------------------------------------------------


def test_filter_by_pet_is_case_insensitive():
    """filter_by_pet() should match pet names regardless of case."""
    dog = Pet("Biscuit")
    cat = Pet("Mochi")
    dog_task = dog.add_task(Task("Walk", 30, Priority.HIGH))
    cat.add_task(Task("Litter", 5, Priority.MEDIUM))

    result = Scheduler.filter_by_pet([dog_task, *cat.tasks], "BISCUIT")

    assert result == [dog_task]


def test_filter_by_pet_skips_tasks_without_pet():
    """Tasks with no linked pet should be excluded from pet filtering."""
    orphan = Task("Walk", 30, Priority.HIGH)  # no pet linked

    result = Scheduler.filter_by_pet([orphan], "Biscuit")

    assert result == []


def test_filter_by_status_splits_done_and_pending():
    """filter_by_status() should separate completed from pending tasks."""
    done = Task("Walk", 30, Priority.HIGH, completed=True)
    pending = Task("Feed", 10, Priority.MEDIUM)
    tasks = [done, pending]

    assert Scheduler.filter_by_status(tasks, completed=True) == [done]
    assert Scheduler.filter_by_status(tasks, completed=False) == [pending]


# ---------------------------------------------------------------------------
# Scheduler: conflict detection
# ---------------------------------------------------------------------------


def test_detect_conflicts_flags_overlapping_tasks():
    """Two tasks overlapping in time on the same day should conflict."""
    day = date(2024, 1, 1)
    walk = Task("Walk", 60, Priority.HIGH, start_time="08:00", due_date=day)
    feed = Task("Feed", 30, Priority.HIGH, start_time="08:30", due_date=day)

    conflicts = Scheduler.detect_conflicts([walk, feed])

    assert len(conflicts) == 1


def test_detect_conflicts_back_to_back_do_not_conflict():
    """A task ending exactly when the next begins should NOT conflict."""
    day = date(2024, 1, 1)
    first = Task("Walk", 30, Priority.HIGH, start_time="08:00", due_date=day)
    second = Task("Feed", 30, Priority.HIGH, start_time="08:30", due_date=day)

    assert Scheduler.detect_conflicts([first, second]) == []


def test_detect_conflicts_ignores_different_days():
    """Overlapping times on different days should not conflict."""
    monday = Task("Walk", 60, Priority.HIGH, start_time="08:00",
                  due_date=date(2024, 1, 1))
    tuesday = Task("Feed", 60, Priority.HIGH, start_time="08:00",
                   due_date=date(2024, 1, 2))

    assert Scheduler.detect_conflicts([monday, tuesday]) == []


def test_detect_conflicts_spans_pets():
    """Two different pets' tasks at the same time still conflict (one owner)."""
    day = date(2024, 1, 1)
    dog = Pet("Biscuit")
    cat = Pet("Mochi")
    dog_task = dog.add_task(
        Task("Walk", 60, Priority.HIGH, start_time="08:00", due_date=day)
    )
    cat_task = cat.add_task(
        Task("Play", 60, Priority.HIGH, start_time="08:30", due_date=day)
    )

    assert len(Scheduler.detect_conflicts([dog_task, cat_task])) == 1


def test_detect_conflicts_skips_unparseable_times():
    """Tasks with an unparseable start_time should be skipped, not raise."""
    day = date(2024, 1, 1)
    good = Task("Walk", 60, Priority.HIGH, start_time="08:00", due_date=day)
    bad = Task("Feed", 30, Priority.HIGH, start_time="noon", due_date=day)

    assert Scheduler.detect_conflicts([good, bad]) == []


def test_conflict_warnings_are_generated_for_overlaps():
    """conflict_warnings() should produce a message per detected conflict."""
    day = date(2024, 1, 1)
    dog = Pet("Biscuit")
    walk = dog.add_task(
        Task("Walk", 60, Priority.HIGH, start_time="08:00", due_date=day)
    )
    feed = dog.add_task(
        Task("Feed", 30, Priority.HIGH, start_time="08:30", due_date=day)
    )

    warnings = Scheduler.conflict_warnings([walk, feed])

    assert len(warnings) == 1
    assert "Biscuit" in warnings[0]


def test_conflict_warnings_empty_when_no_conflicts():
    """No conflicts should yield an empty warnings list."""
    day = date(2024, 1, 1)
    first = Task("Walk", 30, Priority.HIGH, start_time="08:00", due_date=day)
    second = Task("Feed", 30, Priority.HIGH, start_time="09:00", due_date=day)

    assert Scheduler.conflict_warnings([first, second]) == []
