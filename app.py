import streamlit as st
from graphviz import Digraph

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Deadlock Detection & Prevention Simulator",
    page_icon="🔒",
    layout="wide"
)

st.title("🔒 Deadlock Detection & Prevention Simulator")

st.markdown(
    """
    **Operating Systems Mini Project**

    Simulate resource allocation, detect deadlocks,
    verify safe states using Banker's Algorithm,
    and analyze resource requests.
    """
)

st.divider()


# --------------------------------------------------
# EXAMPLE DATA
# --------------------------------------------------

# Deadlock Detection Example
detection_safe_allocation = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
]

detection_safe_request = [
    [0, 1, 0],
    [0, 0, 1],
    [1, 0, 0]
]

detection_safe_available = [1, 0, 0]


detection_deadlock_allocation = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
]

detection_deadlock_request = [
    [0, 1, 0],
    [0, 0, 1],
    [1, 0, 0]
]

detection_deadlock_available = [0, 0, 0]


# Standard Banker's Algorithm example

banker_allocation = [
    [0, 1, 0],
    [2, 0, 0],
    [3, 0, 2],
    [2, 1, 1],
    [0, 0, 2]
]

banker_maximum = [
    [7, 5, 3],
    [3, 2, 2],
    [9, 0, 2],
    [2, 2, 2],
    [4, 3, 3]
]

banker_available = [3, 3, 2]


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "processes" not in st.session_state:
    st.session_state.processes = 3

if "resources" not in st.session_state:
    st.session_state.resources = 3


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def calculate_need(allocation, maximum):
    need = []

    for i in range(len(allocation)):
        row = []

        for j in range(len(allocation[0])):
            row.append(maximum[i][j] - allocation[i][j])

        need.append(row)

    return need


def detection_algorithm(allocation, request, available):
    work = available.copy()

    finish = [False] * len(allocation)

    sequence = []

    trace = []

    changed = True

    while changed:
        changed = False

        for i in range(len(allocation)):

            if finish[i]:
                continue

            can_finish = True

            for j in range(len(available)):
                if request[i][j] > work[j]:
                    can_finish = False
                    break

            if can_finish:

                old_work = work.copy()

                for j in range(len(available)):
                    work[j] += allocation[i][j]

                finish[i] = True

                sequence.append(i)

                trace.append({
                    "process": i,
                    "before": old_work,
                    "released": allocation[i].copy(),
                    "after": work.copy()
                })

                changed = True

    deadlocked = [
        i for i in range(len(allocation))
        if not finish[i]
    ]

    no_deadlock = len(deadlocked) == 0

    return no_deadlock, sequence, deadlocked, trace


def banker_safety_algorithm(allocation, maximum, available):
    need = calculate_need(allocation, maximum)

    work = available.copy()

    finish = [False] * len(allocation)

    sequence = []

    trace = []

    changed = True

    while changed:
        changed = False

        for i in range(len(allocation)):

            if finish[i]:
                continue

            can_finish = True

            for j in range(len(available)):
                if need[i][j] > work[j]:
                    can_finish = False
                    break

            if can_finish:

                old_work = work.copy()

                for j in range(len(available)):
                    work[j] += allocation[i][j]

                finish[i] = True

                sequence.append(i)

                trace.append({
                    "process": i,
                    "need": need[i].copy(),
                    "before": old_work,
                    "released": allocation[i].copy(),
                    "after": work.copy()
                })

                changed = True

    safe = all(finish)

    return safe, sequence, need, trace


def load_detection_safe():

    st.session_state.processes = 3
    st.session_state.resources = 3

    st.session_state.process_count = 3
    st.session_state.resource_count = 3

    for i in range(3):
        for j in range(3):
            st.session_state[f"det_allocation_{i}_{j}"] = \
                detection_safe_allocation[i][j]

            st.session_state[f"det_request_{i}_{j}"] = \
                detection_safe_request[i][j]

    for j in range(3):
        st.session_state[f"det_available_{j}"] = \
            detection_safe_available[j]


def load_detection_deadlock():

    st.session_state.processes = 3
    st.session_state.resources = 3

    st.session_state.process_count = 3
    st.session_state.resource_count = 3

    for i in range(3):
        for j in range(3):
            st.session_state[f"det_allocation_{i}_{j}"] = \
                detection_deadlock_allocation[i][j]

            st.session_state[f"det_request_{i}_{j}"] = \
                detection_deadlock_request[i][j]

    for j in range(3):
        st.session_state[f"det_available_{j}"] = \
            detection_deadlock_available[j]


