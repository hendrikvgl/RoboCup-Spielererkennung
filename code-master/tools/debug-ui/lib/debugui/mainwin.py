#-*- coding:utf-8 -*-
from debugui.stateview import StateView
from debugui.motorview import MotorView
from debugui.debugimageview import DebugImageView
from debugui.imageview import ImageView
from debugui.fieldimageview import FieldImageView
from debugui.dotview import DotView
import gtk
import gobject
import copy
from functions import make_ui_proxy
from bitbots.util import find_resource as find

import bitbots.glibevent
import traceback


class DataItem(object):
    __slots__ = ("name", "type", "value")

    def __init__(self, name, type, value):
        self.name = name
        self.type = type
        self.value = value


class DataStore(object):
    def __init__(self):
        self.latest = {}
        self.observers = {}

    def update(self, item):
        # letzten Wert merken
        self.latest[item.name] = item

        # alle Views dafür updaten
        for obs in copy.copy(self.observers.get(item.name, ())):
            try:
                obs(item)
            except:
                traceback.print_exc()

    def get(self, name):
        return self.latest[name]

    def add_observer(self, name, obs):
        self.observers.setdefault(name, set()).add(obs)

    def del_observer(self, name, obs):
        if name is not None:
            self.observers.get(name, set()).discard(obs)
        else:
            # Observer überall rauslöschen
            for observers in self.observers.itervalues():
                observers.discard(obs)


