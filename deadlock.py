"""Core deadlock algorithms (no UI code, so they are easy to test and explain)."""


def find_deadlock(alloc, req, avail):
    """Detection / safety algorithm.

    `req` is the Request matrix (detection) or the Need matrix (Banker's).
    Returns (finish_order, deadlocked_processes, steps) where each step is
    (process, work_before, work_after).
    """
    n, m = len(alloc), len(avail)
    work, done, order, steps = list(avail), [False] * n, [], []
    progress = True
    while progress:
        progress = False
        for i in range(n):
            if not done[i] and all(req[i][j] <= work[j] for j in range(m)):
                before = list(work)
                work = [work[j] + alloc[i][j] for j in range(m)]
                done[i] = True
                order.append(i)
                steps.append((i, before, list(work)))
                progress = True
    return order, [i for i in range(n) if not done[i]], steps


def need_matrix(mx, alloc):
    """Need = Max - Allocation."""
    return [[mx[i][j] - alloc[i][j] for j in range(len(alloc[0]))]
            for i in range(len(alloc))]


def request_check(alloc, need, avail, p, rq):
    """Banker's resource-request algorithm. Returns (granted, message, safe_order)."""
    m = len(avail)
    if any(rq[j] > need[p][j] for j in range(m)):
        return False, "Rejected: request exceeds the process's remaining need (max claim).", []
    if any(rq[j] > avail[j] for j in range(m)):
        return False, "Must wait: requested resources are not currently available.", []
    a2 = [r[:] for r in alloc]
    n2 = [r[:] for r in need]
    for j in range(m):
        a2[p][j] += rq[j]
        n2[p][j] -= rq[j]
    order, unsafe, _ = find_deadlock(a2, n2, [avail[j] - rq[j] for j in range(m)])
    if unsafe:
        return False, "Denied: granting this request leads to an UNSAFE state.", []
    return True, "Granted: the system stays in a SAFE state.", order


def recover_by_termination(alloc, req, avail):
    """Recovery: repeatedly terminate the deadlocked process holding the most
    resources until no deadlock remains. Returns the list of victims."""
    alloc, req, avail = [r[:] for r in alloc], [r[:] for r in req], list(avail)
    victims = []
    while True:
        _, bad, _ = find_deadlock(alloc, req, avail)
        if not bad:
            return victims
        v = max(bad, key=lambda i: sum(alloc[i]))
        avail = [a + b for a, b in zip(avail, alloc[v])]
        alloc[v], req[v] = [0] * len(avail), [0] * len(avail)
        victims.append(v)


def hold_and_wait(alloc, req):
    """Processes that hold some resources while requesting more."""
    return [i for i in range(len(alloc)) if sum(alloc[i]) > 0 and sum(req[i]) > 0]


def ordering_violations(alloc, req):
    """Circular-wait prevention: a process holding R_k may only request R_j with j >= k.
    Returns (process, held_resource, requested_resource) for each violation."""
    return [(i, k, j)
            for i in range(len(alloc)) for j in range(len(req[i])) if req[i][j] > 0
            for k in range(len(alloc[i])) if alloc[i][k] > 0 and k > j]
