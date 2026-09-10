from automata.regex_to_nfa import regex_to_nfa


# =========================================================
# EPSILON CLOSURE
# =========================================================

def epsilon_closure(states):

    closure = set(states)

    stack = list(states)

    while stack:

        state = stack.pop()

        for next_state in state.transitions.get("ε", []):

            if next_state not in closure:

                closure.add(next_state)

                stack.append(next_state)

    return closure


# =========================================================
# MOVE
# =========================================================

def move(states, symbol):

    result = set()

    for state in states:

        for next_state in state.transitions.get(
            symbol,
            []
        ):

            result.add(next_state)

    return result


# =========================================================
# GET ALPHABET
# =========================================================

def get_alphabet(start_state):

    alphabet = set()

    visited = set()

    stack = [start_state]

    while stack:

        state = stack.pop()

        if state in visited:
            continue

        visited.add(state)


        for symbol, next_states in state.transitions.items():

            # Ignore epsilon transitions
            if symbol != "ε":

                alphabet.add(symbol)


            for next_state in next_states:

                if next_state not in visited:

                    stack.append(next_state)


    return alphabet


# =========================================================
# NFA -> DFA
# =========================================================

def nfa_to_dfa(nfa):

    # -----------------------------------------------------
    # Find alphabet
    # -----------------------------------------------------

    alphabet = get_alphabet(
        nfa.start
    )


    # -----------------------------------------------------
    # Start state
    #
    # DFA start state is epsilon closure
    # of NFA start state.
    # -----------------------------------------------------

    start_closure = frozenset(
        epsilon_closure(
            {nfa.start}
        )
    )


    # -----------------------------------------------------
    # DFA state numbering
    #
    # frozenset of NFA states -> DFA state number
    # -----------------------------------------------------

    dfa_states = {

        start_closure: 0

    }


    # -----------------------------------------------------
    # DFA transitions
    #
    # DFA state number ->
    #     symbol -> destination DFA state
    # -----------------------------------------------------

    dfa_transitions = {}


    # -----------------------------------------------------
    # Accepting states
    # -----------------------------------------------------

    dfa_accept_states = set()


    # -----------------------------------------------------
    # BFS queue
    # -----------------------------------------------------

    queue = [
        start_closure
    ]


    # =====================================================
    # SUBSET CONSTRUCTION
    # =====================================================

    while queue:

        current = queue.pop(0)

        current_id = dfa_states[
            current
        ]


        # Create transition dictionary
        dfa_transitions[
            current_id
        ] = {}


        # -------------------------------------------------
        # Check accepting state
        # -------------------------------------------------

        if nfa.accept in current:

            dfa_accept_states.add(
                current_id
            )


        # -------------------------------------------------
        # Process EVERY alphabet symbol
        # -------------------------------------------------

        for symbol in sorted(alphabet):


            # Move from current subset
            moved = move(
                current,
                symbol
            )


            # -------------------------------------------------
            # IMPORTANT:
            #
            # If no NFA state can consume this symbol,
            # the DFA goes to the DEAD/TRAP state.
            #
            # Empty set represents the trap state.
            # -------------------------------------------------

            if not moved:

                next_closure = frozenset()

            else:

                next_closure = frozenset(
                    epsilon_closure(
                        moved
                    )
                )


            # -------------------------------------------------
            # Create new DFA state if needed
            # -------------------------------------------------

            if next_closure not in dfa_states:

                dfa_states[
                    next_closure
                ] = len(dfa_states)


                queue.append(
                    next_closure
                )


            # -------------------------------------------------
            # Store transition
            # -------------------------------------------------

            dfa_transitions[
                current_id
            ][symbol] = dfa_states[
                next_closure
            ]


    # =====================================================
    # IMPORTANT:
    #
    # The empty set is the DEAD/TRAP state.
    #
    # From the trap state, every symbol keeps us
    # inside the trap state.
    #
    # Example:
    #
    # DEAD --0--> DEAD
    # DEAD --1--> DEAD
    #
    # =====================================================

    dead_state = frozenset()


    if dead_state in dfa_states:

        dead_id = dfa_states[
            dead_state
        ]


        if dead_id not in dfa_transitions:

            dfa_transitions[
                dead_id
            ] = {}


        for symbol in sorted(alphabet):

            dfa_transitions[
                dead_id
            ][symbol] = dead_id


    # =====================================================
    # RETURN DFA
    # =====================================================

    return {

        "start_state":
            0,

        "accept_states":
            dfa_accept_states,

        "transitions":
            dfa_transitions,

        "state_sets":
            dfa_states,

        "alphabet":
            alphabet

    }


# =========================================================
# PRINT DFA
# =========================================================

def print_dfa(dfa):

    print("\n")
    print("=" * 50)

    print("DFA TRANSITIONS")

    print("=" * 50)


    for state in sorted(
        dfa["transitions"]
    ):

        transitions = dfa[
            "transitions"
        ][state]


        for symbol in sorted(
            transitions
        ):

            next_state = transitions[
                symbol
            ]


            print(
                f"D{state} --{symbol}--> D{next_state}"
            )


    print("\nStart State:")

    print(
        f"D{dfa['start_state']}"
    )


    print("\nAccept States:")


    accept = sorted(
        dfa["accept_states"]
    )


    if accept:

        print(
            ", ".join(
                f"D{x}"
                for x in accept
            )
        )

    else:

        print("None")


    print("\nAll DFA States:")


    for state_set, state_number in dfa[
        "state_sets"
    ].items():

        if state_set:

            names = ",".join(
                f"q{state.id}"
                for state in sorted(
                    state_set,
                    key=lambda s: s.id
                )
            )

            print(
                f"D{state_number} = {{{names}}}"
            )

        else:

            print(
                f"D{state_number} = ∅  (DEAD STATE)"
            )


    print("=" * 50)


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    regex = "01"

    print(
        "Regex:",
        regex
    )


    nfa = regex_to_nfa(
        regex
    )


    dfa = nfa_to_dfa(
        nfa
    )


    print_dfa(
        dfa
    )