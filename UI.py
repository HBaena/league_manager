import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Pango
from data_structs import User, League


def doc(o):
    print(dir(o))


def init_menu_bar(parent):
    parent.builder.get_object("menuitem_contact").set_label("Comité")
    parent.builder.get_object("menuitem_contact").connect("activate",
                                                          lambda i, parent: go_to_contact(parent),
                                                          parent)


def add_result():
    builder = Gtk.Builder()
    builder.add_from_file("add_result.glade")

    # LAYOUT
    result = [None, None]
    dialog = builder.get_object("main")
    accept = builder.get_object("button_ok")
    cancel = builder.get_object("button_cancel")
    visit = builder.get_object("entry_visitgoals")
    local = builder.get_object("entry_localgoals")
    dialog.add_action_widget(accept, 0)
    dialog.add_action_widget(cancel, 1)

    def on_accept(button, result):

        try:
            result[0] = int(local.get_text())
        except Exception as e:
            local.set_text("")
        try:
            result[1] = int(visit.get_text())
        except Exception as e:
            visit.set_text("")

        if local.get_text() != "" and visit.get_text() != "":
            dialog.destroy()

    accept.connect("clicked", on_accept, result)
    dialog.set_focus(cancel)
    cancel.connect("clicked", lambda button, dialog: dialog.destroy(), dialog)

    response = dialog.run()
    return result


def fill_tree_view_list(headers, data, list_model, tree):
    # headers       ---> ["...", ..., "..."]
    # list_model    ---> Gtk.List_store(str, str, ..., str)
    # data          ---> [][]
    # Adding data to ListStore
    for i in range(len(data)):
        list_model.append(data[i])
    # Setting model to tree
    tree.set_model(list_model)
    # Adding columns to tree
    for i, column in enumerate(headers):
        cell = Gtk.CellRendererText()
        if i == 0:
            # Headers
            cell.props.weight_set = True
            cell.props.weight = Pango.Weight.BOLD
        # Column
        col = Gtk.TreeViewColumn(column, cell, text=i)
        # Append column
        tree.append_column(col)


def fill_combo_box(combo_box, combo_list, data):
    for text in data:
        combo_list.append(text)
    combo_box.set_model(combo_list)
    combo_box.set_active(0)
    renderer_text = Gtk.CellRendererText()
    combo_box.pack_start(renderer_text, True)
    combo_box.add_attribute(renderer_text, "text", 0)


def go_back(previous, present):
    previous.set_visible(True)
    present.close()


def transfer(parent, present):
    parent.set_visible(False)
    parent.set_focus(None)
    present.present()


def go_to_contact(parent):
    transfer(parent, WContact(parent))


def go_to_admin_manager(parent):
    transfer(parent, WAdminManager(parent))


def go_to_team_manager(parent):
    transfer(parent, WTeamManager(parent))


def go_to_view_team(parent):
    transfer(parent, WViewTeam(parent))


def go_to_view_player(parent):
    transfer(parent, WViewPlayer(parent))


def go_to_add_team(parent):
    transfer(parent, WAddTeam(parent))


def go_to_add_player(parent):
    transfer(parent, WAddPlayer(parent))


def go_to_add_user(parent):
    transfer(parent, WAddUser(parent))


def go_to_add_tournament(parent):
    transfer(parent, WAddTournament(parent))


def go_to_add_match(parent):
    transfer(parent, WAddMatch(parent))


