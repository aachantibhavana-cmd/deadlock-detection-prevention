import streamlit as st
from graphviz import Digraph

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Deadlock Detection & Prevention",
    page_icon="🔒",
    layout="wide"
)

# ============================================================
# CUSTOM CSS - DASHBOARD STYLE
# ============================================================

st.markdown("""
<style>
    .stApp {
        background: #f5f8fc;
    }

    .hero {
        background: linear-gradient(135deg, #193a59 0%, #245d78 100%);
        color: white;
        padding: 30px 34px 26px 34px;
        border-radius: 0 0 22px 22px;
        margin: -1rem -1rem 26px -1rem;
        text-align: center;
        box-shadow: 0 8px 24px rgba(15, 45, 70, 0.14);
    }

    .hero-title {
        font-size: 38px;
        font-weight: 800;
        letter-spacing: -0.8px;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 18px;
        font-weight: 600;
        opacity: 0.96;
        margin-bottom: 6px;
    }

    .hero-description {
        font-size: 14px;
        opacity: 0.82;
    }

    .metric-card {
        background: white;
        border: 1px solid #dbe4ee;
        border-top: 4px solid #4388bd;
        border-radius: 14px;
        padding: 15px 18px;
        min-height: 92px;
        box-shadow: 0 5px 16px rgba(25, 58, 89, 0.07);
    }

    .metric-label {
        color: #66778a;
        font-size: 13px;
        font-weight: 600;
    }

    .metric-value {
        color: #193a59;
        font-size: 28px;
        font-weight: 800;
        margin-top: 4px;
    }

    .card {
        background: white;
        border: 1px solid #dbe4ee;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 4px 14px rgba(25, 58, 89, 0.05);
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white;
        border: 1px solid #dbe4ee;
        border-radius: 14px;
        box-shadow: 0 4px 14px rgba(25, 58, 89, 0.05);
    }

    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        border-radius: 14px;
    }

    .result-safe {
        background: #edf9f1;
        border: 1px solid #b8e3c4;
        border-left: 6px solid #2e9b57;
        border-radius: 13px;
        padding: 17px 20px;
        color: #18733b;
        font-size: 21px;
        font-weight: 800;
        margin: 16px 0;
    }

    .result-deadlock {
        background: #fff1f2;
        border: 1px solid #f3c1c7;
        border-left: 6px solid #d43b45;
        border-radius: 13px;
        padding: 17px 20px;
        color: #b4232d;
        font-size: 21px;
        font-weight: 800;
        margin: 16px 0;
    }

    .section-note {
        color: #66778a;
        font-size: 14px;
        margin-bottom: 12px;
    }

    .small-heading {
        color: #193a59;
        font-weight: 750;
        font-size: 18px;
    }

    div[data-testid="stExpander"] {
        border-radius: 12px;
        border-color: #dbe4ee;
        background: white;
    }

    div.stButton > button {
        border-radius: 10px;
        font-weight: 700;
        min-height: 44px;
    }

    div[data-baseweb="tab-list"] {
        gap: 8px;
    }

    button[data-baseweb="tab"] {
        font-weight: 650;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# EXAMPLE DATASETS
# ============================================================

NO_DEADLOCK_ALLOCATION = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 0]
]

NO_DEADLOCK_REQUEST = [
    [0, 1, 0],
    [0, 0, 1],
    [1, 0, 0]
]

NO_DEADLOCK_AVAILABLE = [0, 0, 1]

DEADLOCK_ALLOCATION = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
]

DEADLOCK_REQUEST = [
    [0, 1, 0],
    [0, 0, 1],
    [1, 0, 0]
]

DEADLOCK_AVAILABLE = [0, 0, 0]

# ============================================================
# SESSION STATE
# ============================================================

if "num_processes" not in st.session_state:
    st.session_state.num_processes = 3
if "num_resources" not in st.session_state:
    st.session_state.num_resources = 3
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_sequence" not in st.session_state:
    st.session_state.last_sequence = []
if "last_deadlocked" not in st.session_state:
    st.session_state.last_deadlocked = []
if "last_trace" not in st.session_state:
    st.session_state.last_trace = []
if "example_choice" not in st.session_state:
    st.session_state.example_choice = "Manual Input"

# ============================================================
# HELPERS
# ============================================================

def matrix_key(kind, i, j):
    return f"{kind}_{i}_{j}"


def available_key(j):
    return f"available_{j}"


def ensure_widget_state(rows, cols):
    for i in range(rows):
        for j in range(cols):
            for kind in ("allocation", "request"):
                key = matrix_key(kind, i, j)
                if key not in st.session_state:
                    st.session_state[key] = 0

    for j in range(cols):
        key = available_key(j)
        if key not in st.session_state:
            st.session_state[key] = 0


def read_matrix(kind, rows, cols):
    return [
        [int(st.session_state[matrix_key(kind, i, j)]) for j in range(cols)]
        for i in range(rows)
    ]


def read_available(cols):
    return [int(st.session_state[available_key(j)]) for j in range(cols)]


def set_inputs(allocation, request, available):
    rows = len(allocation)
    cols = len(available)

    st.session_state.num_processes = rows
    st.session_state.num_resources = cols


    for i in range(rows):
        for j in range(cols):
            st.session_state[matrix_key("allocation", i, j)] = int(allocation[i][j])
            st.session_state[matrix_key("request", i, j)] = int(request[i][j])

    for j in range(cols):
        st.session_state[available_key(j)] = int(available[j])

    st.session_state.last_result = None
    st.session_state.last_sequence = []
    st.session_state.last_deadlocked = []
    st.session_state.last_trace = []


def normalize_matrix(matrix, rows, cols):
    result = []
    for i in range(rows):
        row = []
        for j in range(cols):
            try:
                value = int(matrix[i][j])
            except (IndexError, TypeError, ValueError):
                value = 0
            row.append(max(0, value))
        result.append(row)
    return result


def detection_algorithm(allocation, request, available):
    work = available[:]
    finish = [False] * len(allocation)
    sequence = []
    trace = [f"Initial Available (Work) = {work}"]

    while True:
        found = False

        for i in range(len(allocation)):
            if finish[i]:
                continue

            can_finish = all(
                request[i][j] <= work[j]
                for j in range(len(available))
            )

            if can_finish:
                old_work = work[:]

                for j in range(len(available)):
                    work[j] += allocation[i][j]

                finish[i] = True
                sequence.append(i)
                found = True

                trace.append(
                    f"P{i + 1} can complete because Request <= Work. "
                    f"Work changes from {old_work} to {work}."
                )

        if not found:
            break

    deadlocked = [i for i in range(len(allocation)) if not finish[i]]

    if deadlocked:
        trace.append("No remaining process can complete with the available resources.")
        trace.append(
            "Deadlock remains among: "
            + ", ".join(f"P{i + 1}" for i in deadlocked)
        )
        return False, sequence, deadlocked, trace

    trace.append("All processes can complete. No deadlock is detected.")
    return True, sequence, deadlocked, trace


def load_dataset(allocation, request, available):
    rows = len(allocation)
    cols = len(available)

    st.session_state.num_processes = rows
    st.session_state.num_resources = cols

    st.session_state.system_processes = rows
    st.session_state.system_resources = cols

    for i in range(rows):
        for j in range(cols):
            st.session_state[matrix_key("allocation", i, j)] = int(allocation[i][j])
            st.session_state[matrix_key("request", i, j)] = int(request[i][j])

    for j in range(cols):
        st.session_state[available_key(j)] = int(available[j])

    st.session_state.last_result = None
    st.session_state.last_sequence = []
    st.session_state.last_deadlocked = []
    st.session_state.last_trace = []

    st.session_state.example_choice = (
        "No Deadlock Example"
        if available == NO_DEADLOCK_AVAILABLE
        else "Deadlock Example"
    )
    


def reset_project():
    allocation = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]

    request = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]

    available = [0, 0, 0]

    st.session_state.num_processes = 3
    st.session_state.num_resources = 3
    st.session_state.system_processes = 3
    st.session_state.system_resources = 3

    for i in range(3):
        for j in range(3):
            st.session_state[matrix_key("allocation", i, j)] = allocation[i][j]
            st.session_state[matrix_key("request", i, j)] = request[i][j]

    for j in range(3):
        st.session_state[available_key(j)] = available[j]

    st.session_state.last_result = None
    st.session_state.last_sequence = []
    st.session_state.last_deadlocked = []
    st.session_state.last_trace = []
    st.session_state.example_choice = "Manual Input"

# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">🔒 Deadlock Detection & Prevention Simulator</div>
        <div class="hero-subtitle">Operating Systems Mini Project</div>
        <div class="hero-description">
            Simulate processes and resources, detect deadlocks, and analyze prevention strategies.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

n = st.session_state.num_processes
m = st.session_state.num_resources
ensure_widget_state(n, m)

# ============================================================
# QUICK METRICS
# ============================================================

current_available = read_available(m)
current_allocation = read_matrix("allocation", n, m)
allocated_units = sum(sum(row) for row in current_allocation)

mc1, mc2, mc3, mc4 = st.columns(4)

with mc1:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">⚙️ Processes</div>'
        f'<div class="metric-value">{n}</div></div>',
        unsafe_allow_html=True
    )

with mc2:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">📦 Resources</div>'
        f'<div class="metric-value">{m}</div></div>',
        unsafe_allow_html=True
    )

with mc3:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">🟢 Available Units</div>'
        f'<div class="metric-value">{sum(current_available)}</div></div>',
        unsafe_allow_html=True
    )

with mc4:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">📊 Allocated Units</div>'
        f'<div class="metric-value">{allocated_units}</div></div>',
        unsafe_allow_html=True
    )

st.write("")

# ============================================================
# TABS
# ============================================================

detection_tab, prevention_tab, visual_tab, info_tab = st.tabs([
    "🔍 Detection",
    "🛡️ Prevention",
    "🕸️ Visualization",
    "📘 Project Info"
])

# ============================================================
# DETECTION TAB
# ============================================================

with detection_tab:

    st.markdown("## 🎯 Example Datasets")
    st.markdown(
        '<div class="section-note">Load a ready-made case or enter your own process and resource values.</div>',
        unsafe_allow_html=True
    )

    ex1, ex2, ex3 = st.columns([2.2, 1, 1])

    with ex1:
        choice = st.selectbox(
            "Example Dataset",
            ["Manual Input", "No Deadlock Example", "Deadlock Example"],
            index=["Manual Input", "No Deadlock Example", "Deadlock Example"].index(
                st.session_state.example_choice
            ),
            key="example_selector"
        )
        st.session_state.example_choice = choice

    with ex2:
        st.write("")
        st.write("")
        if st.button(
            "📥 Load Example",
            use_container_width=True,
            disabled=(choice == "Manual Input")
        ):
            if choice == "No Deadlock Example":
                load_dataset(
                    NO_DEADLOCK_ALLOCATION,
                    NO_DEADLOCK_REQUEST,
                    NO_DEADLOCK_AVAILABLE
                )
            else:
                load_dataset(
                    DEADLOCK_ALLOCATION,
                    DEADLOCK_REQUEST,
                    DEADLOCK_AVAILABLE
                )
            st.rerun()

    with ex3:
        st.write("")
        st.write("")
        if st.button("🔄 Reset", use_container_width=True):
            reset_project()
            st.rerun()

    st.divider()

    st.markdown("## ⚙️ System Configuration")

    c1, c2 = st.columns(2)

    with c1:
        new_processes = st.number_input(
            "Number of Processes",
            min_value=1,
            max_value=10,
            step=1,
            key="system_processes",
            value=n
        )

    with c2:
        new_resources = st.number_input(
            "Number of Resources",
            min_value=1,
            max_value=10,
            step=1,
            key="system_resources",
            value=m
        )

    if new_processes != n or new_resources != m:
        old_allocation = read_matrix("allocation", n, m)
        old_request = read_matrix("request", n, m)
        old_available = read_available(m)

        resized_allocation = normalize_matrix(old_allocation, new_processes, new_resources)
        resized_request = normalize_matrix(old_request, new_processes, new_resources)
        resized_available = [
            old_available[j] if j < len(old_available) else 0
            for j in range(new_resources)
        ]

        set_inputs(resized_allocation, resized_request, resized_available)
        st.rerun()

    st.caption("You can simulate up to 10 processes and 10 resources.")

    st.divider()

    st.markdown("## 🔍 Deadlock Detection")
    st.markdown(
        '<div class="section-note">Enter the current allocation, remaining requests, and available resources.</div>',
        unsafe_allow_html=True
    )

    n = st.session_state.num_processes
    m = st.session_state.num_resources
    ensure_widget_state(n, m)

    left, right = st.columns(2, gap="large")

    with left:
        with st.container(border=True):
            st.markdown("### 📦 Allocation Matrix")
            st.caption("Resources currently allocated to each process.")

            header = st.columns([1] + [2] * m)
            header[0].write("**Process**")
            for j in range(m):
                header[j + 1].write(f"**R{j + 1}**")

            for i in range(n):
                cols = st.columns([1] + [2] * m)
                cols[0].write(f"**P{i + 1}**")
                for j in range(m):
                    cols[j + 1].number_input(
                        f"Allocation P{i + 1} R{j + 1}",
                        min_value=0,
                        max_value=100,
                        step=1,
                        key=matrix_key("allocation", i, j),
                        label_visibility="collapsed"
                    )

    with right:
        with st.container(border=True):
            st.markdown("### 📋 Request Matrix")
            st.caption("Resources still requested by each process.")

            header = st.columns([1] + [2] * m)
            header[0].write("**Process**")
            for j in range(m):
                header[j + 1].write(f"**R{j + 1}**")

            for i in range(n):
                cols = st.columns([1] + [2] * m)
                cols[0].write(f"**P{i + 1}**")
                for j in range(m):
                    cols[j + 1].number_input(
                        f"Request P{i + 1} R{j + 1}",
                        min_value=0,
                        max_value=100,
                        step=1,
                        key=matrix_key("request", i, j),
                        label_visibility="collapsed"
                    )

    st.write("")
    st.markdown("### 🟢 Available Resources")
    st.caption("Resources currently free and available to satisfy requests.")

    available_cols = st.columns(m)
    for j in range(m):
        with available_cols[j]:
            st.number_input(
                f"R{j + 1} Available",
                min_value=0,
                max_value=100,
                step=1,
                key=available_key(j)
            )

    st.write("")

    if st.button("🔎  Detect Deadlock", use_container_width=True, type="primary"):
        allocation = read_matrix("allocation", n, m)
        request = read_matrix("request", n, m)
        available = read_available(m)

        result, sequence, deadlocked, trace = detection_algorithm(
            allocation, request, available
        )

        st.session_state.last_result = result
        st.session_state.last_sequence = sequence
        st.session_state.last_deadlocked = deadlocked
        st.session_state.last_trace = trace
        st.rerun()

    if st.session_state.last_result is not None:
        if st.session_state.last_result:
            st.markdown(
                '<div class="result-safe">🟢 NO DEADLOCK DETECTED</div>',
                unsafe_allow_html=True
            )

            sequence_text = " → ".join(
                f"P{i + 1}" for i in st.session_state.last_sequence
            )
            st.info(f"**Process completion order:** {sequence_text}")
        else:
            st.markdown(
                '<div class="result-deadlock">🔴 DEADLOCK DETECTED</div>',
                unsafe_allow_html=True
            )

            deadlocked_text = ", ".join(
                f"P{i + 1}" for i in st.session_state.last_deadlocked
            )
            st.error(f"**Deadlocked processes:** {deadlocked_text}")

    with st.expander("🪜 Step-by-Step Detection", expanded=False):
        if not st.session_state.last_trace:
            st.info("Click **Detect Deadlock** to generate the detection steps.")
        else:
            for index, step in enumerate(st.session_state.last_trace, start=1):
                st.write(f"**Step {index}:** {step}")

# ============================================================
# PREVENTION TAB
# ============================================================

with prevention_tab:

    st.markdown("## 🛡️ Deadlock Prevention")
    st.markdown(
        '<div class="section-note">Deadlock prevention works by ensuring that at least one necessary deadlock condition cannot occur.</div>',
        unsafe_allow_html=True
    )

    p1, p2 = st.columns(2, gap="large")

    with p1:
        with st.expander("1️⃣ Mutual Exclusion",expanded=True):
            st.write("**Condition:** At least one resource is non-shareable.")
            st.write("**Prevention:** Make resources shareable whenever possible.")
            st.write("**Limitation:** Some hardware resources cannot be safely shared.")

        with st.expander("2️⃣ Hold and Wait",expanded=True):
            st.write("**Condition:** A process holds resources while waiting for another resource.")
            st.write("**Prevention:** Request all required resources together, or release held resources before requesting new ones.")
            st.write("**Trade-off:** Resource utilization may decrease.")

    with p2:
        with st.expander("3️⃣ No Preemption",expanded=True):
            st.write("**Condition:** A resource cannot normally be taken from a process until it releases it.")
            st.write("**Prevention:** Allow resources to be released and reassigned when necessary.")
            st.write("**Trade-off:** Previously performed work may need to be repeated.")

        with st.expander("4️⃣ Circular Wait",expanded=True):
            st.write("**Condition:** Processes form a circular waiting chain.")
            st.write("**Prevention:** Impose a fixed ordering on resource requests.")
            st.write("**Example:** R1 → R2 → R3.")

    n = st.session_state.num_processes
    m = st.session_state.num_resources
    ensure_widget_state(n, m)
    allocation = read_matrix("allocation", n, m)
    request = read_matrix("request", n, m)

    with st.expander("🔎 Current Input Prevention Analysis", expanded=False):
        hold_wait_processes = []

        for i in range(n):
            holding = any(allocation[i][j] > 0 for j in range(m))
            waiting = any(request[i][j] > 0 for j in range(m))
            if holding and waiting:
                hold_wait_processes.append(i)

        if hold_wait_processes:
            names = ", ".join(f"P{i + 1}" for i in hold_wait_processes)
            st.warning(f"⚠️ Hold-and-Wait condition may exist for: **{names}**")
        else:
            st.success("✅ No Hold-and-Wait condition detected in the current input.")

        ordering_violation = []

        for i in range(n):
            held = [j for j in range(m) if allocation[i][j] > 0]
            requested = [j for j in range(m) if request[i][j] > 0]

            if held and requested:
                highest_held = max(held)
                if any(j < highest_held for j in requested):
                    ordering_violation.append(i)

        if ordering_violation:
            names = ", ".join(f"P{i + 1}" for i in ordering_violation)
            st.warning(f"⚠️ Resource-ordering violation detected for: **{names}**")
        else:
            st.success("✅ No resource-ordering violation detected.")

    with st.expander("📌 Prevention Summary", expanded=False):
        st.table({
            "Deadlock Condition": [
                "Mutual Exclusion",
                "Hold and Wait",
                "No Preemption",
                "Circular Wait"
            ],
            "Prevention Approach": [
                "Share resources whenever possible",
                "Request all resources together or release before requesting",
                "Allow resources to be released and reassigned when necessary",
                "Impose a fixed order on resource requests"
            ]
        })

# ============================================================
# VISUALIZATION TAB
# ============================================================

with visual_tab:

    st.markdown("## 🕸️ Resource Allocation Graph")
    st.markdown(
        '<div class="section-note">Visualize processes, resources, allocations, and requests.</div>',
        unsafe_allow_html=True
    )

    n = st.session_state.num_processes
    m = st.session_state.num_resources
    ensure_widget_state(n, m)
    allocation = read_matrix("allocation", n, m)
    request = read_matrix("request", n, m)
    available = read_available(m)

    graph = Digraph()
    graph.attr(rankdir="LR")

    for i in range(n):
        graph.node(f"P{i + 1}", f"P{i + 1}", shape="circle")

    for j in range(m):
        graph.node(f"R{j + 1}", f"R{j + 1}", shape="box")

    for i in range(n):
        for j in range(m):
            if allocation[i][j] > 0:
                graph.edge(
                    f"R{j + 1}",
                    f"P{i + 1}",
                    label=str(allocation[i][j])
                )

            if request[i][j] > 0:
                graph.edge(
                    f"P{i + 1}",
                    f"R{j + 1}",
                    label=str(request[i][j]),
                    style="dashed"
                )

    st.graphviz_chart(graph, use_container_width=True)
    st.caption(
        "Solid arrows: Resource → Process = allocated resource | "
        "Dashed arrows: Process → Resource = requested resource"
    )

    st.divider()

    st.markdown("## 📊 System Dashboard")
    d1, d2, d3, d4 = st.columns(4)

    with d1:
        st.metric("Processes", n)
    with d2:
        st.metric("Resources", m)
    with d3:
        st.metric("Available Units", sum(available))
    with d4:
        st.metric("Allocated Units", sum(sum(row) for row in allocation))

# ============================================================
# PROJECT INFO TAB
# ============================================================

with info_tab:

    st.markdown("## 📘 Project Information")
    st.markdown(
        '<div class="section-note">Main concepts demonstrated by this mini-project.</div>',
        unsafe_allow_html=True
    )

    a, b, c = st.columns(3, gap="large")

    with a:
        with st.container(border=True):
            st.markdown("### 🔍 Deadlock Detection")
            st.write("• Allocation Matrix")
            st.write("• Request Matrix")
            st.write("• Available Resources")
            st.write("• Detection Algorithm")
            st.write("• Deadlocked Processes")
            st.write("• Step-by-Step Execution")

    with b:
        with st.container(border=True):
            st.markdown("### 🛡️ Deadlock Prevention")
            st.write("• Mutual Exclusion")
            st.write("• Hold and Wait")
            st.write("• No Preemption")
            st.write("• Circular Wait")
            st.write("• Resource Ordering")

    with c:
        with st.container(border=True):
            st.markdown("### 🕸️ Resource Allocation Graph")
            st.write("• Process Nodes")
            st.write("• Resource Nodes")
            st.write("• Allocation Edges")
            st.write("• Request Edges")
            st.write("• Visual Representation")