class DebugMainWindow(object):
    def __init__(self, server):
        self.setup_ui()

        self.views = []
        self.backlog = []
        self.store = DataStore()

        self.last_log_message = None
        self.last_log_message_count = None

        server.add_listener(self.on_debug_message)
        gobject.timeout_add(100, self.handle_backlog)

        self.warning_renderer = gtk.CellRendererText()
        self.warning_renderer.set_property('cell_background', 'red')

    def setup_ui(self):
        builder = gtk.Builder()
        builder.add_from_file(find("debug.ui"))
        builder.connect_signals(self)

        self.ui = make_ui_proxy(builder)

    def show(self):
        self.ui.window.show()

    def on_window_destroy(self, win):
        gtk.main_quit()

    def handle_log_messages(self, logs):
        row = None
        model = self.ui.logmodel

        # Merken, ob die letzte Zeile markiert ist
        path, _ = self.ui.logview.get_cursor()
        scroll_to_end = self.ui.autoscroll.get_active()
        for item in logs:
            """ Wird aufgerufen, wenn eine LogNachricht verarbeitet werden soll """
            # Zeile für die UI fertig machen
            if item.type == "warning":
                newrow = (
                    "<span foreground='red'>"
                    + item.name[:-8]
                    + "</span>", item.value)
            else:
                newrow = (item.name[:-4], item.value)

            if self.last_log_message == newrow:
                # Letzte Zeile einfach updaten
                self.last_log_message_count += 1
                model[-1][1] = "%s (%d mal)" % (
                    item.value, self.last_log_message_count)
                return

            self.last_log_message = newrow
            self.last_log_message_count = 1
            row = model.append(newrow)

        if scroll_to_end and row is not None:
            path = self.ui.logmodel.get_string_from_iter(row)
            self.ui.logview.set_cursor(path)

    def handle_backlog(self):
        done = set()
        todo = []
        logs = []
        for item in reversed(self.backlog):
            if item.type in ["log", "warning"]:
                logs.append(item)
                continue

            if item.name in done:
                continue

            done.add(item.name)
            todo.append(item)

        self.backlog = []

        self.handle_log_messages(reversed(logs))

        for item in reversed(todo):

            model = self.ui.treestore
            #hostname einklappbar?
            name = item.name.replace('::', '.')

            #find existing part of the path:
            names = name.rsplit('.')
            names.reverse()  # make popping easier

            #obtain the TreeStore root element
            treeit = model.get_iter_first()
            path_prefix = treeit
            treeit = path_prefix
            oldit = path_prefix
            name = names.pop()
            matched_something = False

            # Extend existing paths as long as possible
            while treeit is not None and len(names) > 0:
                # this entry can be extended
                if (model.get_value(treeit, 3) == name):
                    matched_something = True
                    name = names.pop()
                    oldit = treeit
                    treeit = model.iter_children(treeit)
                # try next iterator
                else:
                    treeit = model.iter_next(treeit)

            # generate rest part of path new
            if not matched_something:
                oldit = None
            while len(names) > 0:
                newit = model.iter_children(oldit)
                #Find first lexical higher sibling
                while newit is not None:
                    if model.get_value(newit, 3) > name:
                        break
                    newit = model.iter_next(newit)
                #insert before the first lexical higher sibling
                #no problem if newit is none it will be appended to oldit instead
                oldit = model.insert_before(
                    oldit, newit, (item.name, '', '', name))
                name = names.pop()

            # last node reached
            generate_last = True
            if len(names) == 0:
                # See if exact match is possible
                while treeit is not None:
                    if model.get_value(treeit, 3) == name:
                        model.set(treeit, 0, item.name,
                                  1, item.type, 2, format(item), 3, name)
                        generate_last = False
                        break
                    #lexically higher value means break too
                    if model.get_value(treeit, 3) > name:
                        break
                    treeit = model.iter_next(treeit)
                # No last match possible, make new
                if generate_last:
                    #If treeit is None it will be appended to oldit
                    oldit = model.insert_before(oldit, treeit, (
                        item.name, item.type, format(item), name))

            self.store.update(item)
            assert(len(names) == 0)
        return True

    def on_debug_message(self, type, name, value):
        """ Verarbeitet Debug-Nachrichten """
        if type == "shape":
            return

        if isinstance(value, str):
            # strings escapen, da sie ausversehen zeichen der markup
            # sprache enthalten können
            value = gobject.markup_escape_text(value)
        # Item erzeugen
        item = DataItem(name, type, value)
        self.backlog.append(item)

    def on_filter_changed(self, widget):
        """ Wird von der UI aufgerufen, wenn der Text im Filter verändert
            wird. Setzt ein neues Filter-Modell in dem TreeView
        """
        text = widget.get_text().strip()
        if not text:
            # keine Filterung
            self.ui.logview.set_model(self.ui.logmodel)
            return

        # Filter aktivieren
        model = self.ui.logmodel.filter_new()
        func = lambda model, it: (
            model.get_value(it, 0) or "").find(text) != -1
        model.set_visible_func(func)
        self.ui.logview.set_model(model)


    def on_treeview_clicked(self, treeview, event):
        if event.button != 3:
            return

        # Gucken worauf wir geklickt haben
        x, y = int(event.x), int(event.y)
        path = treeview.get_path_at_pos(x, y)
        if path is None:
            return

        # Zeile holen, die wir angeklickt haben
        model = treeview.get_model()
        name, dtype = model.get(model.get_iter(path[0]), 0, 1)

        menu = gtk.Menu()

        me_expand = gtk.MenuItem("Expand All")
        me_expand.connect(
            "activate", lambda mi: treeview.expand_row(path[0], True))
        menu.append(me_expand)
        me_collapse = gtk.MenuItem("Collapse All")
        me_collapse.connect(
            "activate", lambda mi: treeview.collapse_row(path[0]))
        menu.append(me_collapse)
        me_clear = gtk.MenuItem("Clear All")
        me_clear.connect(
            "activate", lambda mi: model.clear())
        menu.append(me_clear)
        me_overview = gtk.MenuItem("Technical Overview")
        me_overview.connect(
            "activate", lambda mi: self.make_view(name, MotorView))
        menu.append(me_overview)


        if dtype == "matrix":
            me_show = gtk.MenuItem("Show Image")
            me_show.connect(
                "activate", lambda mi: self.make_view(name, ImageView))
            menu.append(me_show)

        if dtype == "shapes" and "Positions" in name:
            me_show = gtk.MenuItem("Show Field")
            me_show.connect(
                "activate", lambda mi: self.make_view(name, FieldImageView))
            menu.append(me_show)

        elif dtype == "string" and "Dot" in name:
            me_show = gtk.MenuItem("Graph anzeigen")
            me_show.connect(
                "activate", lambda mi: self.make_view(name, DotView))
            menu.append(me_show)

        elif dtype == "string" and "Zustand" in name:
            # TODO: enums oder irgendwas statisches benutzen um auf fieldie oder goalie zu prüfen
            states = None
            for n in ("Fieldie", "Goalie", "ThrowIn"):
                if n.lower() in name.lower():
                    states = getattr(bitbots.modules.fsm.states, n + "States")
                    break
            else:
                return

            me_show = gtk.MenuItem("Zustandsgraph anzeigen")
            me_show.connect("activate", lambda mi:
                            self.make_view(name, StateView, states=states))
            menu.append(me_show)

        # Menu öffnen
        treeview.grab_focus()
        treeview.set_cursor(path[0])

        menu.show_all()
        menu.popup(None, None, None, event.button, event.time)

    def make_view(self, name, clazz, **kwargs):
        cleanup_ops = []

        def destroy():
            view.cleanup()
            self.views.remove(view)
            self.store.del_observer(None, view.update)
            for op in cleanup_ops:
                op()

        def add_observer(name, func):
            self.store.add_observer(name, func)
            cleanup_ops.append(lambda: self.store.del_observer(name, func))

        # View erzeugen
        view = clazz(destroy, **kwargs)
        view.update(self.store.get(name))
        view.register_observers(name, add_observer)
        self.store.add_observer(name, view.update)
        self.views.append(view)


def format(item):
    if item.type == "matrix":
        shape = item.value.shape[:2]
        return "Matrix mit %d Zeilen und %d Spalten" % tuple(shape)

    if item.type == "number":
        return "%1.4f" % float(item.value)

    if item.name.endswith(".Dot"):
        return "Dot File Information"

    return str(item.value)[:100]