def load_banker_example():

    st.session_state.processes = 5
    st.session_state.resources = 3

    st.session_state.process_count = 5
    st.session_state.resource_count = 3

    for i in range(5):
        for j in range(3):

            st.session_state[f"bank_allocation_{i}_{j}"] = \
                banker_allocation[i][j]

            st.session_state[f"bank_maximum_{i}_{j}"] = \
                banker_maximum[i][j]

    for j in range(3):
        st.session_state[f"bank_available_{j}"] = \
            banker_available[j]


def reset_project():

    st.session_state.processes = 3
    st.session_state.resources = 3

    st.session_state.process_count = 3
    st.session_state.resource_count = 3

    for i in range(10):
        for j in range(10):

            st.session_state[f"det_allocation_{i}_{j}"] = 0
            st.session_state[f"det_request_{i}_{j}"] = 0

            st.session_state[f"bank_allocation_{i}_{j}"] = 0
            st.session_state[f"bank_maximum_{i}_{j}"] = 0

    for j in range(10):
        st.session_state[f"det_available_{j}"] = 0
        st.session_state[f"bank_available_{j}"] = 0


# --------------------------------------------------
# EXAMPLE DATASETS
# --------------------------------------------------

st.subheader("🎯 Example Datasets")

example = st.selectbox(
    "Choose an example",
    [
        "Manual Input",
        "🟢 Detection - No Deadlock",
        "🔴 Detection - Deadlock",
        "🏦 Banker's Algorithm - Safe Example"
    ]
)

col1, col2 = st.columns(2)

with col1:

    if example == "🟢 Detection - No Deadlock":

        st.button(
            "📥 Load Example",
            on_click=load_detection_safe
        )

    elif example == "🔴 Detection - Deadlock":

        st.button(
            "📥 Load Example",
            on_click=load_detection_deadlock
        )

    elif example == "🏦 Banker's Algorithm - Safe Example":

        st.button(
            "📥 Load Example",
            on_click=load_banker_example
        )

    else:

        st.button(
            "📥 Load Example",
            disabled=True
        )


with col2:

    st.button(
        "🔄 Reset",
        on_click=reset_project
    )

st.divider()


# --------------------------------------------------
# SYSTEM CONFIGURATION
# --------------------------------------------------

st.subheader("⚙️ System Configuration")

col1, col2 = st.columns(2)

with col1:

    processes = st.number_input(
        "Number of Processes",
        min_value=1,
        max_value=10,
        value=st.session_state.processes,
        key="process_count"
    )

with col2:

    resources = st.number_input(
        "Number of Resources",
        min_value=1,
        max_value=10,
        value=st.session_state.resources,
        key="resource_count"
    )


st.divider()


# ==================================================
# 1. DEADLOCK DETECTION
# ==================================================

st.header("🔍 1. Deadlock Detection")

st.info(
    "Deadlock detection uses Allocation, Request and Available "
    "resources to determine whether processes are deadlocked."
)


# --------------------------------------------------
# DETECTION ALLOCATION
# --------------------------------------------------

st.subheader("📦 Allocation Matrix")

st.caption(
    "Resources currently allocated to each process."
)

detection_allocation = []

header = st.columns(resources + 1)

header[0].write("")

for j in range(resources):
    header[j + 1].markdown(f"**R{j + 1}**")


for i in range(processes):

    cols = st.columns(resources + 1)

    cols[0].markdown(f"**P{i + 1}**")

    row = []

    for j in range(resources):

        value = cols[j + 1].number_input(
            f"P{i + 1} R{j + 1} Allocation",
            min_value=0,
            max_value=100,
            step=1,
            key=f"det_allocation_{i}_{j}",
            label_visibility="collapsed"
        )

        row.append(value)

    detection_allocation.append(row)


# --------------------------------------------------
# DETECTION REQUEST
# --------------------------------------------------

st.subheader("📋 Request Matrix")

st.caption(
    "Resources still requested by each process."
)

detection_request = []

header = st.columns(resources + 1)

header[0].write("")

for j in range(resources):
    header[j + 1].markdown(f"**R{j + 1}**")


