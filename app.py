import streamlit as st

from pawpal_system import Owner, Pet, Task, Priority

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Translate the UI's priority labels into the backend Priority enum.
PRIORITY_MAP = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH}

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

    if st.button("Add task"):
        # Find the chosen pet and hand the data to Pet.add_task() from Phase 2.
        pet = next(p for p in owner.pets if p.name == selected_pet_name)
        pet.add_task(
            Task(
                name=task_title,
                duration_minutes=int(duration),
                priority=PRIORITY_MAP[priority],
            )
        )
        st.success(f"Added '{task_title}' for {selected_pet_name}!")

    # Display current tasks by reading straight from the objects.
    all_tasks = owner.get_all_tasks(include_completed=True)
    if all_tasks:
        st.write("Current tasks:")
        st.table(
            [
                {
                    "pet": task.pet.name,
                    "task": task.name,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority.name.lower(),
                }
                for task in all_tasks
            ]
        )
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
