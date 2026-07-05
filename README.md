# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

========================================
Today's Schedule for Alex
(Time available: 90 min)
========================================
  - Give medication (5 min) [HIGH] for Mochi
  - Breakfast (10 min) [HIGH] for Biscuit
  - Morning walk (30 min) [HIGH] for Biscuit
  - Litter box cleaning (15 min) [MEDIUM] for Mochi
----------------------------------------
  Total scheduled time: 60 min

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

PawPal+ goes beyond a flat task list with several scheduling behaviors. Each is
implemented in `pawpal_system.py` and named below.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_tasks()` | Chronological order by `"HH:MM"` start time, or by priority then duration |
| Filtering | `Scheduler.filter_by_pet()`, `Scheduler.filter_by_status()` | Narrow tasks to one pet or to pending vs. completed |
| Conflict detection | `Scheduler.detect_conflicts()`, `Scheduler.conflict_warnings()` | Flags tasks whose time windows overlap on the same day |
| Recurring tasks | `Task.mark_complete()`, `Task._next_occurrence()` | Completing a daily/weekly task spawns its next occurrence |

### Sorting behavior

- **`Scheduler.sort_by_time()`** orders tasks chronologically by their `"HH:MM"`
  `start_time`. The sort key splits `"HH:MM"` into an `(hour, minute)` tuple of
  ints, so times sort correctly even when a value isn't zero-padded
  (`"9:00"` still comes before `"13:00"`). It returns a new list and never
  mutates its input.
- **`Scheduler.sort_tasks()`** provides the alternative ordering used by the
  planner: by priority (high first), breaking ties by shorter duration.

### Filtering behavior

- **`Scheduler.filter_by_pet(tasks, pet_name)`** returns only the tasks
  belonging to a given pet. Matching is case-insensitive and tasks with no
  linked pet are safely skipped.
- **`Scheduler.filter_by_status(tasks, completed)`** returns only the tasks
  matching a completion state — `completed=False` for pending, `completed=True`
  for done.

Both filters take and return a task list, so they compose with each other and
with the sort methods, e.g. `sort_by_time(filter_by_status(filter_by_pet(tasks,
"Biscuit"), completed=False))`.

### Conflict detection logic

- **`Scheduler.detect_conflicts(tasks)`** returns every pair of tasks that
  overlap in time on the same day. Each task occupies the window
  `[start, start + duration)`, and two tasks conflict when
  `start_a < end_b and start_b < end_a`. This treats **back-to-back** tasks
  (one ending exactly as the next begins) as *not* conflicting. Conflicts are
  detected across all tasks regardless of pet, since one owner cannot do two
  overlapping tasks at once. Tasks with an unparseable `start_time` are skipped
  rather than crashing.
- **`Scheduler.conflict_warnings(tasks)`** is a lightweight wrapper that turns
  those pairs into human-readable warning strings for the CLI or UI, returning
  an empty list when there are no conflicts.

### Recurring task logic

- **`Task.mark_complete()`** — when a `DAILY` or `WEEKLY` task linked to a pet is
  completed, a fresh, incomplete copy is automatically added to that pet for the
  next occurrence. `ONCE` tasks simply complete and are not regenerated.
- **`Task._next_occurrence()`** builds that copy, advancing the `due_date` with
  `datetime.timedelta` (`DAILY` → +1 day, `WEEKLY` → +7 days), which handles
  month and year rollovers accurately.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
