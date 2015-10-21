#from bitbots.modules.fsm.states import BasicStates


class StateGraphCreator(object):
    def __init__(self, state_type):
        self.states = state_type
        self.build_order = state_type.get_build_order()

    def create_graph(self, current, last_state):
        """
            Creates a String in the dot-language describing the Graph to display.
        """

        current_printed = False
        cluster = 0
        cluster_depth = 0
        graph = [
            "rankdir=LR",
            "ratio = compress"
        ]

        print "build_ordrer:", self.build_order
        for state in self.build_order:
            if "{" in state:
                cluster_depth += 1
                cluster += 1
                graph.append("subgraph cluster%d {" % cluster)
            elif "}" in state:
                cluster_depth -= 1
                graph.append("}")
            else:
                fc = "grey"
                if state == current:
                    current_printed = True
                    fc = "red"
                graph.append("%s%s [style=filled , fillcolor=%s]" % ("\t" * cluster_depth, state, fc))

        for from_state in self.states:
            for to_state in self.states.transitions.get(from_state, ()):
                attributes = []

                #if BasicStates.contains(to_state):
                #    continue
                #    attributes.append('constraint=false')

                if current == from_state:
                    attributes.append('color=green')
                elif current == last_state:
                    attributes.append('color=red')
                #elif BasicStates.contains(to_state):
                #    attributes.append('color=grey')

                attributes = ("[%s]" % ', '.join(attributes)) if attributes else ''
                graph.append("%s -> %s %s" % (from_state, to_state, attributes))

        if not current_printed:
            graph.append("%s [style=filled , fillcolor=red]" % ("\"Hidden State: %s\"" % str(current)))

        return "digraph G {\n\t%s\n}" % "\n\t".join(graph)