class WMain(Gtk.Window):
    """docstring for WindowMain"""

    def __init__(self, DB_connection=None):
        # init parent
        Gtk.Window.__init__(self)
        self.DB_connection = DB_connection
        self.builder = None
        self.layout_main = None
        self.tournament_list = None
        # Putting max size to the window
        self.maximize()
        # Avoiding resize window
        self.set_resizable(False)
        # self.fullscreen()
        self.set_title("MAIN")
        # Adding elements to the window
        self.init()
        # Connecting destroy action
        self.connect("destroy", self.onDestroy)
        self.set_focus(self.builder.get_object("button_login"))

    def init(self):
        # Reading builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file("main.glade")

        # LAYOUT
        self.layout_main = self.builder.get_object("layout_main")
        self.add(self.layout_main)

        # COMBOBOX
        combobox_tournament = self.builder.get_object("combobox_tournament")
        league = League(1)
        text_tournament = league.get_tournaments(self.DB_connection)
        self.tournament_list = Gtk.ListStore(str)
        fill_combo_box(combobox_tournament, self.tournament_list, text_tournament)
        combobox_tournament.connect("changed", self.on_tournament_changed)

        # BUTTONS
        self.builder.get_object("button_login").connect("clicked", self.on_login_pressed)

        # INIT MENUBAR
        init_menu_bar(self)

        # TREEVIEWLIST
        headers = ["Nombre", "Apellido paterno", "Apellido materno"]
        data = [
            ["Adán", "Hernández", "Baena"],
            ["Adán", "Hernández", "Baena"],
            ["Adán", "Hernández", "Baena"]
        ]
        list_model = Gtk.ListStore(str, str, str)
        tree = self.builder.get_object("treeview_teams")
        fill_tree_view_list(headers, data, list_model, tree)

    def onDestroy(self, *args):
        print("OnDestroy")
        Gtk.main_quit()

    def on_login_pressed(self, button):
        text_user = self.builder.get_object("entry_user").get_text()
        text_password = self.builder.get_object("entry_password").get_text()

        if text_user == '' or text_password == '':
            DialogOK("Debe ingresar ambos datos.")
            return

        user = User(text_user, text_password)

        if not user.valid_user(self.DB_connection):
            DialogOK("Usuario invalido.")
            self.builder.get_object("entry_user").set_text('')
            self.builder.get_object("entry_password").set_text('')
            return
        else:
            if not user.valid_password(self.DB_connection):
                DialogOK("Contraseña invalida.")
                self.builder.get_object("entry_password").set_text('')
                return

        self.builder.get_object("entry_user").set_text('')
        self.builder.get_object("entry_password").set_text('')

        if user.ocupation == 'admin':
            go_to_admin_manager(self)
        elif user.ocupation == 'referee':
            pass
        elif user.ocupation == 'manager':
            go_to_team_manager(self)

    def on_tournament_changed(self, combo):
        print(combo)
        i = combo.get_active_iter()
        print(combo.get_model()[i][0])


