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
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
