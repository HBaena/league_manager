import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Pango
from data_structs import *


def doc(o):
    print(dir(o))


def init_menu_bar(parent):
    parent.builder.get_object("menuitem_contact").set_label("Comité")
    parent.builder.get_object("menuitem_contact").connect("activate",
                                                          lambda i, parent: go_to_contact(parent),
                                                          parent)


def check_void(list):
    for i in list:
        if i == '':
            return True
    return False


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
    # combo_model    ---> Gtk.List_store(str, str, ..., str)
    # data          ---> [['dsd'], ...]

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


def go_to_contact(parent, sql):
    transfer(parent, WContact(parent, sql))


def go_to_admin_manager(parent, sql):
    transfer(parent, WAdminManager(parent, sql))


def go_to_team_manager(parent, sql):
    transfer(parent, WTeamManager(parent, sql))


def go_to_view_team(parent, sql):
    transfer(parent, WViewTeam(parent, sql))


def go_to_view_player(parent, sql):
    transfer(parent, WViewPlayer(parent, sql))


def go_to_add_team(parent, sql, team=None):
    transfer(parent, WAddTeam(parent, sql, team))


def go_to_add_player(parent, sql):
    transfer(parent, WAddPlayer(parent, sql))


def go_to_add_user(parent, sql, user=None):
    transfer(parent, WAddUser(parent, sql, user))


def go_to_add_tournament(parent, sql):
    transfer(parent, WAddTournament(parent, sql))


