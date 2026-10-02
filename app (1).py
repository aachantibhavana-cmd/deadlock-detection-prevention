import pandas as pd
import streamlit as st
from graphviz import Digraph

import deadlock as dl

st.set_page_config(page_title="Deadlock Simulator", page_icon="🔒", layout="wide")

# ---------------- examples & state ----------------
_A = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]
_M = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]
EXAMPLES = {
    "Deadlock (circular wait, 3x3)": {
        "alloc": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        "req": [[0, 1, 0], [0, 0, 1], [1, 0, 0]],
        "mx": [[1, 1, 0], [0, 1, 1], [1, 0, 1]],
        "avail": [[0, 0, 0]]},
    "Safe state (textbook, 5x3)": {
        "alloc": _A,
        "req": [[x - y for x, y in zip(r, s)] for r, s in zip(_M, _A)],
        "mx": _M,
        "avail": [[3, 3, 2]]},
}


def reset():
    st.session_state.update(
        n=3, m=3, ver=st.session_state.get("ver", 0) + 1,
        data={"alloc": [[0] * 3 for _ in range(3)], "req": [[0] * 3 for _ in range(3)],
              "mx": [[0] * 3 for _ in range(3)], "avail": [[0] * 3]})


def load(name):
    e = EXAMPLES[name]
    st.session_state.update(n=len(e["alloc"]), m=len(e["avail"][0]),
                            ver=st.session_state.ver + 1, data=dict(e))


if "data" not in st.session_state:
    reset()


def grid(key, rows, m, labels):
    """Editable matrix; keeps values when the matrix size changes."""
    old = st.session_state.data[key]
    vals = [[old[i][j] if i < len(old) and j < len(old[0]) else 0 for j in range(m)]
            for i in range(rows)]
    df = pd.DataFrame(vals, index=labels, columns=[f"R{j}" for j in range(m)])
    cfg = {c: st.column_config.NumberColumn(min_value=0, max_value=99, step=1)
           for c in df.columns}
    out = st.data_editor(df, column_config=cfg,
                         key=f"{key}{st.session_state.ver}_{rows}_{m}")
    res = out.fillna(0).astype(int).values.tolist()
    st.session_state.data[key] = res
    return res


def names(ids):
    return ", ".join(f"P{i}" for i in ids)


def trace(steps, bad, alloc, matrix, avail, label):
    for k, (i, before, after) in enumerate(steps, 1):
        st.write(f"**Step {k} - P{i}:** {label} {matrix[i]} <= Work {before} -> can finish, "
                 f"releases {alloc[i]} -> Work = {after}")
    work = steps[-1][2] if steps else avail
    for i in bad:
        st.write(f"❌ **P{i}:** {label} {matrix[i]} > Work {work} -> must keep waiting")


# ---------------- header & inputs ----------------
st.title("🔒 Deadlock Detection, Avoidance & Prevention Simulator")
st.caption(STUDENT)

c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
choice = c1.selectbox("Example datasets", list(EXAMPLES))
c1.button("📥 Load example", on_click=load, args=(choice,))
c1.button("🔄 Reset", on_click=reset)
n = c2.number_input("Processes", 1, 10, key="n")
m = c3.number_input("Resources", 1, 10, key="m")
P = [f"P{i}" for i in range(n)]

st.subheader("Input matrices")
a, b = st.columns(2)
with a:
    st.caption("Allocation (currently held)")
    alloc = grid("alloc", n, m, P)
with b:
    st.caption("Request (still waiting for - used by detection)")
    req = grid("req", n, m, P)
with a:
    st.caption("Max claim (used by Banker's algorithm)")
    mx = grid("mx", n, m, P)
with b:
    st.caption("Available")
    avail = grid("avail", 1, m, ["Avail"])[0]

total = [avail[j] + sum(alloc[i][j] for i in range(n)) for j in range(m)]
st.info("Total instances of each resource (Allocation + Available): "
        + ", ".join(f"R{j} = {t}" for j, t in enumerate(total)))

tab1, tab2, tab3 = st.tabs(["🔍 Detection & Recovery", "🏦 Avoidance (Banker's)", "🛡️ Prevention"])

