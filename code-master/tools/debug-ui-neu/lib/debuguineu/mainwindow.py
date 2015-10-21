#-*- coding:utf-8 -*-
#include <gtk/gtk.h>
"""
mainwindow
^^^^^^^^^^

Implementation of the UI's Mainwindow, which, according to the
"One-Window-Approach", Constitutes the bulk of the UI, from which most
other views and functions are activated.

:platform: Unix and Windows

.. moduleauthor:: Robocup-AG in cooperation with Projekt-Debug-UI

.. autoclass:: DataItem(Object)
    :members:
.. autoclass:: DataStore(Object)
    :members:
.. autoclass:: DebugUiMainWin(Object)
    :members:

.. automodule:: debuguineu.genericView
.. automodule:: debuguineu.VisionView
.. automodule:: debuguineu.MotorView
"""

import gtk
import gtk.glade

import sys

from os.path import normpath
import time

from MotorView import MotorView
from VisionView import VisionView, FieldView
from debuguineu.HalfFieldView import HalfFieldView
from debuguineu.WorldView import WorldView
from dotview import DotView
from motorTemp import MotorTempGraph
from bitbots.util import get_config

#Verzeichnisse für leute ohne virtualenv
sys.path.append(normpath(sys.path[0] + "/lib"))
sys.path.append(normpath(sys.path[0] + "/tools/debug-ui/bin"))
sys.path.append(normpath(sys.path[0] + "/tools/debug-ui/lib"))


#from debugui.imageview import ImageView

import bitbots.glibevent

import gobject
import copy

#from functions import make_ui_proxy
import traceback

from debuguineu.functions import find
from debuguineu.plaindump import DebugPlainDumper

config = get_config()["debugui"]

class DataItem(object):
    """
    A Dataitem represents a piece of information send by a robot
    """
    __slots__ = ("name", "type", "value")

    def __init__(self, name, type, value):
        self.name = name
        self.type = type
        self.value = value


class DataStore(object):
    """
    The DataStore holds ol DataItems recived, and handel calbacks on chhanges of
    data keys.
    """
    def __init__(self):
        self.latest = {}
        self.observers = {}

    def update(self, item):
        """
        Updates a DataItem in the Store and do the connected callbacks

        :param item: the Item to Update/Store
        :type item: :class:`DataItem`
        """
        # letzten Wert merken
        self.latest[item.name] = item

        # alle Views dafuer updaten
        for obs in copy.copy(self.observers.get(item.name, ())):
            try:
                obs(item)
            except:
                traceback.print_exc()

    def get(self, name):
        """
        Gets the latest item with itm.name = name

        :param name: the name of the item
        :type name: String
        """
        return self.latest[name]

    def add_observer(self, name, obs):
        """
        Adds a observer on a name

        :param name: The name of the Item on witch the observer ist called
        :type name: String
        :param obs: the Function to be called
        :type obs: function(item)

        The observer Function gets the Item as parameter
        """
        print "Register: %s %s" % (str(name), str(obs))
        self.observers.setdefault(name, set()).add(obs)

    def del_observer(self, name, obs):
        """
        Delete a observer from a name, or from all names if name = None

        :param name: The Name to unregister the observer from
        :type name: String or None
        :param obs: The observer to unregister
        :tyoe obs: function
        """
        if name is not None:
            self.observers.get(name, set()).discard(obs)
        else:
            # Observer ueberall rauslöschen
            for observers in self.observers.itervalues():
                observers.discard(obs)