def go_to_add_match(parent, sql):
    transfer(parent, WAddMatch(parent, sql))


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
            go_to_admin_manager(self, self.DB_connection)
        elif user.ocupation == 'referee':
            pass
        elif user.ocupation == 'manager':
            go_to_team_manager(self, self.DB_connection)

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

    def __init__(self, parent=None, DB_connection=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        self.DB_connection = DB_connection
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

        # treeviewlist
        # users
        users = self.builder.get_object("treeview_user")
        headers = ["Nombre", "Apellido paterno", "Apellido materno", "Ciudad", "Usuario", "Contraseña"]
        list_model = Gtk.ListStore(str, str, str, str, str, str)
        data = self.DB_connection.read("Usr", ["name", "last_name", "last_last_name", "city", "email", "password"])
        fill_tree_view_list(headers, data, list_model, users)
        # players
        users = self.builder.get_object("treeview_player")
        headers = ["CURP", "Nombre", "Apellido paterno", "Apellido materno", "Ciudad", "Equipo"]
        list_model = Gtk.ListStore(str, str, str, str, str, str)
        columns = ["Player.curp", "Player.name", "Player.last_name", "Player.last_last_name", "Player.city", "Team.name"]
        tables = ["Player", "Team"]
        condition = "Player.id_team = Team.id_team"
        data = self.DB_connection.select_tables(tables, columns, condition)

        fill_tree_view_list(headers, data, list_model, users)

    def on_search_changed(self, entry):
        print(entry.get_text())

    def on_add_button_pressed(self, button):
        active = self.builder.get_object("stack").get_visible_child().get_name()
        print(active)

        if active == "Tournament":
            go_to_add_tournament(self, self.DB_connection)
        elif active == "Team":
            go_to_add_team(self, self.DB_connection)
        elif active == "Player":
            go_to_add_player(self, self.DB_connection)
        elif active == "User":
            go_to_add_user(self, self.DB_connection)
        elif active == "Match":
            go_to_add_match(self, self.DB_connection)

    def on_modify_button_pressed(self, button):
        active = self.builder.get_object("stack").get_visible_child().get_name()

        if active == "Tournament":
            go_to_add_tournament(self, self.DB_connection)
        elif active == "Team":
            go_to_add_team(self, self.DB_connection)
        elif active == "Player":
            go_to_add_player(self, self.DB_connection)
        elif active == "User":
            # go_to_add_user(self, self.DB_connection)
            model, selection = self.builder.get_object("selection_user").get_selected()
            data = self.DB_connection.read("Usr", ["*"], "email='{}'".format(model[selection][4]))[0]
            user = User(data[10], data[11], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9],
                        data[12], data[0], data[1])
            go_to_add_user(self, self.DB_connection, user)
            return
        elif active == "Match":
            go_to_add_match(self, self.DB_connection)

        self.builder.get_object("selection_user").unselect_all()

    def on_delete_button_pressed(self, button):
        active = self.builder.get_object("stack").get_visible_child().get_name()
        dialog = DialogConfirm(self, "Delete " + active + "?", "¿Está seguro de eliminar?")
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            model, selection = None, None
            if active == "User":
                model, selection = self.builder.get_object("selection_user").get_selected()
                self.DB_connection.delete('Usr', "email='{}'".format(model[selection][4]))
            elif active == "Player":
                model, selection = self.builder.get_object("selection_player").get_selected()
                self.DB_connection.delete('Player', "curp='{}'".format(model[selection][0]))
            if model is not None:
                model.remove(selection)
            self.DB_connection.commit()
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

    def __init__(self, parent=None, DB_connection=None, team=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        self.DB_connection = DB_connection
        self.team = team
        self.builder = None
        self.layout_main = None
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
        teamname = self.builder.get_object("entry_teamname")
        teamshortname = self.builder.get_object("entry_teamshortname")
        matchtime = self.builder.get_object("entry_matchtime")
        matchplace = self.builder.get_object("entry_matchplace")
        name = self.builder.get_object("entry_name").get_text()
        last_name = self.builder.get_object("entry_lastname").get_text()
        last_last_name = self.builder.get_object("entry_llastname").get_text()
        city = self.builder.get_object("entry_city").get_text()
        suburb = self.builder.get_object("entry_suburb").get_text()
        street = self.builder.get_object("entry_street").get_text()
        number = self.builder.get_object("entry_number").get_text()
        phonenumber = self.builder.get_object("entry_phonenumber").get_text()
        email = self.builder.get_object("entry_email").get_text()
        password = self.builder.get_object("entry_password").get_text()
        password2 = self.builder.get_object("entry_password2").get_text()
        entries = [teamname, teamshortname, matchplace, matchtime, name, last_name, last_last_name, city, suburb,
                   street, number, phonenumber, email, password, password2]
        if check_void(entries):
            DialogOK("Debe ingresar todos los datos")
            return
        if password != password2:
            DialogOK("La contraseña no coincide")
            self.builder.get_object("entry_password").set_text("")
            self.builder.get_object("entry_password2").set_text("")
            return
        if User(email).valid_user(self.DB_connection):
            DialogOK("El usuario/email ya está registrado.")
            self.builder.get_object("entry_email").set_text("")
            return
        user = User(email, password, name, last_name, last_last_name, city, suburb, street, number, phonenumber,
                    'manager', id_league=1)
        user.add(self.DB_connection)
        team = Team(teamname, teamshortname, matchplace, id_dt=user.id_user)
        team.add(self.DB_connection)
        DialogOK("Se ha aañadido correctamente el equipo y DT.")
        self.onDestroy()

    def onDestroy(self, *args):
        go_back(self.parent, self)


class WAddUser(Gtk.Window):
    """docstring for WindowAdminManager"""

    def __init__(self, parent=None, DB_connection=None, user=None):
        Gtk.Window.__init__(self)
        self.user = user
        self.builder = None
        self.layout_main = None
        self.DB_connection = DB_connection
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
        # combobox
        combo_job = self.builder.get_object("combobox_job")
        job_list = Gtk.ListStore(str)
        data = [['Admin'], ['DT'], ['Árbitro']]
        fill_combo_box(combo_job, job_list, data)

        if self.user is not None:
            self.builder.get_object("entry_name").set_text(self.user.name)
            self.builder.get_object("entry_lastname").set_text(self.user.last_name)
            self.builder.get_object("entry_llastname").set_text(self.user.last_last_name)
            self.builder.get_object("entry_phonenumber").set_text(self.user.phone)
            self.builder.get_object("entry_city").set_text(self.user.city)
            self.builder.get_object("entry_suburb").set_text(self.user.suburb)
            self.builder.get_object("entry_street").set_text(self.user.street)
            self.builder.get_object("entry_number").set_text(str(self.user.no))
            self.builder.get_object("entry_email").set_text(self.user.email)
            self.builder.get_object("entry_password").set_text(self.user.password)
            self.builder.get_object("entry_password2").set_text(self.user.password)
            if self.user.ocupation == 'admin':
                self.builder.get_object("combobox_job").set_active(0)
            elif self.user.ocupation == 'manager':
                self.builder.get_object("combobox_job").set_active(1)
            elif self.user.ocupation == 'referee':
                self.builder.get_object("combobox_job").set_active(2)
            self.builder.get_object("button_add").set_label("Modificar")

    def on_add_button_pressed(self, button):
        name = self.builder.get_object("entry_name").get_text()
        last_name = self.builder.get_object("entry_lastname").get_text()
        last_last_name = self.builder.get_object("entry_llastname").get_text()
        city = self.builder.get_object("entry_city").get_text()
        suburb = self.builder.get_object("entry_suburb").get_text()
        street = self.builder.get_object("entry_street").get_text()
        number = self.builder.get_object("entry_number").get_text()
        phonenumber = self.builder.get_object("entry_phonenumber").get_text()
        email = self.builder.get_object("entry_email").get_text()
        password = self.builder.get_object("entry_password").get_text()
        password2 = self.builder.get_object("entry_password2").get_text()
        i = self.builder.get_object("combobox_job").get_active_iter()
        job = self.builder.get_object("combobox_job").get_model()[i][0]

        entries = [name, last_name, last_last_name, city, suburb, street, number, phonenumber, email, password,
                   password2]

        if check_void(entries):
            DialogOK("Debes llenar todos los campos.")
            return

        if password != password2:
            DialogOK("La contraseña no coincide.")
            self.builder.get_object("entry_password").set_text("")
            self.builder.get_object("entry_password2").set_text("")
            return
        user = User(email)

        if job == 'Admin':
            self.user.ocupation = 'admin'
        elif job == 'DT':
            self.user.ocupation = 'manager'
        elif job == 'Árbitro':
            self.user.ocupation = 'referee'

        if button.get_label() == "Modificar":
            self.user.email = email
            self.user.password = password
            self.user.name = name
            self.user.last_name = last_name
            self.user.last_last_name = last_last_name
            self.user.city = city
            self.user.suburb = suburb
            self.user.street = street
            self.user.no = number
            self.user.phone = phonenumber
            self.user.update(self.DB_connection)
            DialogOK("Se ha modificado con éxito.")
        else:
            if user.valid_user(self.DB_connection):
                DialogOK("El e-mail ya está registrado.")
                self.builder.get_object("entry_email").set_text("")
                return

            del user
            user = User(email, password, name, last_name, last_last_name, city, suburb, street, number, phonenumber,
                        job)
            user.add(self.DB_connection)
            DialogOK("Se ha agregado con éxito.")
        self.onDestroy()

    def onDestroy(self, *args):
        go_back(self.parent, self)


class WAddPlayer(Gtk.Window):
    """docstring for WindowAdminManager"""

    def __init__(self, parent=None, DB_connection=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        self.DB_connection = DB_connection
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

    def __init__(self, parent=None, DB_connection=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        self.DB_connection = DB_connection
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

    def __init__(self, parent=None, DB_connection=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        self.DB_connection = DB_connection
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
