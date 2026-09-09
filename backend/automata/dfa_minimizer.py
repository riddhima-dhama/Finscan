from automata.regex_to_nfa import regex_to_nfa
from automata.nfa_to_dfa import nfa_to_dfa


def minimize_dfa(dfa):
    states = set(dfa["transitions"].keys())
    accept_states = set(dfa["accept_states"])
    non_accept_states = states - accept_states
    alphabet = dfa["alphabet"]

    partitions = []

    if accept_states:
        partitions.append(accept_states)

    if non_accept_states:
        partitions.append(non_accept_states)

    changed = True

    while changed:
        changed = False
        new_partitions = []

        for group in partitions:
            transition_groups = {}

            for state in group:
                signature = []

                for symbol in sorted(alphabet):
                    next_state = dfa["transitions"].get(
                        state, {}
                    ).get(symbol)

                    target_group = None

                    if next_state is not None:
                        for index, partition in enumerate(partitions):
                            if next_state in partition:
                                target_group = index
                                break

                    signature.append(target_group)

                signature = tuple(signature)

                if signature not in transition_groups:
                    transition_groups[signature] = set()

                transition_groups[signature].add(state)

            new_partitions.extend(
                transition_groups.values()
            )

            if len(transition_groups) > 1:
                changed = True

        partitions = new_partitions

    state_mapping = {}

    for index, group in enumerate(partitions):
        for state in group:
            state_mapping[state] = index

    minimized_transitions = {}

    for index, group in enumerate(partitions):
        representative = next(iter(group))
        minimized_transitions[index] = {}

        for symbol, next_state in dfa["transitions"].get(
            representative, {}
        ).items():

            minimized_transitions[index][symbol] = \
                state_mapping[next_state]

    minimized_accept_states = set()

    for index, group in enumerate(partitions):
        if group & accept_states:
            minimized_accept_states.add(index)

    minimized_start = state_mapping[dfa["start_state"]]

    return {
        "start_state": minimized_start,
        "accept_states": minimized_accept_states,
        "transitions": minimized_transitions,
        "alphabet": alphabet,
        "partitions": partitions
    }


def print_minimized_dfa(dfa):
    print("\nMINIMIZED DFA TRANSITIONS")

    for state in sorted(dfa["transitions"]):
        for symbol, next_state in dfa["transitions"][state].items():
            print(f"M{state} --{symbol}--> M{next_state}")

    print(f"\nStart State: M{dfa['start_state']}")

    accept = sorted(dfa["accept_states"])
    print(
        "Accept States:",
        ", ".join(f"M{x}" for x in accept)
    )


if __name__ == "__main__":
    regex = "(HF)+"

    print("Regex:", regex)

    nfa = regex_to_nfa(regex)
    dfa = nfa_to_dfa(nfa)

    print("\nOriginal DFA States:",
          len(dfa["transitions"]))

    minimized_dfa = minimize_dfa(dfa)

    print(
        "Minimized DFA States:",
        len(minimized_dfa["transitions"])
    )

    print_minimized_dfa(minimized_dfa)