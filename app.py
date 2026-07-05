from datetime import date, time

import streamlit as st

from pawpal_system import Owner, Pet, Task, Priority, Frequency, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Translate the UI's priority labels into the backend Priority enum.
PRIORITY_MAP = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH}

# Translate the UI's frequency labels into the backend Frequency enum. "Once"
# is first (and the default) so a normal task simply completes and stays done;
# daily/weekly are an explicit opt-in that spawns the next occurrence.
FREQUENCY_MAP = {
    "once": Frequency.ONCE,
    "daily": Frequency.DAILY,
    "weekly": Frequency.WEEKLY,
}

# Persist a single Owner across reruns. Streamlit reruns this script top to
# bottom on every interaction, so we only create the Owner if the session
# "vault" doesn't already hold one — otherwise it would be reborn empty.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Grab the persistent Owner from the session "vault".
owner = st.session_state.owner

# Keep the owner's name in sync with the input field.
owner.name = st.text_input("Owner name", value=owner.name)

st.subheader("Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    # Hand the form data to the Owner.add_pet() method from Phase 2.
    owner.add_pet(Pet(name=pet_name, breed=species))
    st.success(f"Added {pet_name}!")

if owner.pets:
    st.write("Your pets: " + ", ".join(pet.name for pet in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")

if not owner.pets:
    st.caption("Add a pet first, then you can schedule tasks for them.")
else:
    selected_pet_name = st.selectbox(
        "Schedule task for", [pet.name for pet in owner.pets]
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=20
        )
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    # Let the owner pick when the task should start and which day it's due.
    # st.time_input returns a datetime.time (formatted to the "HH:MM" string
    # the backend expects); st.date_input returns a date the Task uses directly.
    time_col, date_col, freq_col = st.columns(3)
    with time_col:
        start_time = st.time_input("Start time", value=time(8, 0))
    with date_col:
        due_date = st.date_input("Due date", value=date.today())
    with freq_col:
        # "Once" first so it's the default: the task completes and stays done.
        frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])

    if st.button("Add task"):
        # Find the chosen pet and hand the data to Pet.add_task() from Phase 2.
        pet = next(p for p in owner.pets if p.name == selected_pet_name)
        pet.add_task(
            Task(
                name=task_title,
                duration_minutes=int(duration),
                priority=PRIORITY_MAP[priority],
                start_time=start_time.strftime("%H:%M"),
                due_date=due_date,
                frequency=FREQUENCY_MAP[frequency],
            )
        )
        st.success(f"Added '{task_title}' for {selected_pet_name}!")

    # Display current tasks in a filterable, sorted table. Completing a
    # DAILY/WEEKLY task automatically spawns its next occurrence (with an
    # advanced due date) via the picker below the table.
    all_tasks = owner.get_all_tasks(include_completed=True)
    if all_tasks:
        st.markdown("#### Your tasks")

        # --- Filters, powered by the Scheduler's filter helpers ---
        filter_col, status_col = st.columns(2)
        with filter_col:
            pet_filter = st.selectbox(
                "Filter by pet", ["All pets"] + [p.name for p in owner.pets]
            )
        with status_col:
            status_filter = st.radio(
                "Filter by status", ["All", "Pending", "Done"], horizontal=True
            )

        # Narrow the task set with the Scheduler's filter methods, then order it
        # chronologically so it reads like a real daily schedule.
        tasks = all_tasks
        if pet_filter != "All pets":
            tasks = Scheduler.filter_by_pet(tasks, pet_filter)
        if status_filter == "Pending":
            tasks = Scheduler.filter_by_status(tasks, completed=False)
        elif status_filter == "Done":
            tasks = Scheduler.filter_by_status(tasks, completed=True)
        tasks = Scheduler.sort_by_time(tasks)

        # Surface any timing conflicts among the pending tasks currently shown.
        visible_pending = Scheduler.filter_by_status(tasks, completed=False)
        for warning in Scheduler.conflict_warnings(visible_pending):
            st.warning(warning)

        if tasks:
            rows = [
                {
                    "Status": "✅ Done" if task.completed else "⏳ Pending",
                    "Task": task.name,
                    "Pet": task.pet.name,
                    "Priority": task.priority.name.capitalize(),
                    "Time": f"{task.start_time}–{task.end_time}",
                    "Duration": f"{task.duration_minutes} min",
                    "Due": str(task.due_date),
                    "Repeats": task.frequency.name.capitalize(),
                }
                for task in tasks
            ]
            st.table(rows)
            st.success(
                f"Showing {len(tasks)} task(s): "
                f"{len(visible_pending)} pending, "
                f"{len(tasks) - len(visible_pending)} done."
            )
        else:
            st.info("No tasks match these filters.")

        # --- Mark a task complete (st.table is read-only, so use a picker) ---
        pending_all = owner.get_all_tasks(include_completed=False)
        if pending_all:
            st.markdown("**Mark a task done**")
            # Index-prefixed labels stay unique even if two tasks share a name,
            # so the selectbox can always map back to the right Task object.
            labels = {
                f"{position}. {task.name} · {task.pet.name} · "
                f"{task.due_date} {task.start_time}": task
                for position, task in enumerate(
                    Scheduler.sort_by_time(pending_all), start=1
                )
            }
            pick_col, button_col = st.columns([4, 1])
            with pick_col:
                choice = st.selectbox("Task to complete", list(labels.keys()))
            with button_col:
                st.write("")  # spacer to align the button with the selectbox
                if st.button("Mark done"):
                    labels[choice].mark_complete()
                    st.rerun()
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    st.warning(
        "Not implemented yet. Next step: create your scheduling logic (classes/functions) and call it here."
    )
    st.markdown(
        """
Suggested approach:
1. Design your UML (draft).
2. Create class stubs (no logic).
3. Implement scheduling behavior.
4. Connect your scheduler here and display results.
"""
    )