# ---------------- detection ----------------
with tab1:
    order, bad, steps = dl.find_deadlock(alloc, req, avail)
    if bad:
        st.error(f"🔴 DEADLOCK DETECTED - deadlocked processes: {names(bad)}")
    else:
        st.success("🟢 NO DEADLOCK - all processes can finish in order: "
                   + " → ".join(f"P{i}" for i in order))
    with st.expander("Step-by-step detection trace", expanded=True):
        trace(steps, bad, alloc, req, avail, "Request")

    st.subheader("Resource Allocation Graph")
    g = Digraph(graph_attr={"rankdir": "LR"})
    for i in range(n):
        g.node(f"P{i}", shape="circle", style="filled",
               fillcolor="#f8b4b4" if i in bad else "#cfe8ff")
    for j in range(m):
        g.node(f"R{j}", shape="box")
    for i in range(n):
        for j in range(m):
            if alloc[i][j] > 0:
                g.edge(f"R{j}", f"P{i}", label=str(alloc[i][j]))
            if req[i][j] > 0:
                g.edge(f"P{i}", f"R{j}", label=str(req[i][j]), style="dashed",
                       color="red" if i in bad else "black")
    st.graphviz_chart(g)
    st.caption("Solid arrow: resource allocated to process. Dashed arrow: process requests "
               "resource. Red nodes: deadlocked processes.")

    if bad:
        st.subheader("Recovery by process termination")
        victims = dl.recover_by_termination(alloc, req, avail)
        st.warning("Terminate (most resources held first): " + " → ".join(f"P{v}" for v in victims)
                   + ". After this, the remaining processes can finish.")

# ---------------- avoidance ----------------
with tab2:
    need = dl.need_matrix(mx, alloc)
    if any(v < 0 for row in need for v in row):
        st.error("Invalid input: Max claim must be >= Allocation for every process/resource.")
    else:
        st.write("**Need = Max - Allocation**")
        st.dataframe(pd.DataFrame(need, index=P, columns=[f"R{j}" for j in range(m)]))
        order, bad, steps = dl.find_deadlock(alloc, need, avail)
        if bad:
            st.error(f"🔴 UNSAFE STATE - processes that cannot be guaranteed to finish: {names(bad)}")
        else:
            st.success("🟢 SAFE STATE - safe sequence: " + " → ".join(f"P{i}" for i in order))
        with st.expander("Safety algorithm trace"):
            trace(steps, bad, alloc, need, avail, "Need")

        st.subheader("Resource-request check")
        p = st.selectbox("Process making the request", range(n), format_func=lambda i: f"P{i}")
        cols = st.columns(m)
        rq = [cols[j].number_input(f"R{j}", 0, 99, 0, key=f"rq{j}") for j in range(m)]
        if st.button("Check request"):
            ok, msg, seq = dl.request_check(alloc, need, avail, p, rq)
            (st.success if ok else st.error)(msg)
            if ok:
                st.write("Safe sequence after granting: " + " → ".join(f"P{i}" for i in seq))

# ---------------- prevention ----------------
with tab3:
    st.write("Prevention makes sure at least one of the four Coffman conditions can never hold.")
    st.table(pd.DataFrame({
        "Condition": ["Mutual exclusion", "Hold and wait", "No preemption", "Circular wait"],
        "How to prevent it": ["Make resources shareable (e.g. read-only files)",
                              "Request all resources at once, or release before requesting",
                              "Allow the OS to take resources away from waiting processes",
                              "Number resources; request only in increasing order"],
        "Drawback": ["Not possible for printers, locks, etc.",
                     "Low utilisation, starvation",
                     "Only works for saveable state (CPU, memory)",
                     "Fixed order can be inconvenient"]}))

    st.subheader("Check the current input against two prevention rules")
    hw = dl.hold_and_wait(alloc, req)
    if hw:
        st.warning(f"Hold and wait exists: {names(hw)} hold resources while waiting for more.")
    else:
        st.success("No process holds resources while waiting for more.")
    viol = dl.ordering_violations(alloc, req)
    if viol:
        for i, k, j in viol:
            st.error(f"P{i} holds R{k} but requests R{j} - breaks resource ordering, so a "
                     f"circular wait is possible.")
    else:
        st.success("All requests follow the order R0 < R1 < R2 ..., so circular wait is impossible.")

st.divider()
st.caption("Operating Systems Mini Project | Deadlock Detection, Avoidance and Prevention")
