import xdot


class DotView(object):
    def __init__(self, destroy):
        self.new_dotcode = True
        self.destroy = destroy
        self.setup_ui()

    def setup_ui(self):
        self.sg_window = xdot.DotWindow()
        self.sg_window.connect("delete-event", lambda *a: self.destroy())
        self.sg_window.connect("key-press-event", self.on_key_event)
        self.sg_window.show()

    def register_observers(self, name, register):
        pass

    def update(self, item):
        """ Update Graph
        """
        if item is None:
            return
        if self.new_dotcode:
            self.sg_window.set_dotcode(item.value)
            self.new_dotcode = False

    def on_key_event(self, widget, event):
        if event.keyval == 32:
            self.new_dotcode = True

    def cleanup(self):
        self.sg_window.destroy()