class DebugUiMainWin(object):
    """
    The Main Class of the UI, which contains most functionalities
    of the UI itself, as well as some of the more basic views.
    """

    def __init__(self, server):
        """
        Initializes the mainwindow and, by doing that, the UI itself.
        Sets up the views and provides them with the Datastream from
        the robots.

        :param server: The Server, from which the data is
        put into the UI

        :type server: A Datastream (Not entirely sure about that.
        More Information is required!)
        """

        self.store = DataStore()
        self.views = []

        # wir fügen erstmal statisch 3 Views hinzu
        # TODO: dynamisch & config
        self.views.append(
            MotorView(self.store.add_observer, self.view_calback))
        if config["NeedVisionView"]:
            self.views.append(
                VisionView(self.store.add_observer, self.view_calback))
        else:
            self.views.append(
                WorldView(self.store.add_observer, self.view_calback))
        self.views.append(
            HalfFieldView(self.store.add_observer, self.view_calback))
        print self.views
        self.setup_ui()

        self.robots = []
        self.treestores = {}

        self.backlog = []

        self.last_log_message = None
        self.last_log_message_count = None

        server.add_listener(self.on_debug_message)
        gobject.timeout_add(100, self.handle_backlog)


        self.last_image = None
        self.last_shapes = None
        self.last_width = self.last_height = None

    def setup_ui(self):
        """
        Sets up the UI. Loads all files necessary to set up
        the individual Views

        For Testing purposes Only: Pops up the warning window, when the
        UI is started.
        """
        self.builderMainWin = gtk.Builder()
        self.builderConfWin = gtk.Builder()

        self.builderMainWin.add_from_file(
            find("Projekt_DebugUI_MainWindow.glade"))
        self.builderConfWin.add_from_file(
            find("Projekt_DebugUI_Confirmation.glade"))

        #die externe Nachrichtensicht
        self.builderNewsExt = gtk.Builder()
        self.builderNewsExt.add_from_file(
            find("Projekt_DebugUI_NewsExt.glade"))
        #die externe Roboauswahlsicht
        self.builderRoboSel = gtk.Builder()
        self.builderRoboSel.add_from_file(
            find("Projekt_DebugUI_RoboSelect.glade"))

        #das Aboutfenster
        self.builderAboutView = gtk.Builder()
        self.builderAboutView.add_from_file(
            find("Projekt_DebugUI_Aboutfenster2.glade"))
        self.aboutD = self.builderAboutView.get_object("Aboutfenster")

        ##die externe Kamerasicht
        #self.builderCameraView = gtk.Builder()
        #self.builderCameraView.add_from_file(find("debug-ui-neu/Projekt_DebugUI_CameraView.glade"))
        self.mainwindow = self.builderMainWin.get_object("mainWindowDebugUI")
        self.confWin = self.builderConfWin.get_object("messagedialogQuitConf")

        # Views anzeigen
        # TODO: das will vielleicht dynamischer werden
        self.builderMainWin.get_object("Content1").add(self.views[0])
        self.builderMainWin.get_object("Content3").add(self.views[1])
        self.builderMainWin.get_object("Content2").add(self.views[2])
        self.viewslots_oben = []
        self.viewslots_unten = []
        self.viewslots_oben.append(self.builderMainWin.get_object("Content1"))
        self.viewslots_oben.append(self.builderMainWin.get_object("Content2"))
        self.viewslots_unten.append(self.builderMainWin.get_object("Content3"))
        self.mainwindow.show_all()

        #self.imageViewFrame = self.builderMainWin.get_object("frameImageview")
        #self.imageFrame1 = self.builderMainWin.get_object("frame1")

        #fenster für values anlegen, aber nicht zeigen
        self.RoboSel = self.builderRoboSel.get_object("RoboSelectExtern")
        self.builderRoboSel.connect_signals(self)

        # fenster für externe LogView
        self.NewsExt = self.builderNewsExt.get_object("NewsExtern")
        self.builderNewsExt.connect_signals(self)
        #self.make_view(name, imageViewFrame)
        #self.me_show.show()
        #self.store = DataStore()

        self.debug_plain_dumper = DebugPlainDumper()

        #  Automatische Verbindung der in Glade festgelegten Signals mit ihren Handlern.
        self.builderMainWin.connect_signals(self)
        self.builderConfWin.connect_signals(self)
        self.builderAboutView.connect_signals(self)

