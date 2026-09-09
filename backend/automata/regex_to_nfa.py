class State:
    def __init__(self):
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


def symbol_nfa(symbol):
    start = State()
    accept = State()

    start.add_transition(symbol, accept)

    return NFA(start, accept)


def regex_to_nfa(regex):
    stack = []

    for char in regex:

        if char.isalnum():
            stack.append(symbol_nfa(char))

        elif char == "*":
            nfa = stack.pop()
            stack.append(kleene_star(nfa))

        elif char == "+":
            nfa = stack.pop()

            repeated = kleene_star(nfa)

            stack.append(concatenate(nfa, repeated))

        elif char == "|":
            nfa2 = stack.pop()
            nfa1 = stack.pop()

            stack.append(union(nfa1, nfa2))

    while len(stack) > 1:
        nfa2 = stack.pop()
        nfa1 = stack.pop()

        stack.append(concatenate(nfa1, nfa2))

    return stack.pop()
if __name__ == "__main__":

    regex = "HF"

    nfa = regex_to_nfa(regex)

    print("NFA created successfully")
    print("Start State:", id(nfa.start))
    print("Accept State:", id(nfa.accept))