for i in range(processes):

    cols = st.columns(resources + 1)

    cols[0].markdown(f"**P{i + 1}**")

    row = []

    for j in range(resources):

        value = cols[j + 1].number_input(
            f"P{i + 1} R{j + 1} Request",
            min_value=0,
            max_value=100,
            step=1,
            key=f"det_request_{i}_{j}",
            label_visibility="collapsed"
        )

        row.append(value)

    detection_request.append(row)


# --------------------------------------------------
# DETECTION AVAILABLE
# --------------------------------------------------

st.subheader("🟢 Available Resources")

available_cols = st.columns(resources)

detection_available = []

for j in range(resources):

    value = available_cols[j].number_input(
        f"R{j + 1} Available",
        min_value=0,
        max_value=100,
        step=1,
        key=f"det_available_{j}"
    )

    detection_available.append(value)


# --------------------------------------------------
# DETECTION BUTTON
# --------------------------------------------------

if st.button(
    "🔎 Detect Deadlock",
    type="primary",
    use_container_width=True
):

    no_deadlock, sequence, deadlocked, trace = \
        detection_algorithm(
            detection_allocation,
            detection_request,
            detection_available
        )

    if no_deadlock:

        st.success("### 🟢 NO DEADLOCK DETECTED")

        sequence_text = " → ".join(
            [f"P{i + 1}" for i in sequence]
        )

        st.info(
            f"Possible completion sequence: **{sequence_text}**"
        )

    else:

        st.error("### 🔴 DEADLOCK DETECTED")

        deadlocked_text = ", ".join(
            [f"P{i + 1}" for i in deadlocked]
        )

        st.warning(
            f"Deadlocked processes: **{deadlocked_text}**"
        )


# --------------------------------------------------
# DETECTION TRACE
# --------------------------------------------------

if st.button(
    "▶️ Show Detection Steps",
    use_container_width=True
):

    no_deadlock, sequence, deadlocked, trace = \
        detection_algorithm(
            detection_allocation,
            detection_request,
            detection_available
        )

    if trace:

        for step_number, item in enumerate(trace, start=1):

            process_name = f"P{item['process'] + 1}"

            st.write(
                f"### Step {step_number}: {process_name}"
            )

            st.write(
                f"Available before: `{item['before']}`"
            )

            st.write(
                f"Resources released: `{item['released']}`"
            )

            st.write(
                f"Available after: `{item['after']}`"
            )

            st.success(
                f"{process_name} can complete."
            )

    if no_deadlock:

        st.success(
            "All processes can complete. No deadlock exists."
        )

    else:

        remaining = ", ".join(
            [f"P{i + 1}" for i in deadlocked]
        )

        st.error(
            f"Deadlock remains among: {remaining}"
        )


st.divider()


# ==================================================
# 2. BANKER'S ALGORITHM
# ==================================================

st.header("🏦 2. Deadlock Avoidance — Banker's Algorithm")

st.info(
    "Banker's Algorithm checks whether resource allocation keeps "
    "the system in a safe state."
)


# --------------------------------------------------
# BANKER ALLOCATION
# --------------------------------------------------

st.subheader("📦 Allocation Matrix")

banker_input_allocation = []

header = st.columns(resources + 1)

header[0].write("")

for j in range(resources):
    header[j + 1].markdown(f"**R{j + 1}**")


for i in range(processes):

    cols = st.columns(resources + 1)

    cols[0].markdown(f"**P{i + 1}**")

    row = []

    for j in range(resources):

        value = cols[j + 1].number_input(
            f"P{i + 1} R{j + 1} Banker Allocation",
            min_value=0,
            max_value=100,
            step=1,
            key=f"bank_allocation_{i}_{j}",
            label_visibility="collapsed"
        )

        row.append(value)

    banker_input_allocation.append(row)


# --------------------------------------------------
# BANKER MAXIMUM
# --------------------------------------------------

st.subheader("📈 Maximum Matrix")

st.caption(
    "Maximum resources that each process may require."
)

banker_maximum_input = []

header = st.columns(resources + 1)

header[0].write("")

for j in range(resources):
    header[j + 1].markdown(f"**R{j + 1}**")


