#-*- coding:utf-8 -*-
"""
This Module provides some generic Views

.. autoclass:: GenericView
    :members:

.. autoclass:: GenericNotebookView
    :members:
"""

import gtk

from bitbots.util import find, generate_find

try:
    find('share/debug-ui-neu')
    find = generate_find('share/debug-ui-neu')
except:
    find = generate_find('tools/debug-ui-neu/share/debug-ui-neu')


class GenericView(gtk.Alignment):
    """
    This Class can be used as normal gtk Widget, and take care of the external
    window for each view. It also show the Caption for the view and some buttons
    """
    def __init__(self, name, data_callback, view_calback):
        """
        Initialises the external window and internal widgets

        :param name: The name of the View
        :type name: String
        """
        super(GenericView, self).__init__()

        self.view_name = name
        self.view_calback = view_calback
        self.data_callback = data_callback
        self.extern_window_shown = False

        # skalierung des
        self.set_property("xalign", 0)
        self.set_property("yalign", 0)
        self.set_property("xscale", 1)
        self.set_property("yscale", 1)

        #View elemente bauen
        self.builder = gtk.Builder()
        self.builder.add_objects_from_file(
            find("GenericView.glade"), ("View",))
        self.builder.get_object(
            'Name').set_markup("<b>%s</b>" % self.view_name)
        super(GenericView, self).add(self.builder.get_object("View"))
        # und anzeigen (nur sicherheitshalber)
        self.show_all()

        # externes Fenster erstellen, aber nicht anzeigen
        self.ext_builder = gtk.Builder()
        self.ext_builder.add_from_file(
            find("GenericViewExtern.glade"))
        self.ext_builder.get_object(
            "Name").set_markup("<b>%s</b>" % self.view_name)
        self.external_window = self.ext_builder.get_object("GenericExternView")

        # signals connecten
        self.builder.connect_signals(self)
        self.ext_builder.connect_signals(self)

    def add(self, widget_intern, widget_extern):
        """
        Adds a widget to the view. Because of the external window you have to
        provide 2 views

        :param widget_intern: The widget to use in the debugmainscreen
        :param widget_extern: The widget to use in the external window
        """
        self.builder.get_object("Inhalt").add(widget_intern)
        self.ext_builder.get_object("Inhalt").add(widget_extern)

    def show_all(self):
        """
        This Method shows th internal widgets, and if on screen the external
        """
        # für die View durchreichen
        super(GenericView, self).show_all()
        # wenn das externe Fenster dargestellt wird, muss es auch aktuallisiert
        # werden
        if self.extern_window_shown:
            self.external_window.show_all()

    def show_external_window(self):
        """
        Bring the external window on the Screen
        """
        self.external_window.show_all()
        self.extern_window_shown = True

    def hide_external_window(self):
        """
        Hides the external window
        """
        self.external_window.hide()
        self.extern_window_shown = False
        return True  # gtk mitteilen das das Signal bearbeitet wurde

    def on_button_new_window_clicked(self, *kwargs):
        """
        Buttonhandler
        """
        self.show_external_window()

    def on_external_window_delete(self, *kwargs):
        """
        Handler for Button
        """
        return self.hide_external_window()

    def on_button_duplicate_clicked(self, *kwargs):
        print "Duplicate cliced"
        view = self.__class__(self.data_callback, self.view_calback)
        view.set_internal_state(self.get_internal_state())
        self.view_calback("add", view)

    def add_new_robot(self, robot):
        """
        Dummy um es einfach an allen Views aufruffen zu können, ob da was
        passiert darf jeder selbst entscheiden
        """
        pass

    def get_internal_state(self):
        """
        Diese Funktion kann einen internen status zurückgeben der dazu dient
        das Widget zu dublizieren und an :func:`set_internal_state` übergeben
        wird.
        """
        return {}

    def set_internal_state(self, state):
        """
        Stellt den Internen status wieder her, bekommt die daten des zu
        duplizierenden Views von :func:`get_internal_state`
        """
        pass


class GenericNotebookView(GenericView):
    """
    This is the :class:`GenericView` extended by a notebook so that each robot
    can have his own tab
    """
    def __init__(self, name, data_callback, view_calback):
        super(GenericNotebookView, self).__init__(name,
                                                  data_callback, view_calback)

        # anlegen der beiden Notebooks (intern/extern)
        self.notebook = gtk.Notebook()
        self.ext_notebook = gtk.Notebook()

        # notebook den Views hinzufügen
        self.add(self.notebook, self.ext_notebook)

        # anzeigen
        self.show_all()

    def add_notebook_page(self, name, view_intern, view_extern):
        """
        Adds a New Page to the notebook
        """
        print name
        print "intern"
        self._insert_page(name, view_intern, self.notebook)
        print "extern"
        self._insert_page(name, view_extern, self.ext_notebook)

    def _insert_page(self, name, view, notebook):
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        #scroll.add(view)
        # FIXME: wenn ich hier nen ScrolledWindow zwischenschiebe: im 2. tab gibts nen segfault...
        l = gtk.Label(name)
        #gtk.gdk.beep()
        notebook.insert_page(view, l, -1)
        #gtk.hande
        notebook.show_all()


class DummyView(GenericView):
    def __init__(self, data_calback, view_calback):
        super(
            DummyView, self).__init__("DummyView", data_calback, view_calback)
