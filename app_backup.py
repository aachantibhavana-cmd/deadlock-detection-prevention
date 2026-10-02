import streamlit as st
from graphviz import Digraph

# ==================================================
# PAGE SETTINGS
# ==================================================

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
    verify safe states, and analyze resource requests.
    """
)

st.divider()


# ==================================================
# EXAMPLE DATA
# ==================================================

safe_allocation = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
]

safe_request = [
    [0, 1, 0],
    [0, 0, 1],
    [1, 0, 0]
]

safe_available = [1, 0, 0]


deadlock_allocation = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
]

deadlock_request = [
    [0, 1, 0],
    [0, 0, 1],
    [1, 0, 0]
]

deadlock_available = [0, 0, 0]


# ==================================================
# SESSION STATE
# ==================================================

if "processes" not in st.session_state:
    st.session_state.processes = 3

if "resources" not in st.session_state:
    st.session_state.resources = 3


def initialize_values():

    for i in range(3):

        for j in range(3):

            if f"allocation_{i}_{j}" not in st.session_state:
                st.session_state[f"allocation_{i}_{j}"] = 0

            if f"request_{i}_{j}" not in st.session_state:
                st.session_state[f"request_{i}_{j}"] = 0

    for j in range(3):

        if f"available_{j}" not in st.session_state:
            st.session_state[f"available_{j}"] = 1


initialize_values()


# ==================================================
# EXAMPLE FUNCTIONS
# ==================================================

def load_safe_example():

    st.session_state.processes = 3
    st.session_state.resources = 3

    for i in range(3):

        for j in range(3):

            st.session_state[f"allocation_{i}_{j}"] = \
                safe_allocation[i][j]

            st.session_state[f"request_{i}_{j}"] = \
                safe_request[i][j]

    for j in range(3):

        st.session_state[f"available_{j}"] = \
            safe_available[j]


def load_deadlock_example():

    st.session_state.processes = 3
    st.session_state.resources = 3

    for i in range(3):

        for j in range(3):

            st.session_state[f"allocation_{i}_{j}"] = \
                deadlock_allocation[i][j]

            st.session_state[f"request_{i}_{j}"] = \
                deadlock_request[i][j]

    for j in range(3):

        st.session_state[f"available_{j}"] = \
            deadlock_available[j]


def reset_project():

    st.session_state.processes = 3
    st.session_state.resources = 3

    for i in range(3):

        for j in range(3):

            st.session_state[f"allocation_{i}_{j}"] = 0
            st.session_state[f"request_{i}_{j}"] = 0

    for j in range(3):

        st.session_state[f"available_{j}"] = 1


# ==================================================
# SAFETY CHECK
# ==================================================

def safety_check(allocation, request, available):

    work = available.copy()

    finish = [False] * len(allocation)

    sequence = []

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

                for j in range(len(available)):

                    work[j] += allocation[i][j]

                finish[i] = True

                sequence.append(i)

                changed = True

    safe = all(finish)

    deadlocked = [
        i for i in range(len(allocation))
        if not finish[i]
    ]

    return safe, sequence, deadlocked


# ==================================================
# EXAMPLE DATASETS
# ==================================================

st.subheader("🎯 Example Datasets")

example = st.selectbox(
    "Choose an example",
    [
        "Manual Input",
        "🟢 Safe State Example",
        "🔴 Deadlock Example"
    ]
)

col1, col2 = st.columns(2)

with col1:

    if example == "🟢 Safe State Example":

        st.button(
            "📥 Load Example",
            on_click=load_safe_example
        )

    elif example == "🔴 Deadlock Example":

        st.button(
            "📥 Load Example",
            on_click=load_deadlock_example
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


# ==================================================
# SYSTEM CONFIGURATION
# ==================================================

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


# Current version uses 3 × 3 matrices

if processes != 3 or resources != 3:

    st.info(
        "For this version, use 3 processes and 3 resources."
    )

    processes = 3
    resources = 3


st.divider()


# ==================================================
# ALLOCATION MATRIX
# ==================================================

st.subheader("📦 Allocation Matrix")

st.write(
    "Resources currently allocated to each process."
)

allocation = []

header_cols = st.columns(resources + 1)

header_cols[0].write("")

for j in range(resources):

    header_cols[j + 1].markdown(
        f"**R{j + 1}**"
    )


for i in range(processes):

    cols = st.columns(resources + 1)

    cols[0].markdown(
        f"**P{i}**"
    )

    row = []

    for j in range(resources):

        value = cols[j + 1].number_input(
            f"P{i} R{j + 1}",
            min_value=0,
            max_value=20,
            step=1,
            key=f"allocation_{i}_{j}",
            label_visibility="collapsed"
        )

        row.append(value)

    allocation.append(row)


st.divider()


# ==================================================
# REQUEST / NEED MATRIX
# ==================================================

st.subheader("📋 Request / Need Matrix")

st.write(
    "Resources still required by each process to complete."
)

request = []

header_cols = st.columns(resources + 1)

header_cols[0].write("")

for j in range(resources):

    header_cols[j + 1].markdown(
        f"**R{j + 1}**"
    )


for i in range(processes):

    cols = st.columns(resources + 1)

    cols[0].markdown(
        f"**P{i}**"
    )

    row = []

    for j in range(resources):

        value = cols[j + 1].number_input(
            f"P{i} R{j + 1}",
            min_value=0,
            max_value=20,
            step=1,
            key=f"request_{i}_{j}",
            label_visibility="collapsed"
        )

        row.append(value)

    request.append(row)


st.divider()


# ==================================================
# AVAILABLE RESOURCES
# ==================================================

st.subheader("🟢 Available Resources")

available_cols = st.columns(resources)

available = []

for j in range(resources):

    value = available_cols[j].number_input(
        f"R{j + 1} Available",
        min_value=0,
        max_value=20,
        step=1,
        key=f"available_{j}"
    )

    available.append(value)


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
        "Available Units",
        sum(available)
    )


st.divider()


# ==================================================
# DEADLOCK DETECTION
# ==================================================

st.subheader("🔍 Deadlock Detection")

if st.button(
    "🔎 Detect Deadlock",
    type="primary",
    use_container_width=True
):

    safe, sequence, deadlocked = safety_check(
        allocation,
        request,
        available
    )

    st.divider()

    if safe:

        st.success("### 🟢 SYSTEM IS SAFE")

        sequence_text = " → ".join(
            [f"P{i}" for i in sequence]
        )

        st.markdown(
            f"""
            **Safe Sequence**

            ### {sequence_text}

            All processes can complete successfully
            using the available resources.
            """
        )

    else:

        st.error("### 🔴 DEADLOCK DETECTED")

        deadlocked_text = ", ".join(
            [f"P{i}" for i in deadlocked]
        )

        st.markdown(
            f"""
            **Deadlocked Processes**

            ### {deadlocked_text}

            These processes cannot complete with the
            currently available resources.
            """
        )

# ==================================================
# STEP-BY-STEP DETECTION
# ==================================================

st.subheader("🪜 Step-by-Step Detection")

if st.button(
    "▶️ Show Detection Steps",
    use_container_width=True
):

    work = available.copy()

    finish = [False] * processes

    step = 1

    progress = True

    while progress:

        progress = False

        for i in range(processes):

            if finish[i]:
                continue

            can_finish = True

            for j in range(resources):

                if request[i][j] > work[j]:

                    can_finish = False
                    break

            if can_finish:

                old_work = work.copy()

                for j in range(resources):

                    work[j] += allocation[i][j]

                finish[i] = True

                st.write(
                    f"### Step {step}: P{i}"
                )

                st.write(
                    f"Available before: `{old_work}`"
                )

                st.write(
                    f"Resources released by P{i}: "
                    f"`{allocation[i]}`"
                )

                st.write(
                    f"Available after: `{work}`"
                )

                st.success(
                    f"P{i} can finish."
                )

                step += 1

                progress = True


    if all(finish):

        st.success(
            "All processes can finish. No deadlock."
        )

    else:

        remaining = [
            f"P{i}"
            for i in range(processes)
            if not finish[i]
        ]

        st.error(
            "Deadlock remains among: "
            + ", ".join(remaining)
        )


st.divider()


# ==================================================
# PREVENTION / SAFE RESOURCE REQUEST
# ==================================================

st.subheader("🛡️ Prevention / Safe Resource Request")

st.write(
    "Check whether an additional resource request "
    "can be safely granted."
)

selected_process = st.selectbox(
    "Select Process",
    [f"P{i}" for i in range(processes)]
)

selected_index = int(
    selected_process[1:]
)


st.write("Enter additional resources requested:")

request_cols = st.columns(resources)

additional_request = []

for j in range(resources):

    value = request_cols[j].number_input(
        f"R{j + 1}",
        min_value=0,
        max_value=20,
        step=1,
        key=f"additional_request_{j}"
    )

    additional_request.append(value)


if st.button(
    "🛡️ Check Request",
    use_container_width=True
):

    exceeds_need = False

    for j in range(resources):

        if additional_request[j] > request[selected_index][j]:

            exceeds_need = True

    if exceeds_need:

        st.error(
            "❌ Request exceeds the remaining need "
            "of the process."
        )

    else:

        exceeds_available = False

        for j in range(resources):

            if additional_request[j] > available[j]:

                exceeds_available = True

        if exceeds_available:

            st.warning(
                "⏳ Request cannot be granted immediately "
                "because sufficient resources are not available."
            )

        else:

            temp_available = available.copy()

            temp_allocation = [
                row.copy()
                for row in allocation
            ]

            temp_request = [
                row.copy()
                for row in request
            ]

            for j in range(resources):

                temp_available[j] -= \
                    additional_request[j]

                temp_allocation[selected_index][j] += \
                    additional_request[j]

                temp_request[selected_index][j] -= \
                    additional_request[j]

            safe, sequence, deadlocked = safety_check(
                temp_allocation,
                temp_request,
                temp_available
            )

            if safe:

                sequence_text = " → ".join(
                    [f"P{i}" for i in sequence]
                )

                st.success(
                    "✅ Request can be safely granted."
                )

                st.info(
                    f"Safe Sequence after granting request: "
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
# RESOURCE ALLOCATION GRAPH
# ==================================================

st.subheader("🕸️ Resource Allocation Graph")

show_graph = st.checkbox(
    "Show Resource Allocation Graph"
)

if show_graph:

    graph = Digraph()

    graph.attr(
        rankdir="LR"
    )

    # Process nodes

    for i in range(processes):

        graph.node(
            f"P{i}",
            f"P{i}",
            shape="circle"
        )

    # Resource nodes

    for j in range(resources):

        graph.node(
            f"R{j}",
            f"R{j + 1}",
            shape="box"
        )

    # Allocation edges
    # Resource → Process

    for i in range(processes):

        for j in range(resources):

            if allocation[i][j] > 0:

                graph.edge(
                    f"R{j}",
                    f"P{i}",
                    label=str(allocation[i][j])
                )

    # Request edges
    # Process → Resource

    for i in range(processes):

        for j in range(resources):

            if request[i][j] > 0:

                graph.edge(
                    f"P{i}",
                    f"R{j}",
                    style="dashed",
                    label=str(request[i][j])
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
# PROJECT INFORMATION
# ==================================================

st.subheader("📘 Project Information")

info1, info2, info3 = st.columns(3)

with info1:

    st.markdown(
        """
        **Deadlock Conditions**

        • Mutual Exclusion  
        • Hold and Wait  
        • No Preemption  
        • Circular Wait
        """
    )


with info2:

    st.markdown(
        """
        **Detection**

        • Available resources  
        • Allocation matrix  
        • Request/Need matrix  
        • Safe sequence
        """
    )


with info3:

    st.markdown(
        """
        **Safety Check**

        • Check process request  
        • Simulate allocation  
        • Release resources  
        • Check final state
        """
    )


st.divider()

st.caption(
    "Operating Systems Mini Project | "
    "Deadlock Detection and Prevention"
)