for i in range(processes):

    cols = st.columns(resources + 1)

    cols[0].markdown(f"**P{i + 1}**")

    row = []

    for j in range(resources):

        value = cols[j + 1].number_input(
            f"P{i + 1} R{j + 1} Maximum",
            min_value=0,
            max_value=100,
            step=1,
            key=f"bank_maximum_{i}_{j}",
            label_visibility="collapsed"
        )

        row.append(value)

    banker_maximum_input.append(row)


# --------------------------------------------------
# BANKER AVAILABLE
# --------------------------------------------------

st.subheader("🟢 Available Resources")

banker_available_input = []

available_cols = st.columns(resources)

for j in range(resources):

    value = available_cols[j].number_input(
        f"Banker R{j + 1} Available",
        min_value=0,
        max_value=100,
        step=1,
        key=f"bank_available_{j}"
    )

    banker_available_input.append(value)


# --------------------------------------------------
# VALIDATE ALLOCATION <= MAXIMUM
# --------------------------------------------------

invalid_allocation = False

for i in range(processes):

    for j in range(resources):

        if (
            banker_input_allocation[i][j]
            > banker_maximum_input[i][j]
        ):

            invalid_allocation = True


if invalid_allocation:

    st.error(
        "❌ Invalid input: Allocation cannot be greater "
        "than Maximum."
    )

else:

    banker_need = calculate_need(
        banker_input_allocation,
        banker_maximum_input
    )

    st.subheader("🧮 Need Matrix")

    st.caption(
        "Need = Maximum − Allocation"
    )

    header = st.columns(resources + 1)

    header[0].write("")

    for j in range(resources):
        header[j + 1].markdown(f"**R{j + 1}**")

    for i in range(processes):

        cols = st.columns(resources + 1)

        cols[0].markdown(f"**P{i + 1}**")

        for j in range(resources):

            cols[j + 1].write(
                banker_need[i][j]
            )


    # --------------------------------------------------
    # BANKER SAFETY CHECK
    # --------------------------------------------------

    if st.button(
        "🏦 Check Safe State",
        type="primary",
        use_container_width=True
    ):

        safe, sequence, need, trace = \
            banker_safety_algorithm(
                banker_input_allocation,
                banker_maximum_input,
                banker_available_input
            )

        if safe:

            st.success(
                "### 🟢 SYSTEM IS IN A SAFE STATE"
            )

            sequence_text = " → ".join(
                [f"P{i + 1}" for i in sequence]
            )

            st.info(
                f"**Safe Sequence:** {sequence_text}"
            )

        else:

            st.error(
                "### 🔴 SYSTEM IS IN AN UNSAFE STATE"
            )

            st.warning(
                "No complete safe sequence exists."
            )


    # --------------------------------------------------
    # BANKER TRACE
    # --------------------------------------------------

    if st.button(
        "▶️ Show Banker's Steps",
        use_container_width=True
    ):

        safe, sequence, need, trace = \
            banker_safety_algorithm(
                banker_input_allocation,
                banker_maximum_input,
                banker_available_input
            )

        if trace:

            for step_number, item in enumerate(
                trace,
                start=1
            ):

                process_name = (
                    f"P{item['process'] + 1}"
                )

                st.write(
                    f"### Step {step_number}: "
                    f"{process_name}"
                )

                st.write(
                    f"Need: `{item['need']}`"
                )

                st.write(
                    f"Available before: "
                    f"`{item['before']}`"
                )

                st.write(
                    f"Resources released: "
                    f"`{item['released']}`"
                )

                st.write(
                    f"Available after: "
                    f"`{item['after']}`"
                )

                st.success(
                    f"{process_name} can safely complete."
                )

        if safe:

            st.success(
                "All processes can finish. "
                "The system is safe."
            )

        else:

            st.error(
                "The system is unsafe because "
                "a complete safe sequence could not be found."
            )


    # --------------------------------------------------
    # ADDITIONAL RESOURCE REQUEST
    # --------------------------------------------------

    st.subheader("📥 Additional Resource Request")

    selected_process = st.selectbox(
        "Select Process",
        [f"P{i + 1}" for i in range(processes)],
        key="bank_selected_process"
    )

    selected_index = int(
        selected_process[1:]
    ) - 1

    st.write(
        "Enter the additional resources requested:"
    )

    request_cols = st.columns(resources)

    additional_request = []

    for j in range(resources):

        value = request_cols[j].number_input(
            f"Additional R{j + 1}",
            min_value=0,
            max_value=100,
            step=1,
            key=f"bank_additional_request_{j}"
        )

        additional_request.append(value)


    if st.button(
        "🔐 Check Resource Request",
        use_container_width=True
    ):

        exceeds_need = False

        for j in range(resources):

            if (
                additional_request[j]
                > banker_need[selected_index][j]
            ):

                exceeds_need = True


        if exceeds_need:

            st.error(
                "❌ Request exceeds the remaining "
                "Need of the selected process."
            )

        else:

            exceeds_available = False

            for j in range(resources):

                if (
                    additional_request[j]
                    > banker_available_input[j]
                ):

                    exceeds_available = True


            if exceeds_available:

                st.warning(
                    "⏳ Request cannot be granted immediately "
                    "because sufficient resources are unavailable."
                )

            else:

                temp_allocation = [
                    row.copy()
                    for row in banker_input_allocation
                ]

                temp_available = (
                    banker_available_input.copy()
                )

                temp_maximum = [
                    row.copy()
                    for row in banker_maximum_input
                ]


                for j in range(resources):

                    temp_available[j] -= (
                        additional_request[j]
                    )

                    temp_allocation[
                        selected_index
                    ][j] += additional_request[j]


                safe, sequence, temp_need, trace = \
                    banker_safety_algorithm(
                        temp_allocation,
                        temp_maximum,
                        temp_available
                    )


                if safe:

                    st.success(
                        "✅ Request can be safely granted."
                    )

                    sequence_text = " → ".join(
                        [
                            f"P{i + 1}"
                            for i in sequence
                        ]
                    )

                    st.info(
                        f"Safe sequence after granting: "
                        f"**{sequence_text}**"
                    )

                else:

                    st.error(
                        "❌ Request should NOT be granted."
                    )

                    st.warning(
                        "Granting this request would place "
                        "the system in an unsafe state."
                    )


