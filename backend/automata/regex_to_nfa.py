class State:
    counter = 0

    def __init__(self):
        self.id = State.counter
        State.counter += 1
        self.transitions = {}
        self.is_final = False

    def add_transition(self, symbol, state):
        if symbol not in self.transitions:
            self.transitions[symbol] = []

        self.transitions[symbol].append(state)


class NFA:
    def __init__(self, start, accept):
        self.start = start
        self.accept = accept
        self.accept.is_final = True


def symbol_nfa(symbol):
    start = State()
    accept = State()

    start.add_transition(symbol, accept)

    return NFA(start, accept)


def concatenate(nfa1, nfa2):
    nfa1.accept.is_final = False
    nfa1.accept.add_transition("ε", nfa2.start)

    return NFA(nfa1.start, nfa2.accept)


def union(nfa1, nfa2):
    start = State()
    accept = State()

    start.add_transition("ε", nfa1.start)
    start.add_transition("ε", nfa2.start)

    nfa1.accept.is_final = False
    nfa2.accept.is_final = False

    nfa1.accept.add_transition("ε", accept)
    nfa2.accept.add_transition("ε", accept)

    return NFA(start, accept)


def kleene_star(nfa):
    start = State()
    accept = State()

    start.add_transition("ε", nfa.start)
    start.add_transition("ε", accept)

    nfa.accept.is_final = False

    nfa.accept.add_transition("ε", nfa.start)
    nfa.accept.add_transition("ε", accept)

    return NFA(start, accept)


def add_concatenation(regex):
    result = []

    for i in range(len(regex)):
        current = regex[i]
        result.append(current)

        if i + 1 < len(regex):
            next_char = regex[i + 1]

            if (
                (current.isalnum() or current in ")*+")
                and (next_char.isalnum() or next_char == "(")
            ):
                result.append(".")

    return "".join(result)


def precedence(operator):
    priorities = {
        "|": 1,
        ".": 2,
        "*": 3,
        "+": 3
    }

    return priorities.get(operator, 0)


def infix_to_postfix(regex):
    output = []
    stack = []

    for char in regex:

        if char.isalnum():
            output.append(char)

        elif char == "(":
            stack.append(char)

        elif char == ")":
            while stack and stack[-1] != "(":
                output.append(stack.pop())

            if stack:
                stack.pop()

        else:
            while (
                stack
                and stack[-1] != "("
                and precedence(stack[-1]) >= precedence(char)
            ):
                output.append(stack.pop())

            stack.append(char)

    while stack:
        output.append(stack.pop())

    return "".join(output)


def clone_nfa(nfa):
    state_map = {}

    def clone_state(state):
        if state in state_map:
            return state_map[state]

        new_state = State()
        state_map[state] = new_state

        for symbol, states in state.transitions.items():
            for next_state in states:
                new_state.add_transition(
                    symbol,
                    clone_state(next_state)
                )

        return new_state

    new_start = clone_state(nfa.start)
    new_accept = state_map[nfa.accept]

    return NFA(new_start, new_accept)


def one_or_more(nfa):
    first = clone_nfa(nfa)
    repeated = kleene_star(clone_nfa(nfa))

    return concatenate(first, repeated)


def regex_to_nfa(regex):
    regex = add_concatenation(regex)
    postfix = infix_to_postfix(regex)

    stack = []

    for char in postfix:

        if char.isalnum():
            stack.append(symbol_nfa(char))

        elif char == ".":
            nfa2 = stack.pop()
            nfa1 = stack.pop()

            stack.append(concatenate(nfa1, nfa2))

        elif char == "|":
            nfa2 = stack.pop()
            nfa1 = stack.pop()

            stack.append(union(nfa1, nfa2))

        elif char == "*":
            nfa = stack.pop()

            stack.append(kleene_star(nfa))

        elif char == "+":
            nfa = stack.pop()

            stack.append(one_or_more(nfa))

    return stack.pop()


def print_nfa(nfa):
    visited = set()
    queue = [nfa.start]

    print("\nNFA TRANSITIONS")

    while queue:
        state = queue.pop(0)

        if state in visited:
            continue

        visited.add(state)

        for symbol, states in state.transitions.items():
            for next_state in states:
                print(
                    f"q{state.id} --{symbol}--> q{next_state.id}"
                )

                if next_state not in visited:
                    queue.append(next_state)

    print(f"\nStart State: q{nfa.start.id}")
    print(f"Accept State: q{nfa.accept.id}")


if __name__ == "__main__":

    regex = "(HF)+"

    print("Original Regex:", regex)

    explicit_regex = add_concatenation(regex)
    print("With Concatenation:", explicit_regex)

    postfix = infix_to_postfix(explicit_regex)
    print("Postfix Regex:", postfix)

    nfa = regex_to_nfa(regex)

    print_nfa(nfa)