# --------------- Eventhandler Implementationen -------------------------------
    def show(self):
        self.mainwindow.show()

    def gtk_main_quit(self, *args):
        gtk.main_quit()
        print ("Die komplette Anwendung wurde geschlossen")

    def view_calback(self, art, view):
        if art == "add":
            print "Add new Window"
            self.views.append(view)
            self.show_views()
        else:
            print "UNSUPORTED view-calback type: %s" % art

    def show_views(self):
        content_count = len(self.viewslots_oben) + len(self.viewslots_unten)
        print "Contentcount, views ", content_count, len(self.views)
        if len(self.views) > content_count:
            content_object = self.viewslots_oben.pop()
            child = content_object.get_child()
            hpaned = gtk.HPaned()
            contend_holder1 = gtk.Alignment()
            hpaned.add1(contend_holder1)
            contend_holder2 = gtk.Alignment()
            hpaned.add2(contend_holder2)
            child.reparent(contend_holder1)
            #TODO: absicherung, das das neue nicht am ende steht
            contend_holder2.add(self.views[-1])
            content_object.add(hpaned)
            content_object.show_all()

            self.viewslots_oben.append(contend_holder1)
            self.viewslots_oben.append(contend_holder2)

    def handle_log_messages(self, logs):
        """
        Displays the log messages from the robots in the log view

        :param logs: The Messages to be displayed
        :type logs: A list of log messages
        """
        model = self.builderMainWin.get_object("logmodel")
        model2 = self.builderMainWin.get_object(
            "logmodel2")  # fürs warnnachrichtenfenster

        #dazugekommen für externes NachrichtenFenster
       # print ("hole die logmodels des externen Nachrichtenfensters")
        model3 = self.builderNewsExt.get_object("logmodel")
        model4 = self.builderNewsExt.get_object(
            "logmodel2")  # fürs externe warnnachrichtenfenster

        #Kommi von Robocuppern: Merken, ob die letzte Zeile markiert ist
       #von uns dazugekommen:-------------------
        logview = self.builderMainWin.get_object("logview")

       # print("hole den logview des externen Nachrichtenfensters")
        logview3 = self.builderNewsExt.get_object("logview")
        path, _ = logview.get_cursor()

        externpath, _ = logview3.get_cursor()

        #scrollWin = self.builderMainWin.get_object("nachrichtenScrolledwindow")
       # nachrVerlaufscroll = self.builderMainWin.get_object("checkmenuitemNachrichten")
       # warnVerlaufscroll = self.builderMainWin.get_object("checkmenuitemNachrichten2")
       #fragt ab ob die Menüpunkte "Nachrichten mitscrollen" und "Warnungen mitscrollen" aktiviert sind
        #scroll_to_end = nachrVerlaufscroll.get_active()
        #scroll_to_end2 = warnVerlaufscroll.get_active()
        #scroll_to_end = scrollWin.autoscroll.get_active() funzt leider auch net.
        #Nils fragen.
        for item in logs:
            #Wird aufgerufen, wenn eine LogNachricht verarbeitet werden soll
            # Zeile fuer die UI fertig machen
            if item.type == "warning":
                newrow = ("<span foreground='red'>" + item.name[:-8] + "</span>", item.value)
            else:
                newrow = (item.name[:-4], item.value)

            if self.last_log_message == newrow:
                # Letzte Zeile einfach updaten
                self.last_log_message_count += 1
                model[-1][1] = "%s (%d mal)" % (
                    item.value, self.last_log_message_count)
                #dazugekommen fürs externe nachrichtenfenster
                model3[-1][1] = "%s (%d mal)" % (
                    item.value, self.last_log_message_count)
                if item.type == "warning":
                    model2[-1][1] = "%s (%d mal)" % (
                        item.value, self.last_log_message_count)
                    model4[-1][1] = "%s (%d mal)" % (
                        item.value, self.last_log_message_count)
                continue

            self.last_log_message = newrow
            self.last_log_message_count = 1
            model.append(newrow)
            model3.append(newrow)
            #dazugekommen
            if item.type == "warning":
                model2.append(newrow)
                model4.append(newrow)

#muss spaeter einkommentiert werden wenn autoscroll s.o. funzt.
     #   if scroll_to_end and row is not None:
     #       path = model.get_string_from_iter(row)
      #      logview.set_cursor(path)
            #path = self.mainwindow.logmodel.get_string_from_iter(row)
            #self.mainwindow.logview.set_cursor(path)