st.divider()


# ==================================================
# 3. RESOURCE ALLOCATION GRAPH
# ==================================================

st.header("🕸️ Resource Allocation Graph")

show_graph = st.checkbox(
    "Show Resource Allocation Graph"
)

if show_graph:

    graph = Digraph()

    graph.attr(rankdir="LR")

    # Processes
    for i in range(processes):

        graph.node(
            f"P{i + 1}",
            f"P{i + 1}",
            shape="circle"
        )

    # Resources
    for j in range(resources):

        graph.node(
            f"R{j + 1}",
            f"R{j + 1}",
            shape="box"
        )


    # Allocation edges
    for i in range(processes):

        for j in range(resources):

            if detection_allocation[i][j] > 0:

                graph.edge(
                    f"R{j + 1}",
                    f"P{i + 1}",
                    label=str(
                        detection_allocation[i][j]
                    )
                )


    # Request edges
    for i in range(processes):

        for j in range(resources):

            if detection_request[i][j] > 0:

                graph.edge(
                    f"P{i + 1}",
                    f"R{j + 1}",
                    style="dashed",
                    label=str(
                        detection_request[i][j]
                    )
                )


    st.graphviz_chart(
        graph,
        use_container_width=True
    )

    st.caption(
        "Solid arrows represent allocated resources. "
        "Dashed arrows represent resource requests."
    )


st.divider()


# ==================================================
# SYSTEM OVERVIEW
# ==================================================

st.subheader("📊 System Overview")

dash1, dash2, dash3 = st.columns(3)

with dash1:
    st.metric(
        "Processes",
        processes
    )

with dash2:
    st.metric(
        "Resources",
        resources
    )

with dash3:
    st.metric(
        "Detection Available",
        sum(detection_available)
    )


st.divider()


# ==================================================
# PROJECT INFORMATION
# ==================================================

st.subheader("📘 Project Information")

info1, info2, info3 = st.columns(3)

with info1:

    st.markdown(
        """
        **Deadlock Detection**

        • Allocation

        • Request

        • Available

        • Deadlock / No Deadlock
        """
    )


with info2:

    st.markdown(
        """
        **Banker's Algorithm**

        • Allocation

        • Maximum

        • Need

        • Available

        • Safe Sequence
        """
    )


with info3:

    st.markdown(
        """
        **Deadlock Conditions**

        • Mutual Exclusion

        • Hold and Wait

        • No Preemption

        • Circular Wait
        """
    )


st.divider()

st.caption(
    "Operating Systems Mini Project | "
    "Deadlock Detection and Prevention"
)