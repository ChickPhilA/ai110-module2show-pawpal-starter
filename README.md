# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## ✨ Features

The scheduling algorithms below are implemented in [`pawpal_system.py`](pawpal_system.py)
and surfaced in the Streamlit UI. See [Smarter Scheduling](#-smarter-scheduling)
for the full logic behind each.

- **Priority-based day planning** — a greedy planner sorts tasks by priority
  (then shorter duration) and packs as many as fit a time budget
  (`Scheduler.generate_plan()`).
- **Sorting by time** — orders tasks chronologically by their `"HH:MM"` start
  time, tolerating non-zero-padded values (`Scheduler.sort_by_time()`).
- **Sorting by priority** — high priority first, ties broken by shorter duration
  (`Scheduler.sort_tasks()`).
- **Filtering** — narrow tasks to a single pet (case-insensitive) or to pending
  vs. completed (`Scheduler.filter_by_pet()`, `Scheduler.filter_by_status()`).
- **Conflict warnings** — flags any two tasks whose time windows overlap on the
  same day, as human-readable messages
  (`Scheduler.detect_conflicts()`, `Scheduler.conflict_warnings()`).
- **Daily & weekly recurrence** — completing a recurring task auto-spawns its
  next occurrence with an advanced due date
  (`Task.mark_complete()`, `Task._next_occurrence()`).
- **Automatic end times** — each task computes its end time from
  `start_time + duration`, wrapping safely around midnight (`Task.end_time`).

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
python -m pytest

# Run with coverage:
python -m pytest --cov
```

Sample test output:

```
(Check the Testing PawPal+ category for a sample test with more details on the logic it runs and covers.)
```

## 📐 Smarter Scheduling

PawPal+ goes beyond a flat task list with several scheduling behaviors. Each is
implemented in `pawpal_system.py` and named below.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Day planning | `Scheduler.generate_plan()` | Greedily packs highest-priority tasks that fit the available time budget |
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_tasks()` | Chronological order by `"HH:MM"` start time, or by priority then duration |
| Filtering | `Scheduler.filter_by_pet()`, `Scheduler.filter_by_status()` | Narrow tasks to one pet or to pending vs. completed |
| Conflict detection | `Scheduler.detect_conflicts()`, `Scheduler.conflict_warnings()` | Flags tasks whose time windows overlap on the same day |
| Recurring tasks | `Task.mark_complete()`, `Task._next_occurrence()` | Completing a daily/weekly task spawns its next occurrence |
| End-time calc | `Task.end_time` | Derives end time from `start_time + duration`, wrapping around midnight |

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

## Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

The suite (`tests/test_pawpal.py`) covers the core scheduling logic:

- **Task completion & recurrence** — completing a `DAILY` task spawns a fresh
  copy due the next day, `WEEKLY` advances 7 days, `ONCE` tasks don't
  regenerate, and date rollovers (including leap years) are handled correctly.
- **Sorting** — chronological order by start time (even for non-zero-padded
  times like `"9:00"`), plus priority-then-duration ordering without mutating
  the input.
- **Scheduling & budget** — `generate_plan()` includes tasks that fit the time
  budget (including one exactly equal to it), skips oversized tasks while still
  fitting smaller ones, and prioritizes high-priority tasks under a tight budget.
- **Filtering** — case-insensitive filtering by pet and by completion status.
- **Conflict detection** — flags overlapping tasks on the same day, treats
  back-to-back tasks as non-conflicting, ignores different days, spans pets, and
  skips unparseable times.
- **Edge cases** — pets with no tasks, owners with no pets, and zero-minute
  budgets.

Sample output from a successful run:

```
============================= test session starts ==============================
platform darwin -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/chickphila/Desktop/CodePath/Summer2026/ai-110/projects/project2/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 33 items

tests/test_pawpal.py .................................                   [100%]

============================== 33 passed in 0.03s ==============================
```

**Confidence Level:** ★★★★☆ (4/5) — The core scheduling logic (recurrence,
sorting, budget planning, and conflict detection) is thoroughly tested and
reliable. The remaining point is held back by two gaps: input validation
(e.g. negative durations or malformed times) and UI-layer coverage
(`app.py` / `main.py`), which are not yet exercised by the suite.


## 📸 Demo Walkthrough

### What you can do in the app

The Streamlit UI (`app.py`) is organized top to bottom around a single owner:

- **Set the owner.** Edit the owner's name.
- **Add pets.** Give a name and species; added pets appear in a running list.
- **Add tasks.** Pick the pet, then enter a title, duration, priority, **start
  time**, and **due date**. Each task's end time is derived automatically.
- **View tasks in a table.** A sorted `st.table` shows every task's status,
  pet, priority, time window, duration, and due date.
- **Filter.** Narrow the table to one pet or to pending / done tasks.
- **See conflict warnings.** Overlapping tasks are flagged inline above the
  table.
- **Mark tasks done.** A picker completes a task, and recurring tasks
  automatically reappear as their next occurrence.

### Example workflow

1. Enter the owner's name (e.g. *Alex*).
2. Add a pet — *Biscuit*, a dog.
3. Schedule a task for Biscuit: *Morning walk*, 30 min, **high** priority, start
   **08:00**, due today. The table shows it as `08:00–08:30`.
4. Add a second pet, *Mochi*, and a task *Give medication* at **08:15** — which
   overlaps the walk.
5. A ⚠️ **conflict warning** appears above the table, since one owner can't do
   two overlapping tasks at once.
6. Filter the table to **Mochi** to see just her tasks, or to **Pending** to
   hide finished ones.
7. Mark *Morning walk* done. Because it's a daily task, PawPal+ instantly adds
   tomorrow's *Morning walk* as a fresh pending task.

### Scheduler behaviors on display

- **Sorting by time.** Tasks entered out of order are shown chronologically
  (`Scheduler.sort_by_time()`).
- **Filtering.** By pet and by completion status
  (`Scheduler.filter_by_pet()`, `Scheduler.filter_by_status()`).
- **Conflict warnings.** Overlapping same-day windows are flagged
  (`Scheduler.conflict_warnings()`).
- **Recurrence.** Completing a daily/weekly task spawns its next occurrence
  (`Task.mark_complete()`).

### Sample CLI output (`python main.py`)

The `main.py` script demonstrates the same logic in the terminal. It builds a
sample owner (Alex) with two pets, adds tasks **out of time order**, marks
*Breakfast* complete (which spawns its next daily occurrence, so it appears
twice: one *done*, one fresh *pending*), and schedules *Give medication* at
08:15 to deliberately overlap Biscuit's 08:00 walk:

```text
============================================
All tasks (as entered, unsorted)
============================================
  17:30  Enrichment play (45 min) [LOW] for Biscuit - pending
  08:00  Morning walk (30 min) [HIGH] for Biscuit - pending
  07:00  Breakfast (10 min) [HIGH] for Biscuit - done
  07:00  Breakfast (10 min) [HIGH] for Biscuit - pending
  08:15  Give medication (5 min) [HIGH] for Mochi - pending
  12:00  Litter box cleaning (15 min) [MEDIUM] for Mochi - pending

============================================
All tasks sorted by time
============================================
  07:00  Breakfast (10 min) [HIGH] for Biscuit - done
  07:00  Breakfast (10 min) [HIGH] for Biscuit - pending
  08:00  Morning walk (30 min) [HIGH] for Biscuit - pending
  08:15  Give medication (5 min) [HIGH] for Mochi - pending
  12:00  Litter box cleaning (15 min) [MEDIUM] for Mochi - pending
  17:30  Enrichment play (45 min) [LOW] for Biscuit - pending

============================================
Biscuit's tasks sorted by time
============================================
  07:00  Breakfast (10 min) [HIGH] for Biscuit - done
  07:00  Breakfast (10 min) [HIGH] for Biscuit - pending
  08:00  Morning walk (30 min) [HIGH] for Biscuit - pending
  17:30  Enrichment play (45 min) [LOW] for Biscuit - pending

============================================
Pending tasks sorted by time
============================================
  07:00  Breakfast (10 min) [HIGH] for Biscuit - pending
  08:00  Morning walk (30 min) [HIGH] for Biscuit - pending
  08:15  Give medication (5 min) [HIGH] for Mochi - pending
  12:00  Litter box cleaning (15 min) [MEDIUM] for Mochi - pending
  17:30  Enrichment play (45 min) [LOW] for Biscuit - pending

============================================
Completed tasks
============================================
  07:00  Breakfast (10 min) [HIGH] for Biscuit - done

============================================
Schedule conflicts
============================================
  ⚠️ Conflict on 2026-07-05: 'Morning walk' at 08:00 (Biscuit) overlaps 'Give medication' at 08:15 (Mochi).
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
