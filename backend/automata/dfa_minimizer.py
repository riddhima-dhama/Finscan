# =========================================================
# DFA MINIMIZATION
# =========================================================

def minimize_dfa(dfa):

    transitions = dfa["transitions"]
    alphabet = sorted(dfa["alphabet"])
    start_state = dfa["start_state"]
    accept_states = set(dfa["accept_states"])

    # -----------------------------------------------------
    # Collect all DFA states
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
    # Make sure every state has every transition
    #
    # Missing transition -> dead state
    # -----------------------------------------------------

    dead_state = None

    for state in all_states:

        for symbol in alphabet:

            if symbol not in transitions.get(state, {}):

                if dead_state is None:
                    dead_state = max(all_states) + 1

                    all_states.append(dead_state)

                    transitions[dead_state] = {}

                transitions.setdefault(state, {})[symbol] = dead_state

    # Dead state loops to itself
    if dead_state is not None:

        for symbol in alphabet:
            transitions[dead_state][symbol] = dead_state

    # -----------------------------------------------------
    # Initial partition
    #
    # FINAL states vs NON-FINAL states
    # -----------------------------------------------------

    final_group = set(accept_states)

    non_final_group = (
        set(all_states) - final_group
    )

    partitions = []

    if final_group:
        partitions.append(final_group)

    if non_final_group:
        partitions.append(non_final_group)

    # -----------------------------------------------------
    # Partition Refinement
    # -----------------------------------------------------

    changed = True

    while changed:

        changed = False

        state_to_group = {}

        for group_index, group in enumerate(partitions):

            for state in group:
                state_to_group[state] = group_index

        new_partitions = []

        for group in partitions:

            buckets = {}

            for state in group:

                signature = tuple(
                    state_to_group[
                        transitions[state][symbol]
                    ]
                    for symbol in alphabet
                )

                if signature not in buckets:
                    buckets[signature] = set()

                buckets[signature].add(state)

            if len(buckets) > 1:
                changed = True

            new_partitions.extend(
                buckets.values()
            )

        partitions = new_partitions

    # -----------------------------------------------------
    # Sort partitions so numbering is stable
    #
    # Start-state group becomes M0
    # -----------------------------------------------------

    start_group_index = None

    for index, group in enumerate(partitions):

        if start_state in group:
            start_group_index = index
            break

    if start_group_index is not None:

        start_group = partitions.pop(
            start_group_index
        )

        partitions.insert(
            0,
            start_group
        )

    # -----------------------------------------------------
    # Assign minimized state numbers
    # -----------------------------------------------------

    state_map = {}

    state_groups = {}

    for min_state, group in enumerate(partitions):

        state_groups[min_state] = set(group)

        for original_state in group:

            state_map[original_state] = min_state

    # -----------------------------------------------------
    # Build minimized transitions
    # -----------------------------------------------------

    min_transitions = {}

    for min_state, group in state_groups.items():

        representative = sorted(group)[0]

        min_transitions[min_state] = {}

        for symbol in alphabet:

            destination = transitions[
                representative
            ][symbol]

            min_transitions[min_state][symbol] = (
                state_map[destination]
            )

    # -----------------------------------------------------
    # Minimized accepting states
    # -----------------------------------------------------

    min_accept_states = set()

    for min_state, group in state_groups.items():

        if group & accept_states:
            min_accept_states.add(min_state)

    # -----------------------------------------------------
    # Return minimized DFA
    # -----------------------------------------------------

    return {

        "start_state": 0,

        "accept_states": min_accept_states,

        "transitions": min_transitions,

        "alphabet": set(alphabet),

        # IMPORTANT:
        # Mapping from minimized states
        # to original DFA states
        "state_groups": state_groups,

        # Mapping from original DFA states
        # to minimized DFA states
        "state_map": state_map
    }