#erstellt die Roboansicht mit der benötigten Anzahl an Tabs, mit dem Robonamen darin und den zugehörigen Treeviews
    def make_new_value_tab(self, store, notebook, robot):
        """

        Creates the tabbed robotview with the right number of tabs and
        the respective names of the robots as the title of the tab.


        :param store:
        :type store:
        :param notebook:
        :type notebook:
        :param robot:
        :type robot:

        """
        view = gtk.TreeView(store)
        lable = gtk.Label(robot)

        colm1 = gtk.TreeViewColumn('Name', gtk.CellRendererText(), text=3)
        colm1.set_resizable(True)
        colm1.set_sizing(True)
        view.insert_column(colm1, -1)
        colm2 = gtk.TreeViewColumn('Type', gtk.CellRendererText(), text=1)
        colm2.set_resizable(True)
        colm2.set_sizing(True)
        view.insert_column(colm2, -1)
        colm3 = gtk.TreeViewColumn('Object', gtk.CellRendererText(), text=2)
        colm3.set_resizable(True)
        colm3.set_sizing(True)
        view.insert_column(colm3, -1)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(view)

        notebook.insert_page(scroll, lable, -1)

        #macht den treeview wieder anklickbar
        view.connect("button-release-event", self.on_treeview_clicked)

    def handle_backlog(self):
        """
        Handles the backlog (Needs to be expanded upon).
        """
      #  print("handle_backlog wurde aufgerufen") #merke: wird immer nach handle_log_messages aufgerufen
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

        # items fürs werdeview
        for item in reversed(todo):

            # wir trennen den namen des roboters ab
            robot, name = item.name.split('::')
            #hostname einklappbar?
            #name = item.name.replace('::','.')

            #different robots go to different views
            if robot not in self.robots:
                # wenn wir den Roboter noch nicht hatten legen wir ihn an
                self.robots.append(robot)

                notebook = self.builderMainWin.get_object("roboNotebook")
                notebook_extern_window = self.builderRoboSel.get_object(
                    "roboNotebook")
                store = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)

                self.treestores[robot] = store

                self.make_new_value_tab(store, notebook, robot)
                self.make_new_value_tab(store, notebook_extern_window, robot)

                #fenster neu zeichnen sonst ists nicht sichtbar!!!
                self.mainwindow.show_all()
                # das sorgt fürs sofortige auftauchen daher noch auskommentiert
                #self.builderRoboSel.get_object("RoboSelectExtern").show_all()

                #TODO: bessere Stelle dafür finden
                # allen Views vom neuen Roboter erzählen
                print "Bla: ", self.views
                for view in self.views:
                    view.add_new_robot(robot)
                    print "called new_robot on ", view

            model = self.treestores[robot]

            #find existing part of the path:
            names = name.rsplit('.')
            names.reverse()  # make popping easier

            #obtain the TreeStore root element
            treeit = model.get_iter_first()

            path_prefix = treeit

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
                    #oldit2 = treeit2  #-.-
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

        self.debug_plain_dumper.dump(type, name, value)

        if type == "shape":
            return

        # Item erzeugen
        item = DataItem(name, type, value)
        self.backlog.append(item)

    #Methode angepasst. Bewirkt das der Nachrichtenfilter funktioniert
    def on_filter_changed(self, widget):
        """ Wird von der UI aufgerufen, wenn der Text im Nachrichtenfilter veraendert
            wird. Setzt ein neues Filter-Modell in dem TreeView
        """
        logmodel = self.builderMainWin.get_object("logmodel")
        logview = self.builderMainWin.get_object("logview")
        #logmodel und logview des externen Nachrichtenfensters
        logmodel2 = self.builderNewsExt.get_object("logmodel")
        logview2 = self.builderNewsExt.get_object("logview")

        text = widget.get_text().strip()
        if not text:
            # keine Filterung
            logview.set_model(logmodel)
            logview2.set_model(logmodel2)
            return

        # Filter aktivieren
        model = logmodel.filter_new()
        model2 = logmodel2.filter_new()
        func = lambda model, it: (
            model.get_value(it, 0) or "").find(text) != -1
        func2 = lambda model2, it: (
            model2.get_value(it, 0) or "").find(text) != -1
        model.set_visible_func(func)
        model2.set_visible_func(func2)
        logview.set_model(model)
        logview2.set_model(model2)

    #dazugekommene Methode, damit der Warnungsfilter auch funktioniert.
    def on_filter_changed2(self, widget):
        """ Wird von der UI aufgerufen, wenn der Text im Warnungsfilter veraendert
            wird. Setzt ein neues Filter-Modell in dem TreeView
        """
        logmodel3 = self.builderMainWin.get_object("logmodel2")
        logview3 = self.builderMainWin.get_object("logview2")
        #logmodel und logview des externen Warnungsfensters
        logmodel4 = self.builderNewsExt.get_object("logmodel2")
        logview4 = self.builderNewsExt.get_object("logview2")

        text = widget.get_text().strip()
        if not text:
            # keine Filterung
            logview3.set_model(logmodel3)
            logview4.set_model(logmodel4)
            return

        # Filter aktivieren
        model3 = logmodel3.filter_new()
        model4 = logmodel4.filter_new()
        func = lambda model3, it: (
            model3.get_value(it, 0) or "").find(text) != -1
        func2 = lambda model4, it: (
            model4.get_value(it, 0) or "").find(text) != -1
        model3.set_visible_func(func)
        model4.set_visible_func(func2)
        logview3.set_model(model3)
        logview4.set_model(model4)

    def on_treeview_clicked(self, treeview, event):
        print("on_treeview_clicked wurde aufgerufen!")

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
        print name, dtype
        menu = gtk.Menu()

        me_expand = gtk.MenuItem("Expand All")
        me_expand.connect(
            "activate", lambda mi: treeview.expand_row(path[0], True))
        menu.append(me_expand)
        me_collapse = gtk.MenuItem("Collapse All")
        me_collapse.connect(
            "activate", lambda mi: treeview.collapse_row(path[0]))
        menu.append(me_collapse)

        if dtype == "matrix":
            global ImageViewUnser
            self.ImageView = self.builderMainWin.get_object("frameImageview")
            me_show = gtk.MenuItem("Show Image")

            me_show.connect(
                "activate", lambda mi: self.make_view(name, self.ImageView))
            menu.append(me_show)

        elif dtype == "string" and "Dot" in name:
            me_show = gtk.MenuItem("Graph anzeigen")
            me_show.connect(
                "activate", lambda mi: self.make_view(name, DotView))
            menu.append(me_show)

        elif dtype == "number":
            plot = gtk.MenuItem("Plot")
            plot.connect("activate", lambda mi: self.plot_numbers(name))
            menu.append(plot)

        # Menu oeffnen
        treeview.grab_focus()
        treeview.set_cursor(path[0])

        menu.show_all()
        menu.popup(None, None, None, event.button, event.time)

    def plot_numbers(self, name):
        """Plotet den key mit matpotlib"""
        data = [[], []]
        self.store.add_observer(name, lambda item: self.update_plot(item, data))
        graphThread = MotorTempGraph(data, name, None)
        graphThread.start()

    def update_plot(self, item, data):
        """Updates plotdata"""
        data[1].append(item.value)
        data[0].append(time.time())


