# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core tasks a user should be able to perform are tracking pet care tasks, considering constraints in the schedule, and producing + explaining a daily plan.

- Briefly describe your initial UML design.
    - My initial UML design consists of four classes. These classes include the Pet Owner, the Pet themselves, the Assistant/Scheduler, and the Task (that belongs to the Pet). We have the following relationships:
        - An owner can own multiple pets.
        - A pet can have multiple tasks.
        - An owner requests a plan from the Scheduler.
        - The Scheduler, schedules the Task (for the pet).
    - The Owner class has a list of pets, as well as availability and a list of preferences for the scheduler. They can request a plan to the Scheduler to take in.
    - A pet has multiple physical characteristics, as well as its own accomodations and an Owner as well.
    - A task is for a Pet object. It has a name of the task, the duration of it, and a priority string, ranking its priority over other tasks (low, medium, high).
    - A scheduler only does work; it generates the plan based on the tasks given from the owner, and their availability as well.

- What classes did you include, and what responsibilities did you assign to each?
    - **Pet Owner**
        - Attributes:
            - Name (String)
            - Pet(s) (List of Pet object)
            - Available time in minutes (int)
            - Preferences (List of strings)
        - Methods: 
            - Schedule assistant
    - **Pet**
        - Attributes:
            - Name (String)
            - Owner (String)
            - Tasks (list of task objects)
            - Age (Int)
            - Breed (String)
            - Sex/Gender (String)
            - Weight (float/double) (kg or lbs?)
            - Accomodations (list of strings)
        - Methods:
            - None
    - **Assistant/Scheduler**
        - Methods:
            - Produces the daily plan (puts everything all together for tasks and pet owner needs)
    - **Task**
        - Attributes:
            - Name of task (string)
            - Time it takes to do/duration, in minutes (int)
            - Priority (Can be an int, string, or even a boolean)


**b. Design changes**

- Did your design change during implementation?
    - Yes, my design changed slightly during implementation.
- If yes, describe at least one change and why you made it.
    - I added a back-reference from each Task to its Pet so a scheduled task knows which pet it belongs to, and I replaced the free-form string priority with a Priority enum so tasks sort reliably by importance. I also wired the Owner directly to the Scheduler so an owner can gather all its pets' tasks and request a daily plan.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
    - Available time budget (available_minutes)
    - Task duration
    - Start time
    - Priority
    - Completion status (pending vs. done)
    - Frequency / due date (recurring tasks)
    - Time conflicts (overlapping tasks)
    - Pet ownership
- How did you decide which constraints mattered most?
    - I prioritized constraints by what most directly affects a pet's wellbeing and a realistic daily routine, so priority and available time came first (making sure high-importance tasks fit the owner's schedule), followed by time-based ordering and conflict detection to keep the day physically doable. Recurring tasks and pet/status filters mattered next as practical conveniences that keep the plan accurate day to day without driving the core scheduling decisions.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
    - My Scheduler uses an O(n²) pairwise scan in detect_conflicts, trading raw performance for simple, readable code, which is a fine trade at a pet owner's task counts but one that wouldn't scale to hundreds of tasks. More broadly, my scheduler favors straightforward greedy/brute force logic over provably optimal algorithms (like a knapsack based planner), keeping the code easy to follow at the cost of not always producing the mathematically best schedule.
- Why is that tradeoff reasonable for this scenario?
    - That tradeoff is reasonable because a pet owner realistically manages only a handful of tasks per day, so the O(n²) scan and greedy logic run instantly and the performance cost never actually materializes. Prioritizing readable, easy to maintain code over algorithmic optimization is the right call here since the real goal is a clear, correct daily plan rather than squeezing out efficiency that this small scale will never need.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
    - The most effective features were attaching my own files with the @ reference so the assistant reasoned about my real code instead of guessing, and having it run main.py directly to capture true output rather than inventing sample results. Inline edits that I could review one change at a time also let me stay in control of every line that entered my scheduler.
- What kinds of prompts or questions were most helpful?
    - Prompts or questions that were most helpful were inquiring about possible assumptions that the agent could have made while refactoring or generating any body of code, to ensure clarity for edge cases and prospective bugs that could be present in the program. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
    - One moment where I didn't accept an AI suggestion as-is was the AI went ahead in writing code for future functions that we were to implement later on in the application, specifically in pawpal_system.py creating a function for conflict handling. I wanted to take each implementation one step at a time, for validation purposes first to ensure quality of the each component.
- How did you evaluate or verify what the AI suggested?
    - In order to verify my agent's suggestion(s), I had to check for its reasoning and justifications in why what it suggested was correct, in terms of logic, ethics, optimization, and readibility. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
    - I tested task state (starts incomplete, marking done/undone), recurrence (daily, weekly, once, leap year rollovers), pet and owner queries (pending tasks, flattening across pets, empty cases), sorting (by priority and by clock time), budget planning (fitting, skipping oversized, tight budget priority), and filtering plus conflict detection (by pet, by status, and overlapping times).
- Why were these tests important?
    - They lock down the exact rules a wrong schedule would break, like a recurring task vanishing or a low priority task stealing a slot, and they guard the tricky edge cases so I can refactor later and trust the logic still works.

**b. Confidence**

- How confident are you that your scheduler works correctly?
    - If I were to rank from a scale on 1-5, with 1 being very faulty to 5 being flawless, I would rank it a 4.
- What edge cases would you test next if you had more time?
    - Edge cases I would test next time if I had more time were cases where there was an invalid time that doesn't meet the HH:MM format. I would also test invalid or negative durations next time, such as a task with 0 or negative duration_minutes, since there is no validation for it.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
    - I am most satisfied with my conflict detection logic, since it catches overlapping tasks even across different pets and handles tricky cases like back to back times and bad input without crashing.


**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
    - If I had another iteration, I would add input validation so bad data like negative durations or malformed times is caught early, and I would let the Streamlit UI actually call generate_plan so the app shows a real daily plan, not just the task list.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    - One important thing I learned is that designing the classes and relationships up front paid off, since my original UML held through the whole build and I only deepened behavior instead of restructuring. Working with AI taught me to stay in control and review each suggestion, rejecting the ones that added bloat so my design stayed clean.