class WViewTeam(Gtk.Window):
    """docstring for WindowMain"""

    def __init__(self, parent=None, team=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        # Setting team info
        self.team = team
        # Putting max size to the window
        self.maximize()
        # Avoiding resize window 
        self.set_resizable(False)
        # self.fullscreen()
        self.set_title("MAIN")
        # Adding elements to the window
        self.init()
        # Connecting destroy action
        self.connect("destroy", self.onDestroy)

        self.set_focus(self.builder.get_object("button_login"))

    def init(self):
        # Reading builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file("view_team.glade")

        # LAYOUT
        self.layout_main = self.builder.get_object("layout_main")
        self.add(self.layout_main)

        # menubar
        self.builder.get_object("button_back").connect(
            "clicked", lambda button, parent, present:
            go_back(parent, present), self.parent, self)

    def onDestroy(self, *args):
        go_back(self.parent, self)


class WViewPlayer(Gtk.Window):
    """docstring for WindowMain"""

    def __init__(self, parent=None, team=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        # Setting team info
        self.team = team
        # Putting max size to the window
        self.maximize()
        # Avoiding resize window 
        self.set_resizable(False)
        # self.fullscreen()
        self.set_title("MAIN")
        # Adding elements to the window
        self.init()
        # Connecting destroy action
        self.connect("destroy", self.onDestroy)

    def init(self):
        # Reading builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file("view_player.glade")

        # LAYOUT
        self.layout_main = self.builder.get_object("layout_main")
        self.add(self.layout_main)

        # BUTTON
        self.builder.get_object("button_back").connect(
            "clicked", lambda button, parent, present:
            go_back(parent, present), self.parent, self)

    def onDestroy(self, *args):
        go_back(self.parent, self)


class WContact(Gtk.Window):
    """docstring for WindowMain"""

    def __init__(self, parent=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        # Putting max size to the window
        self.maximize()
        # Avoiding resize window 
        self.set_resizable(False)
        # self.fullscreen()
        self.set_title("MAIN")
        # Adding elements to the window
        self.init()
        # Connecting destroy action
        self.connect("destroy", self.onDestroy)

        self.set_focus(self.builder.get_object("button_login"))

    def init(self):
        # Reading builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file("contact.glade")

        # LAYOUT
        self.layout_main = self.builder.get_object("layout_main")
        self.add(self.layout_main)

        # BUTTON
        self.builder.get_object("button_back").connect(
            "clicked", lambda button, parent, present:
            go_back(parent, present), self.parent, self)

    def onDestroy(self, *args):
        go_back(self.parent, self)


class WAdminManager(Gtk.Window):
    """docstring for WindowAdminManager"""

    def __init__(self, parent=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        # Putting max size to the window
        self.maximize()
        # Avoiding resize window 
        self.set_resizable(False)
        # self.fullscreen()
        self.set_title("MAIN")
        # Adding elements to the window
        self.init()
        # Connecting destroy action
        self.connect("destroy", self.onDestroy)

        self.set_focus(self.builder.get_object("layout_main"))

    def init(self):
        # Reading builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file("admin_manager.glade")

        # LAYOUT
        self.layout_main = self.builder.get_object("layout_main")
        self.add(self.layout_main)

        # BUTTONS
        self.builder.get_object("button_back").connect(
            "clicked", lambda button, parent, present:
            go_back(parent, present), self.parent, self)

        self.builder.get_object("button_add").connect("clicked", self.on_add_button_pressed)
        self.builder.get_object("button_modify").connect("clicked", self.on_modify_button_pressed)
        self.builder.get_object("button_delete").connect("clicked", self.on_delete_button_pressed)

        # SEARCHENTRY
        self.builder.get_object("serachentry_global").connect("search-changed", self.on_search_changed)

    def on_search_changed(self, entry):
        print(entry.get_text())

    def on_add_button_pressed(self, button):
        active = self.builder.get_object("stack").get_visible_child().get_name()
        print(active)

        if active == "Tournament":
            go_to_add_tournament(self)
        elif active == "Team":
            go_to_add_team(self)
        elif active == "Player":
            go_to_add_player(self)
        elif active == "User":
            go_to_add_user(self)
        elif active == "Match":
            go_to_add_match(self)

    def on_modify_button_pressed(self, button):
        active = self.builder.get_object("stack").get_visible_child().get_name()
        print(active)

    def on_delete_button_pressed(self, button):
        active = self.builder.get_object("stack").get_visible_child().get_name()
        dialog = DialogConfirm(self, "Delete " + active + "?", "¿Está seguro de eliminar?")
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Delete")

        dialog.destroy()

    def onDestroy(self, *args):
        go_back(self.parent, self)


class WTeamManager(Gtk.Window):
    """docstring for WindowAdminManager"""

    def __init__(self, parent=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        # Putting max size to the window
        self.maximize()
        # Avoiding resize window 
        self.set_resizable(False)
        # self.fullscreen()
        self.set_title("MAIN")
        # Adding elements to the window
        self.init()
        # Connecting destroy action
        self.connect("destroy", self.onDestroy)

        self.set_focus(self.builder.get_object("button_back"))

    def init(self):
        # Reading builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file("manager_team.glade")

        # LAYOUT
        self.layout_main = self.builder.get_object("layout_main")
        self.add(self.layout_main)

        # BUTTON
        self.builder.get_object("button_back").connect(
            "clicked", lambda button, parent, present:
            go_back(parent, present), self.parent, self)

        self.builder.get_object("button_add").connect("clicked", self.on_add_button_pressed)
        self.builder.get_object("button_modify").connect("clicked", self.on_modify_button_pressed)
        self.builder.get_object("button_delete").connect("clicked", self.on_delete_button_pressed)

    def on_add_button_pressed(self, button):
        print("Hola")

    def on_modify_button_pressed(self, button):
        print("Hola")

    def on_delete_button_pressed(self, button):
        print("Hola")

    def onDestroy(self, *args):
        go_back(self.parent, self)


class WAddTeam(Gtk.Window):
    """docstring for WindowAdminManager"""

    def __init__(self, parent=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        # Putting max size to the window
        self.maximize()
        # Avoiding resize window 
        self.set_resizable(False)
        # self.fullscreen()
        self.set_title("MAIN")
        # Adding elements to the window
        self.init()
        # Connecting destroy action
        self.connect("destroy", self.onDestroy)

        self.set_focus(self.builder.get_object("button_back"))

    def init(self):
        # Reading builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file("add_team.glade")

        # LAYOUT
        self.layout_main = self.builder.get_object("layout_main")
        self.add(self.layout_main)

        # BUTTON
        self.builder.get_object("button_back").connect(
            "clicked", lambda button, parent, present:
            go_back(parent, present), self.parent, self)
        self.builder.get_object("button_add").connect("clicked", self.on_add_button_pressed)

    def on_add_button_pressed(self, button):
        print("Hola")

    def onDestroy(self, *args):
        go_back(self.parent, self)


class WAddUser(Gtk.Window):
    """docstring for WindowAdminManager"""

    def __init__(self, parent=None, user=None):
        Gtk.Window.__init__(self)
        self.user = user
        self.builder = None
        self.layout_main = None
        # Setting parent window
        self.parent = parent
        # Putting max size to the window
        self.maximize()
        # Avoiding resize window 
        self.set_resizable(False)
        # self.fullscreen()
        self.set_title("MAIN")
        # Adding elements to the window
        self.init()
        # Connecting destroy action
        self.connect("destroy", self.onDestroy)

        self.set_focus(self.builder.get_object("button_back"))

    def init(self):
        # Reading builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file("add_user.glade")

        # LAYOUT
        self.layout_main = self.builder.get_object("layout_main")
        self.add(self.layout_main)

        # BUTTON
        self.builder.get_object("button_back").connect(
            "clicked", lambda button, parent, present:
            go_back(parent, present), self.parent, self)
        self.builder.get_object("button_add").connect("clicked", self.on_add_button_pressed)

    def on_add_button_pressed(self, button):
        name = self.builder.get_object("entry_name")
        last_name = self.builder.get_object("entry_lastname")
        name = self.builder.get_object("entry_name")

    def onDestroy(self, *args):
        go_back(self.parent, self)


class WAddPlayer(Gtk.Window):
    """docstring for WindowAdminManager"""

    def __init__(self, parent=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        # Putting max size to the window
        self.maximize()
        # Avoiding resize window 
        self.set_resizable(False)
        # self.fullscreen()
        self.set_title("MAIN")
        # Adding elements to the window
        self.init()
        # Connecting destroy action
        self.connect("destroy", self.onDestroy)

        self.set_focus(self.builder.get_object("button_back"))

    def init(self):
        # Reading builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file("add_player.glade")

        # LAYOUT
        self.layout_main = self.builder.get_object("layout_main")
        self.add(self.layout_main)

        # BUTTON
        self.builder.get_object("button_back").connect(
            "clicked", lambda button, parent, present:
            go_back(parent, present), self.parent, self)

        self.builder.get_object("button_add").connect("clicked", self.on_add_button_pressed)

    def on_add_button_pressed(self, button):
        print("Hola")

    def onDestroy(self, *args):
        go_back(self.parent, self)


class WAddTournament(Gtk.Window):
    """docstring for WindowAdminManager"""

    def __init__(self, parent=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        # Putting max size to the window
        self.maximize()
        # Avoiding resize window 
        self.set_resizable(False)
        # self.fullscreen()
        self.set_title("MAIN")
        # Adding elements to the window
        self.init()
        # Connecting destroy action
        self.connect("destroy", self.onDestroy)

        self.set_focus(self.builder.get_object("button_back"))

    def init(self):
        # Reading builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file("add_tournament.glade")

        # LAYOUT
        self.layout_main = self.builder.get_object("layout_main")
        self.add(self.layout_main)

        # BUTTON
        self.builder.get_object("button_back").connect(
            "clicked", lambda button, parent, present:
            go_back(parent, present), self.parent, self)

        self.builder.get_object("button_add").connect("clicked", self.on_add_button_pressed)

    def on_add_button_pressed(self, button):
        print("Hola")

    def onDestroy(self, *args):
        go_back(self.parent, self)


class WAddMatch(Gtk.Window):
    """docstring for WindowAdminManager"""

    def __init__(self, parent=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        # Putting max size to the window
        self.maximize()
        # Avoiding resize window 
        self.set_resizable(False)
        # self.fullscreen()
        self.set_title("MAIN")
        # Adding elements to the window
        self.init()
        # Connecting destroy action
        self.connect("destroy", self.onDestroy)

        self.set_focus(self.builder.get_object("button_back"))

    def init(self):
        # Reading builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file("add_match.glade")

        # LAYOUT
        self.layout_main = self.builder.get_object("layout_main")
        self.add(self.layout_main)

        # BUTTON
        self.builder.get_object("button_back").connect(
            "clicked", lambda button, parent, present:
            go_back(parent, present), self.parent, self)

        self.builder.get_object("button_add_match").connect("clicked", self.on_add_button_pressed)
        # popover de cada button
        popover = self.builder.get_object("popover_add_match")
        # Añadir señal de evento y añadir popover
        self.builder.get_object("button_add_match").connect("event", self.on_event, popover)

        # popover de cada button
        popover = self.builder.get_object("popover_finish")
        # Añadir señal de evento y añadir popover
        self.builder.get_object("button_finish").connect("event", self.on_event, popover)

    def on_event(self, widget, event, popover):
        # doc(event)
        MOUSE_RIGHT = 3
        if event.type == Gdk.EventType.BUTTON_PRESS and event.get_button()[1] == MOUSE_RIGHT:
            popover.popup()

    def on_add_button_pressed(self, button):
        print("Hola")

    def onDestroy(self, *args):
        go_back(self.parent, self)


class DialogConfirm(Gtk.Dialog):

    def __init__(self, parent, title, text_content):
        Gtk.Dialog.__init__(self, title, parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.set_default_size(150, 100)
        label = Gtk.Label(text_content)
        label.set_name("label_h3")
        box = self.get_content_area()
        box.add(label)
        self.show_all()


class DialogOK(Gtk.MessageDialog):

    def __init__(self, text):
        Gtk.Dialog.__init__(self)
        self.set_default_size(150, 100)
        self.message_type = Gtk.MessageType.ERROR
        label = Gtk.Label(text)
        label.set_name("label_header2")
        self.add_button("Aceptar", 1)
        self.get_content_area().add(label)
        self.get_content_area().set_name("dialog")
        self.show_all()
        self.run()
        self.destroy()