#TODO:
    #Es passiert noch nix, beim Klicken auf die Menüpunkte. die GenericView müsste
    #glaube ich angesprochen werden und dann die entsprechende View im Uebersichtsfenster hinzufügen.
    def make_view(self, name, clazz, **kwargs):
        """
        Creates a generic view from a specified clazz.

        :param name: The name that shall be registered as an observer.
        :type name: String
        :param clazz: A Frame, from which the generic view is created.
        :type clazz: Frame
        """
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

    def on_nachrichtenButtonEigenesFenster_clicked(self, *args):
        """
        Makes the extended log view visible.
        """
        print("Externes Fenster fuer Nachrichten wurde erstellt")

        self.NewsExt.show()

    def open_confirmationwin(self, *args):
        """
        Opens the confirmation window on clicking one of the 'quit'-buttons.
        """
        self.confWin.show()
        return True

    def on_messagedialogQuitConf_delete(self, *args):
        """
        Closes the confirmation window on positive confirmation.
        """
        self.confWin.hide()
        return True  # Signal wurde vollständig bearbeitet

    def on_buttonConfN_clicked(self, *args):
        """
        Closes the confirmation window on negative confirmation.
        """
        self.confWin.hide()
        return True  # Signal wurde vollständig bearbeitet

#------------------------------------------------------------------------------
#Diese folgenden Handler werden zZ. nicht benötigt, können aber später verwendet werden, falls die Debug-UI um
#die Optionen "Ansicht speichern" usw. in der Menüleiste, erweitert werden möchte. Gladedateien vorhanden.
    def on_imageMenuItemOeffnen_activate(self, *args):
        """
        Opens the 'Open'-filechooser.
        """
        self.builderFilChoOp = gtk.Builder()
        self.builderFilChoOp.add_from_file(
            find("Projekt_DebugUI_FilechooserOeffnen.glade"))
        self.filChoOp = self.builderFilChoOp.get_object(
            "filechooserdialogOeffnen")
        self.builderFilChoOp.connect_signals(self)
        print ("Oeffnen-Filechooser wurde erstellt")
        self.filChoOp.show()

    def on_imageMenuItemSpeichernUnter_activate(self, *args):
        """
        Opens the 'Save as'-filechooser.
        """
        self.builderFilChoSav = gtk.Builder()
        self.builderFilChoSav.add_from_file(
            find("Projekt_DebugUI_FilechooserSpeichernUnter.glade"))
        self.filChoSav = self.builderFilChoSav.get_object(
            "filechooserdialogSpeichernUnter")
        self.builderFilChoSav.connect_signals(self)
        print ("SpeichernUnter-Filechooser wurde erstellt")
        self.filChoSav.show()

    def on_imageMenuItemPreferences_activate(self, *args):
        """
        Opens the window for changing preferences.
        """
        self.builderPref = gtk.Builder()
        self.builderPref.add_from_file(
            find("Projekt_DebugUI_Einstellungenfenster.glade"))
        self.Pref = self.builderPref.get_object("windowEinstellungen")
        self.builderPref.connect_signals(self)
        print("Preferences-Fenster wurde erstellt")
        self.Pref.show()

    def on_filechooserdialogSpeichernUnter_destroy(self, *args):
        """
        Closes the 'Save as' filechooser.
        """
        self.filChoSav.destroy()
        print ("SpeichernUnter-Filechooser wurde geschlossen")
        return True  # Signal wurde vollständig bearbeitet

    def on_filechooserdialogOeffnen_destroy(self, *args):
        """
        Closes the Filechooser for opening files.
        """
        self.filChoOp.destroy()
        print("Oeffnen-Filechooser wurde geschlossen")
        return True  # Signal wurde vollständig bearbeitet

    def on_windowEinstellungen_destroy(self, *args):
        """
        Closes the preferences window
        """
        self.Pref.destroy()
        print("Einstellungenfenster wurde geschlossen")
        return True  # Signal wurde vollständig bearbeitet
