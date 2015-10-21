from bitbots.debug.stategraph import StateGraphCreator
import xdot
from bitbots.modules.fsm import states


class StateView(object):
    def __init__(self, destroy, states):
        self.destroy = destroy
        self.graph = StateGraphCreator(states)
        self.last_state = None
        self.setup_ui()

    def setup_ui(self):
        self.sg_window = xdot.DotWindow()
        self.sg_window.connect("delete-event", lambda *a: self.destroy())
        self.sg_window.show()

    def register_observers(self, name, register):
        pass

    def update(self, item):
        """ Update Graph if anything is to update
        """
        if item is None:
            return

        current = item.value
        if self.last_state is None or self.last_state != current:
            self.sg_window.set_dotcode(
                self.graph.create_graph(current, self.last_state))
            self.last_state = current

    def cleanup(self):
        self.sg_window.destroy()
