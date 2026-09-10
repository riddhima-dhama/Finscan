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

    # -----------------------------------------------------
    # Nodes
    # -----------------------------------------------------

    for state_set, state_number in state_sets.items():

        nfa_ids = sorted(
            state.id
            for state in state_set
        )

        if nfa_ids:

            subset = "{" + ",".join(
                f"q{i}"
                for i in nfa_ids
            ) + "}"

        else:

            subset = "∅"

        nodes.append({

            "id": f"D{state_number}",

            "label": (
                f"D{state_number}\n"
                f"{subset}"
            ),

            "is_start": (
                state_number == start_state
            ),

            "is_final": (
                state_number in accept_states
            )
        })

    # -----------------------------------------------------
    # Edges
    # -----------------------------------------------------

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
# GET NFA SUBSET FOR A DFA STATE
# =========================================================

def get_dfa_subset(dfa, dfa_state):

    for state_set, state_number in dfa["state_sets"].items():

        if state_number == dfa_state:

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

    state_groups = min_dfa["state_groups"]

    # -----------------------------------------------------
    # Nodes
    # -----------------------------------------------------

    for min_state in sorted(state_groups):

        group = sorted(
            state_groups[min_state]
        )

        # ---------------------------------------------
        # Original DFA states
        # ---------------------------------------------

        dfa_states_text = ",".join(
            f"D{state}"
            for state in group
        )

        # ---------------------------------------------
        # Corresponding NFA subsets
        # ---------------------------------------------

        subsets = []

        for dfa_state in group:

            subset = get_dfa_subset(
                original_dfa,
                dfa_state
            )

            if subset not in subsets:
                subsets.append(subset)

        subset_text = " ".join(
            subsets
        )

        # ---------------------------------------------
        # Final node label
        # ---------------------------------------------

        label = (
            f"M{min_state}\n"
            f"{dfa_states_text}\n"
            f"{subset_text}"
        )

        nodes.append({

            "id": f"M{min_state}",

            "label": label,

            "is_start": (
                min_state == start_state
            ),

            "is_final": (
                min_state in accept_states
            )
        })

    # -----------------------------------------------------
    # Edges
    # -----------------------------------------------------

    for from_state, symbol_map in transitions.items():

        for symbol, to_state in symbol_map.items():

            edges.append({

                "from": f"M{from_state}",

                "to": f"M{to_state}",

                "label": symbol
            })

    return {
        "nodes": nodes,
        "edges": edges
    }


# =========================================================
# BUILD COMPLETE VISUALIZATION
# =========================================================

def build_automata_visualization(regex):

    regex = regex.strip()

    if not regex:
        raise ValueError(
            "Regex cannot be empty."
        )

    # Reset state numbering
    State.counter = 0

    # -----------------------------------------------------
    # REGEX → NFA
    # -----------------------------------------------------

    nfa = regex_to_nfa(regex)

    nfa_graph = serialize_nfa(
        nfa
    )

    # -----------------------------------------------------
    # NFA → DFA
    # -----------------------------------------------------

    dfa = nfa_to_dfa(
        nfa
    )

    dfa_graph = serialize_dfa(
        dfa
    )

    # -----------------------------------------------------
    # DFA → MIN DFA
    # -----------------------------------------------------

    min_dfa = minimize_dfa(
        dfa
    )

    min_dfa_graph = serialize_min_dfa(
        min_dfa,
        dfa
    )

    # -----------------------------------------------------
    # RETURN
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