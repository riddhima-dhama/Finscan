from automata.regex_to_nfa import regex_to_nfa, State
from automata.nfa_to_dfa import nfa_to_dfa
from automata.dfa_minimizer import minimize_dfa


# =========================================================
# NFA SERIALIZATION
# =========================================================

def serialize_nfa(nfa):
    nodes = []
    edges = []

    visited = set()
    queue = [nfa.start]

    while queue:
        state = queue.pop(0)

        if state.id in visited:
            continue

        visited.add(state.id)

        nodes.append({
            "id": f"q{state.id}",
            "label": f"q{state.id}",
            "is_start": state == nfa.start,
            "is_final": state == nfa.accept
        })

        for symbol, destinations in state.transitions.items():
            for destination in destinations:

                edges.append({
                    "from": f"q{state.id}",
                    "to": f"q{destination.id}",
                    "label": symbol
                })

                if destination.id not in visited:
                    queue.append(destination)

    return {
        "nodes": nodes,
        "edges": edges
    }


# =========================================================
# DFA SERIALIZATION
# =========================================================

def serialize_dfa(dfa):
    nodes = []
    edges = []

    state_sets = dfa["state_sets"]
    transitions = dfa["transitions"]
    start_state = dfa["start_state"]
    accept_states = dfa["accept_states"]

    for state_set, state_number in state_sets.items():

        nfa_ids = sorted(
            state.id
            for state in state_set
        )

        if nfa_ids:
            subset = "{" + ",".join(
                f"q{i}" for i in nfa_ids
            ) + "}"
        else:
            subset = "∅"

        nodes.append({
            "id": f"D{state_number}",
            "label": f"D{state_number}\n{subset}",
            "is_start": state_number == start_state,
            "is_final": state_number in accept_states
        })

    for from_state, symbol_map in transitions.items():

        for symbol, to_state in symbol_map.items():

            edges.append({
                "from": f"D{from_state}",
                "to": f"D{to_state}",
                "label": symbol
            })

    return {
        "nodes": nodes,
        "edges": edges
    }


# =========================================================
# FIND ORIGINAL DFA STATES INSIDE MINIMIZED STATE
# =========================================================

def get_minimized_state_groups(dfa, min_dfa):
    """
    Try to obtain the DFA-state groups produced by the minimizer.

    Example:
        minimized state -> {D0, D2}

    Different minimizer implementations may use different keys,
    so we check the common possibilities.
    """

    possible_keys = [
        "state_groups",
        "groups",
        "partitions",
        "state_map",
        "mapping"
    ]

    for key in possible_keys:
        if key in min_dfa:
            return min_dfa[key]

    return None


# =========================================================
# CONVERT DFA STATE TO NFA SUBSET TEXT
# =========================================================

def get_dfa_subset_text(dfa, dfa_state_number):

    for state_set, state_number in dfa["state_sets"].items():

        if state_number == dfa_state_number:

            if not state_set:
                return "∅"

            nfa_ids = sorted(
                state.id
                for state in state_set
            )

            return "{" + ",".join(
                f"q{i}"
                for i in nfa_ids
            ) + "}"

    return "?"


# =========================================================
# MINIMIZED DFA SERIALIZATION
# =========================================================

