from automata.regex_to_nfa import regex_to_nfa


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


def move(states, symbol):
    result = set()

    for state in states:
        for next_state in state.transitions.get(symbol, []):
            result.add(next_state)

    return result


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
            if symbol != "ε":
                alphabet.add(symbol)

            for next_state in next_states:
                if next_state not in visited:
                    stack.append(next_state)

    return alphabet


def nfa_to_dfa(nfa):
    alphabet = get_alphabet(nfa.start)

    start_closure = frozenset(
        epsilon_closure({nfa.start})
    )

    dfa_states = {
        start_closure: 0
    }

    dfa_transitions = {}
    dfa_accept_states = set()

    queue = [start_closure]

    while queue:
        current = queue.pop(0)
        current_id = dfa_states[current]

        dfa_transitions[current_id] = {}

        if nfa.accept in current:
            dfa_accept_states.add(current_id)

        for symbol in alphabet:
            moved = move(current, symbol)

            if not moved:
                continue

            next_closure = frozenset(
                epsilon_closure(moved)
            )

            if next_closure not in dfa_states:
                dfa_states[next_closure] = len(dfa_states)
                queue.append(next_closure)

            dfa_transitions[current_id][symbol] = \
                dfa_states[next_closure]

    return {
        "start_state": 0,
        "accept_states": dfa_accept_states,
        "transitions": dfa_transitions,
        "state_sets": dfa_states,
        "alphabet": alphabet
    }


def print_dfa(dfa):
    print("\nDFA TRANSITIONS")

    for state, transitions in dfa["transitions"].items():
        for symbol, next_state in transitions.items():
            print(
                f"D{state} --{symbol}--> D{next_state}"
            )

    print("\nStart State: D0")

    accept = sorted(dfa["accept_states"])

    print(
        "Accept States:",
        ", ".join(f"D{x}" for x in accept)
    )


if __name__ == "__main__":
    regex = "(HF)+"

    print("Regex:", regex)

    nfa = regex_to_nfa(regex)

    dfa = nfa_to_dfa(nfa)

    print_dfa(dfa)