#------------------------------------------------------------------------------

    def on_roboButtonEigenesFenster_clicked(self, *args):
        """
        Opens the robot selection in a seperate window.
        """
        print("Externes Fenster fuer Roboterauswahl wurde erstellt")
        self.RoboSel.show_all()

    def on_RoboSelectExtern_destroy(self, *args):
        """
        Closes the seperate robot selection window.
        """
        self.RoboSel.hide()
        print("externes Robofenster geschlossen bzw versteckt")
        return True  # Verhindern der Zerstörung des Fenseters (angeblich)

    def on_delete_extern_log_view(self, *donotcare):
        """
        Closes the seperate log view.
        """
        self.NewsExt.hide()  # Fenster verstecken
        print "externe log view verstecken"
        return True  # Signal nicht weiter verarbeiten

    def on_uebersichtButtonMax_clicked(self, *args):
        """
        Maximizes the Overview within the main window and changes the
        button to be able do de-maximize it.
        """
        print "Die Zähmung des Widerspenstigen Buttons"

        self.uebersichtBttnMax = self.builderMainWin.get_object(
            "uebersichtButtonMax")
        self.hPane = self.builderMainWin.get_object("hpaned1")

        if(self.uebersichtBttnMax.get_stock_id() == "gtk-fullscreen"):
            print "Wenn Button fullscreenbild hat dann aender ihn zu +kleiner machen+"
            self.uebersichtBttnMax.set_stock_id("gtk-leave-fullscreen")

            self.hPane.set_position(0)

        else:
            print "Wenn Button +wiedern kleiner machen+ dann aender ihn zu fullscreen"
            self.uebersichtBttnMax.set_stock_id("gtk-fullscreen")
            self.hPane.set_position(300)

    def on_roboButtonMax_clicked(self, *args):
        self.roboBttnMax = self.builderMainWin.get_object("roboButtonMax")
        self.uebersicht = self.builderMainWin.get_object("uebersichtsFrame")
        self.nachrichtExp = self.builderMainWin.get_object(
            "NachrichtenverlaufExpander")
        self.vPane1 = self.builderMainWin.get_object("vpaned1")

        if(self.roboBttnMax.get_stock_id() == "gtk-fullscreen"):
            print "Wenn Button fullscreenbild hat dann aender ihn zu +kleiner machen+"
            self.roboBttnMax.set_stock_id("gtk-leave-fullscreen")

            self.uebersicht.hide()
            self.nachrichtExp.set_expanded(False)
            self.vPane1.set_position(925)

        else:
            print "Wenn Button +wiedern kleiner machen+ dann aender ihn zu fullscreen"
            self.roboBttnMax.set_stock_id("gtk-fullscreen")
            self.uebersicht.show()
            self.nachrichtExp.set_expanded(True)
            self.vPane1.set_position(280)

    def on_nachrichtenButtonMax_clicked(self, *args):
        """
        Maximizes the log and changes the button, allowing to
        restore it to normal size.
        """
        print ("maximiere das Nachrichtenfenster")

        self.nachrichtBttnMax = self.builderMainWin.get_object(
            "nachrichtenButtonMax")
        self.uebersicht = self.builderMainWin.get_object("uebersichtsFrame")
        self.roboAuswExp = self.builderMainWin.get_object(
            "RoboauswahlExpander")
        self.vPane1 = self.builderMainWin.get_object("vpaned1")

        if(self.nachrichtBttnMax.get_stock_id() == "gtk-fullscreen"):
            print "Wenn Button fullscreenbild hat dann aender ihn zu +kleiner machen+"
            self.nachrichtBttnMax.set_stock_id("gtk-leave-fullscreen")

            self.uebersicht.hide()
            self.roboAuswExp.set_expanded(False)
            self.vPane1.set_position(0)

        else:
            print "Wenn Button +wiedern kleiner machen+ dann aender ihn zu fullscreen"
            self.nachrichtBttnMax.set_stock_id("gtk-fullscreen")
            self.uebersicht.show()
            self.roboAuswExp.set_expanded(True)
            self.vPane1.set_position(280)

    def on_imagemenuitemAbout_activate(self, *args):
        print("öffne das Aboutfenster")
        """
        Opens the 'About'-window.
        """
        print("öffne das Aboutfenster")
        self.aboutD.show()

    def on_buttonAboutfensterSchliessen_clicked(self, *args):
        """
        Closes the 'About'-window.
        """
        print("schließe das Aboutfenster")
        self.aboutD.hide()
        return True  # gtk mitteilen das signal bearbeitet wurde

#--------------------------------------------------------------


def format(item):
    """
    Formats the given items according to their type.

    :param item: The Item to Format.
    :type item: Matrices, numbers or .dot-files
    """
    if item.type == "matrix":
        shape = item.value.shape[:2]
        return "Matrix mit %d Zeilen und %d Spalten" % tuple(shape)

    if item.type == "number":
        return "%1.4f" % float(item.value)

    if item.name.endswith(".Dot"):
        return "Dot File Information"

    return str(item.value)[:100]



#if __name__ == "__main__":
            #mainwindow = DebugUiMainWin(server)
            #gtk.main()