def serialize_min_dfa(min_dfa, original_dfa):

    nodes = []
    edges = []

    start_state = min_dfa["start_state"]
    accept_states = min_dfa["accept_states"]
    transitions = min_dfa["transitions"]

    # -----------------------------------------------------
    # Find every minimized state
    # -----------------------------------------------------

    all_states = set()

    all_states.add(start_state)
    all_states.update(accept_states)

    for state, symbol_map in transitions.items():

        all_states.add(state)

        for destination in symbol_map.values():
            all_states.add(destination)

    all_states = sorted(all_states)

    # -----------------------------------------------------
    # Give clean M0, M1, M2... names
    # -----------------------------------------------------

    state_map = {
        state: f"M{index}"
        for index, state in enumerate(all_states)
    }

    # -----------------------------------------------------
    # Try to find partition/group information
    # -----------------------------------------------------

    groups = get_minimized_state_groups(
        original_dfa,
        min_dfa
    )

    # -----------------------------------------------------
    # Create nodes
    # -----------------------------------------------------

    for state in all_states:

        min_name = state_map[state]

        original_states = []

        # -------------------------------------------------
        # CASE 1:
        # Minimized state itself is a set/frozenset
        # containing original DFA states.
        # -------------------------------------------------

        if isinstance(state, (set, frozenset)):

            original_states = sorted(
                list(state)
            )

        # -------------------------------------------------
        # CASE 2:
        # Minimizer returned group information
        # -------------------------------------------------

        elif groups is not None:

            try:

                if isinstance(groups, dict):

                    if state in groups:

                        value = groups[state]

                        if isinstance(
                            value,
                            (set, frozenset, list, tuple)
                        ):
                            original_states = sorted(
                                list(value)
                            )
                        else:
                            original_states = [value]

                    else:

                        # Sometimes mapping is:
                        # original DFA state -> minimized state

                        for original, minimized in groups.items():

                            if minimized == state:
                                original_states.append(
                                    original
                                )

                        original_states = sorted(
                            original_states
                        )

            except Exception:
                original_states = []

        # -------------------------------------------------
        # CASE 3:
        # Current minimizer preserves a representative
        # original DFA state.
        # -------------------------------------------------

        if not original_states:

            if isinstance(state, int):
                original_states = [state]

        # -------------------------------------------------
        # Build label
        # -------------------------------------------------

        dfa_labels = []
        subset_labels = []

        for original_state in original_states:

            if isinstance(original_state, int):

                dfa_labels.append(
                    f"D{original_state}"
                )

                subset = get_dfa_subset_text(
                    original_dfa,
                    original_state
                )

                if subset not in subset_labels:
                    subset_labels.append(subset)

        # Original DFA state line

        if dfa_labels:
            dfa_text = ",".join(dfa_labels)
        else:
            dfa_text = "D?"

        # NFA subset line

        if subset_labels:
            subset_text = " ".join(subset_labels)
        else:
            subset_text = "?"

        label = (
            f"{min_name}\n"
            f"{dfa_text}\n"
            f"{subset_text}"
        )

        nodes.append({
            "id": min_name,
            "label": label,
            "is_start": state == start_state,
            "is_final": state in accept_states
        })

    # -----------------------------------------------------
    # Create transitions
    # -----------------------------------------------------

    for from_state, symbol_map in transitions.items():

        for symbol, to_state in symbol_map.items():

            if (
                from_state not in state_map
                or to_state not in state_map
            ):
                continue

            edges.append({
                "from": state_map[from_state],
                "to": state_map[to_state],
                "label": symbol
            })

    return {
        "nodes": nodes,
        "edges": edges
    }


# =========================================================
# MAIN VISUALIZATION FUNCTION
# =========================================================

def build_automata_visualization(regex):

    regex = regex.strip()

    if not regex:
        raise ValueError(
            "Regex cannot be empty."
        )

    # Reset NFA state numbering
    State.counter = 0

    # -----------------------------------------------------
    # REGEX -> NFA
    # -----------------------------------------------------

    nfa = regex_to_nfa(regex)

    nfa_graph = serialize_nfa(
        nfa
    )

    # -----------------------------------------------------
    # NFA -> DFA
    # -----------------------------------------------------

    dfa = nfa_to_dfa(
        nfa
    )

    dfa_graph = serialize_dfa(
        dfa
    )

    # -----------------------------------------------------
    # DFA -> MIN DFA
    # -----------------------------------------------------

    min_dfa = minimize_dfa(
        dfa
    )

    min_dfa_graph = serialize_min_dfa(
        min_dfa,
        dfa
    )

    # -----------------------------------------------------
    # RETURN EVERYTHING
    # -----------------------------------------------------

    return {
        "regex": regex,

        "nfa": nfa_graph,

        "dfa": dfa_graph,

        "min_dfa": min_dfa_graph,

        "statistics": {
            "nfa_states": len(
                nfa_graph["nodes"]
            ),

            "dfa_states": len(
                dfa_graph["nodes"]
            ),

            "min_dfa_states": len(
                min_dfa_graph["nodes"]
            )
        }
    }