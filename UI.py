import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Pango
from data_structs import *


def doc(o):
    print(dir(o))


def init_menu_bar(parent, sql):
    parent.builder.get_object("menuitem_contact").set_label("Comité")
    parent.builder.get_object("menuitem_contact").connect("activate",
                                                          lambda i, parent, sql: go_to_contact(parent, sql),
                                                          parent, sql)


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


def go_to_contact(parent, sql=None):
    transfer(parent, WContact(parent, sql))


def go_to_admin_manager(parent, sql):
    transfer(parent, WAdminManager(parent, sql))


def go_to_team_manager(parent, sql, team=None):
    transfer(parent, WTeamManager(parent, sql, team))


def go_to_view_team(parent, sql, team=None):
    transfer(parent, WViewTeam(parent, sql, team))


def go_to_view_player(parent, sql, player=None):
    transfer(parent, WViewPlayer(parent, sql, player))


def go_to_add_team(parent, sql, team=None, dt=None):
    transfer(parent, WAddTeam(parent, sql, team, dt))


def go_to_add_player(parent, sql, player=None):
    transfer(parent, WAddPlayer(parent, sql, player))


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
        self.builder.get_object("button_select_team").connect("clicked", self.on_button_select_pressed)
        # ENTRIES
        self.builder.get_object("entry_password").connect("key-press-event", self.onKeyPressed)

        # INIT MENUBAR
        init_menu_bar(self, self.DB_connection)

        # TREEVIEWLIST
        # teams
        teams = self.builder.get_object("treeview_team")
        headers = ["Nombre", "Nombre corto", "Juegos de local", "DT", ""]
        list_model = Gtk.ListStore(str, str, str, str, str)
        columns = ["Team.name", "Team.nick_name", "Team.local_place", "Usr.name", "Usr.last_name"]
        tables = ["Team", "Usr"]
        condition = "Team.id_dt = Usr.id_user"
        data = self.DB_connection.select_tables(tables, columns, condition)
        fill_tree_view_list(headers, data, list_model, teams)

    def onDestroy(self, *args):
        print("OnDestroy")
        Gtk.main_quit()

    def onKeyPressed(self, entry, key_event):
        # print key pressed code
        print(key_event.get_keycode())
        # if key pressed is enter
        if key_event.get_keycode()[1] == 36:
            # start login pressed
            self.on_login_pressed(None)

    def on_button_select_pressed(self, button):
        model, selection = self.builder.get_object("selection_team").get_selected()

        if selection is None:
            return
        # SELECT * FROM Team WHERE name ='selectedname'
        data = self.DB_connection.read("Team", ["*"], "name='{}'".format(model[selection][0]))[0]
        print(data)
        team = Team(id_team=data[0], name=data[1], short_name=data[2], local_place=data[3],
                    id_dt=data[4], goals=data[5], goals_conceded=data[6], win=data[7], lost=data[8], draw=data[9])
        go_to_view_team(self, self.DB_connection, team)

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
            condition = "SELECT id_user FROM Usr WHERE email='{}'".format(user.email)
            data = self.DB_connection.read("Team", ["*"], "id_dt=({})".format(condition))[0]
            print(data)
            team = Team(id_team=data[0], name=data[1], short_name=data[2], local_place=data[3], id_dt=data[4],
                        goals=data[5], goals_conceded=data[6], win=data[7], lost=data[8], draw=data[9])
            go_to_team_manager(self, self.DB_connection, team)

    def on_tournament_changed(self, combo):
        print(combo)
        i = combo.get_active_iter()
        print(combo.get_model()[i][0])


class WViewTeam(Gtk.Window):
    """docstring for WindowMain"""

    def __init__(self, parent=None, DB_connection=None, team=None):
        Gtk.Window.__init__(self)
        self.DB_connection = DB_connection
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

        # LABELS
        self.builder.get_object("label_fullname").set_text(self.team.name)
        self.builder.get_object("label_goals").set_text(str(self.team.goals))
        self.builder.get_object("label_goals_conceded").set_text(str(self.team.goals_conceded))
        self.builder.get_object("label_goalsdifference").set_text(str(self.team.goals - self.team.goals_conceded))
        self.builder.get_object("label_win").set_text(str(self.team.win))
        self.builder.get_object("label_lost").set_text(str(self.team.lost))
        self.builder.get_object("label_draw").set_text(str(self.team.draw))
        self.builder.get_object("label_total").set_text(str(self.team.draw + self.team.lost + self.team.win))
        self.builder.get_object("label_totalpoints").set_text(str(self.team.draw + 3 * self.team.win))

        # TREEVIEWLIST
        headers = ["CURP", "Nombre", "Apellido paterno", "Apellido materno", "Ciudad"]
        data = self.team.get_players(self.DB_connection)
        model = Gtk.ListStore(str, str, str, str, str)
        fill_tree_view_list(headers, data, model, self.builder.get_object("treeview_players"))

        # BUTTONS
        self.builder.get_object("button_back").connect(
            "clicked", lambda button, parent, present:
            go_back(parent, present), self.parent, self)
        self.builder.get_object("button_select").connect("clicked", self.on_button_select_pressed)

    def on_button_select_pressed(self, button):
        model, selection = self.builder.get_object("selection_player").get_selected()
        if selection is None:
            return
        data = self.DB_connection.read("Player", ["*"], "curp='{}'".format(model[selection][0]))[0]

        player = Player(id_player=data[0], name=data[1], last_name=data[2], curp=data[3], city=data[4], suburb=data[5],
                        street=data[6], no=data[7], id_team=data[8], expulsions=data[9], reprimands=data[10],
                        goals=data[11], appearances=data[12], last_last_name=data[13])
        go_to_view_player(self, self.DB_connection, player)

    def onDestroy(self, *args):
        go_back(self.parent, self)


class WViewPlayer(Gtk.Window):
    """docstring for WindowMain"""

    def __init__(self, parent=None, DB_connection=None, player=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        # Setting team info
        self.player = player
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

    def init(self):
        # Reading builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file("view_player.glade")

        # LAYOUT
        self.layout_main = self.builder.get_object("layout_main")
        self.add(self.layout_main)
        # LABELS
        self.builder.get_object("label_fullname").set_text(
            "{} {} {}".format(self.player.name, self.player.last_name, self.player.last_last_name))
        self.builder.get_object("label_teamname").set_text(self.player.get_team(self.DB_connection))
        self.builder.get_object("label_fulladress").set_text(
            "{} {} {}".format(self.player.city, self.player.suburb, self.player.street))
        self.builder.get_object("label_appearences").set_text(str(self.player.appearances))
        self.builder.get_object("label_goals").set_text(str(self.player.goals))
        self.builder.get_object("label_reprimands").set_text(str(self.player.reprimands))
        self.builder.get_object("label_expulsions").set_text(str(self.player.expulsions))

        # BUTTON
        self.builder.get_object("button_back").connect(
            "clicked", lambda button, parent, present:
            go_back(parent, present), self.parent, self)

    def onDestroy(self, *args):
        go_back(self.parent, self)


class WContact(Gtk.Window):
    """docstring for WindowMain"""

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

        self.set_focus(self.builder.get_object("button_login"))

    def init(self):
        # Reading builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file("contact.glade")

        # LAYOUT
        self.layout_main = self.builder.get_object("layout_main")
        self.add(self.layout_main)

        # TREEVIEWLIST
        tree = self.builder.get_object("treeview_contacts")
        headers = ["Nombre", "Apellido paterno", "Apellido materno", "Dirección", "", "", "Teléfono", "e-mail",
                   "Ocupación"]
        data = self.DB_connection.read("Usr",
                                       ["name", "last_name", "last_last_name", "city", "suburb", "street", "phone",
                                        "email", "job"])
        model = Gtk.ListStore(str, str, str, str, str, str, str, str, str)

        for i, usr in enumerate(data):
            if usr[8] == "admin":
                print("ADMIN")
                del data[i]

        fill_tree_view_list(headers, data, model, tree)
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
        headers = ["Nombre", "Apellido paterno", "Apellido materno", "Ciudad", "Usuario", "Contraseña", "Tipo"]
        list_model = Gtk.ListStore(str, str, str, str, str, str, str)
        data = self.DB_connection.read("Usr",
                                       ["name", "last_name", "last_last_name", "city", "email", "password", "job"])
        fill_tree_view_list(headers, data, list_model, users)

        # players
        players = self.builder.get_object("treeview_player")
        headers = ["CURP", "Nombre", "Apellido paterno", "Apellido materno", "Ciudad", "Equipo"]
        list_model = Gtk.ListStore(str, str, str, str, str, str)
        columns = ["Player.curp", "Player.name", "Player.last_name", "Player.last_last_name", "Player.city",
                   "Team.name"]
        tables = ["Player", "Team"]
        condition = "Player.id_team = Team.id_team"
        data = self.DB_connection.select_tables(tables, columns, condition)
        fill_tree_view_list(headers, data, list_model, players)

        # teams
        teams = self.builder.get_object("treeview_team")
        headers = ["ID", "Nombre", "Nombre corto", "Juegos de local", "DT", ""]
        list_model = Gtk.ListStore(int, str, str, str, str, str)
        columns = ["Team.id_team", "Team.name", "Team.nick_name", "Team.local_place", "Usr.name", "Usr.last_name"]
        tables = ["Team", "Usr"]
        condition = "Team.id_dt = Usr.id_user"
        data = self.DB_connection.select_tables(tables, columns, condition)
        fill_tree_view_list(headers, data, list_model, teams)

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
        elif active == "Player":
            model, selection = self.builder.get_object("selection_player").get_selected()

            if selection is None:
                return
            data = self.DB_connection.read("Player",
                                           ["id_player", "last_name", "last_last_name", "name", "curp", "city",
                                            "suburb", "street",
                                            "no"],
                                           "curp='{}'".format(model[selection][0]))[0]
            player = Player(id_player=data[0], last_name=data[1], last_last_name=data[2], name=data[3],
                            curp=data[4], city=data[5], suburb=data[6], street=data[7], no=int(data[8]))
            go_to_add_player(self, self.DB_connection, player)
        elif active == "User":
            # go_to_add_user(self, self.DB_connection)
            model, selection = self.builder.get_object("selection_user").get_selected()
            if selection is None:
                return
            data = self.DB_connection.read("Usr",
                                           ["last_name", "last_last_name", "name", "phone", "city", "suburb", "street",
                                            "no", "email", "password", "job", "id_user"],
                                           "email='{}'".format(model[selection][4]))[0]
            user = User(last_name=data[0], last_last_name=data[1], name=data[2], phone=data[3], city=data[4],
                        suburb=data[5], street=data[6], no=str(data[7]), email=data[8], password=data[9],
                        ocupation=data[10], id_user=data[11])
            go_to_add_user(self, self.DB_connection, user)
        elif active == "Team":
            model, selection = self.builder.get_object("selection_team").get_selected()
            if selection is None:
                return

            data = self.DB_connection.read("Team", ["name", "nick_name", "local_place", "id_team", "id_dt", "goals",
                                                    "goals_conceded", "win", "lost", "draw"],
                                           "id_team={}".format(model[selection][0]))[0]
            team = Team(name=data[0], short_name=data[1], local_place=data[2], id_team=data[3], id_dt=data[4],
                        goals=data[5], goals_conceded=data[6], win=data[7], lost=data[8], draw=data[9])
            data = self.DB_connection.read("Usr",
                                           ["last_name", "last_last_name", "name", "phone", "city", "suburb", "street",
                                            "no", "email", "password", "id_user"], "id_user='{}'".format(data[4]))[0]
            dt = User(last_name=data[0], last_last_name=data[1], name=data[2], phone=data[3], city=data[4],
                      suburb=data[5], street=data[6], no=data[7], email=data[8], password=data[9],
                      id_user=data[10], ocupation="manager", id_league='1')

            go_to_add_team(self, self.DB_connection, team, dt)
            return
        elif active == "Match":
            go_to_add_match(self, self.DB_connection)

    def on_delete_button_pressed(self, button):
        active = self.builder.get_object("stack").get_visible_child().get_name()
        dialog = DialogConfirm(self, "Delete " + active + "?", "¿Está seguro de eliminar?")
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            model, selection = None, None
            if active == "User":
                model, selection = self.builder.get_object("selection_user").get_selected()
                if selection is None:
                    return
                self.DB_connection.delete('Usr', "email='{}'".format(model[selection][4]))
            elif active == "Player":
                model, selection = self.builder.get_object("selection_player").get_selected()
                if selection is None:
                    return
                self.DB_connection.delete('Player', "curp='{}'".format(model[selection][0]))
            elif active == "Team":
                model, selection = self.builder.get_object("selection_team").get_selected()
                if selection is None:
                    return
                # Getting dt id from the team
                dt = self.DB_connection.read("Team", ["id_dt"], "id_team={}".format(model[selection][0]))[0][0]
                # deleting team form db
                self.DB_connection.delete('Team', "id_team='{}'".format(model[selection][0]))
                # Getting email of dt-user
                name = self.DB_connection.read("Usr", ["email"], "id_user={}".format(dt))[0][0]
                # getting model of treeview_user to remove dt
                tmp = self.builder.get_object("treeview_user").get_model()
                # remove dt form db
                self.DB_connection.delete('Usr', "id_user={}".format(dt))
                # remove playersfrom db
                self.DB_connection.delete('Player', "id_team='{}'".format(model[selection][0]))
                # removing dt from treeview
                for sel in tmp:
                    if tmp[sel.iter][4] == name:
                        tmp.remove(sel.iter)
                        break
                tmp = self.builder.get_object("treeview_player").get_model()
                # removing playersfrom treeview
                for sel in tmp:
                    if tmp[sel.iter][5] == model[selection][1]:
                        tmp.remove(sel.iter)

            if model is not None:
                model.remove(selection)
            self.DB_connection.commit()
            print("Delete")
        dialog.destroy()

    def onDestroy(self, *args):
        go_back(self.parent, self)


class WTeamManager(Gtk.Window):
    """docstring for WindowAdminManager"""

    def __init__(self, parent=None, DB_connection=None, team=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        self.DB_connection = DB_connection
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

        self.set_focus(self.builder.get_object("button_back"))

    def init(self):
        # Reading builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file("manager_team.glade")

        # LAYOUT
        self.layout_main = self.builder.get_object("layout_main")
        self.add(self.layout_main)
        # LABELS
        self.builder.get_object("label_fullname").set_text(self.team.name)
        self.builder.get_object("label_goals").set_text(str(self.team.goals))
        self.builder.get_object("label_goals_conceded").set_text(str(self.team.goals_conceded))
        self.builder.get_object("label_goalsdifference").set_text(str(self.team.goals - self.team.goals_conceded))
        self.builder.get_object("label_win").set_text(str(self.team.win))
        self.builder.get_object("label_lost").set_text(str(self.team.lost))
        self.builder.get_object("label_draw").set_text(str(self.team.draw))
        self.builder.get_object("label_total").set_text(str(self.team.draw + self.team.lost + self.team.win))
        self.builder.get_object("label_totalpoints").set_text(str(self.team.draw + 3 * self.team.win))
        # TREEVIEWLIST
        headers = ["CURP", "Nombre", "Apellido paterno", "Apellido materno", "Ciudad"]
        data = self.team.get_players(self.DB_connection)
        model = Gtk.ListStore(str, str, str, str, str)
        fill_tree_view_list(headers, data, model, self.builder.get_object("treeview_player"))

        # BUTTON
        self.builder.get_object("button_back").connect(
            "clicked", lambda button, parent, present:
            go_back(parent, present), self.parent, self)

        self.builder.get_object("button_add").connect("clicked", self.on_add_button_pressed)
        self.builder.get_object("button_modify").connect("clicked", self.on_modify_button_pressed)
        self.builder.get_object("button_delete").connect("clicked", self.on_delete_button_pressed)

    def on_add_button_pressed(self, button):
        go_to_add_player(self, self.DB_connection)

    def on_modify_button_pressed(self, button):
        model, selection = self.builder.get_object("selection_player").get_selected()
        if selection is None:
            return
        data = self.DB_connection.read("Player",
                                       ["id_player", "last_name", "last_last_name", "name", "curp", "city",
                                        "suburb", "street",
                                        "no"],
                                       "curp='{}'".format(model[selection][0]))[0]
        player = Player(id_player=data[0], last_name=data[1], last_last_name=data[2], name=data[3],
                        curp=data[4], city=data[5], suburb=data[6], street=data[7], no=int(data[8]))
        go_to_add_player(self, self.DB_connection, player)

    def on_delete_button_pressed(self, button):
        model, selection = self.builder.get_object("selection_player").get_selected()
        if selection is None:
            return
        dialog = DialogConfirm(self, "Delete?", "¿Está seguro de eliminar al jugador seleccionado?")
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.OK:
            self.DB_connection.delete('Player', "curp='{}'".format(model[selection][0]))
            model.remove(selection)

    def onDestroy(self, *args):
        go_back(self.parent, self)


class WAddTeam(Gtk.Window):
    """docstring for WindowAdminManager"""

    def __init__(self, parent=None, DB_connection=None, team=None, dt=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        self.DB_connection = DB_connection
        self.team = team
        self.dt = dt
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

        if self.team is not None:
            self.builder.get_object("entry_teamname").set_text(self.team.name)
            self.builder.get_object("entry_teamshortname").set_text(self.team.short_name)
            self.builder.get_object("entry_matchplace").set_text(self.team.local_place)
            self.builder.get_object("entry_matchtime").set_text("0")
            self.builder.get_object("entry_name").set_text(self.dt.name)
            self.builder.get_object("entry_lastname").set_text(self.dt.last_name)
            self.builder.get_object("entry_llastname").set_text(self.dt.last_last_name)
            self.builder.get_object("entry_city").set_text(self.dt.city)
            self.builder.get_object("entry_suburb").set_text(self.dt.suburb)
            self.builder.get_object("entry_street").set_text(self.dt.street)
            self.builder.get_object("entry_number").set_text(str(self.dt.no))
            self.builder.get_object("entry_phonenumber").set_text(self.dt.phone)
            self.builder.get_object("entry_email").set_text(self.dt.email)
            self.builder.get_object("entry_password").set_text(self.dt.password)
            self.builder.get_object("entry_password2").set_text(self.dt.password)
            self.builder.get_object("button_add").set_label("Modificar")

    def on_add_button_pressed(self, button):

        teamname = self.builder.get_object("entry_teamname").get_text()
        teamshortname = self.builder.get_object("entry_teamshortname").get_text()
        matchtime = self.builder.get_object("entry_matchtime").get_text()
        matchplace = self.builder.get_object("entry_matchplace").get_text()
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
        if button.get_label() != "Modificar":
            if User(email).valid_user(self.DB_connection):
                DialogOK("El usuario/email ya está registrado.")
                self.builder.get_object("entry_email").set_text("")
                return
            user = User(email=email, password=password, name=name, last_name=last_name, last_last_name=last_last_name,
                        city=city, suburb=suburb, street=street, no=number, phone=phonenumber,
                        ocupation='manager', id_league=1)

            user.add(self.DB_connection)
            team = Team(teamname, teamshortname, matchplace, id_dt=user.id_user)
            team.add(self.DB_connection)
            model = self.parent.builder.get_object("treeview_team").get_model()
            model.append([team.id_team, team.name, team.short_name, team.local_place, user.name, user.last_name])
            model = self.parent.builder.get_object("treeview_user").get_model()
            model.append(
                [user.name, user.last_name, user.last_last_name, user.city, user.email,
                 user.password, user.ocupation])
        else:
            self.dt.name = name
            self.dt.last_name = last_name
            self.dt.last_last_name = last_last_name
            self.dt.password = password
            self.dt.city = city
            self.dt.suburb = suburb
            self.dt.street = street
            self.dt.no = number
            self.dt.phone = phonenumber
            self.dt.id_league = 1
            self.team.name = teamname
            self.team.short_name = teamshortname
            self.team.local_place = matchplace
            self.team.id_dt = self.dt.id_user
            # refreshing team treeview
            model, selection = self.parent.builder.get_object("selection_team").get_selected()
            model[selection][1] = self.team.name
            model[selection][2] = self.team.short_name
            model[selection][3] = self.team.local_place
            model[selection][4] = self.dt.name
            model[selection][5] = self.dt.last_name

            # refreshing user treeview
            model = self.parent.builder.get_object("treeview_user").get_model()
            for sel in model:
                if model[sel.iter][4] == self.dt.email:
                    old = self.dt.email
                    self.dt.email = email
                    self.dt.update(self.DB_connection, old)
                    model[sel.iter][0] = self.dt.name
                    model[sel.iter][1] = self.dt.last_name
                    model[sel.iter][2] = self.dt.last_last_name
                    model[sel.iter][3] = self.dt.city
                    model[sel.iter][4] = self.dt.email
                    model[sel.iter][5] = self.dt.password
                    break
            self.team.update(self.DB_connection)
            DialogOK("Se ha modificado correctamente el equipo y DT.")
            self.onDestroy()
            return

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
            user.ocupation = 'admin'
        elif job == 'DT':
            user.ocupation = 'manager'
        elif job == 'Árbitro':
            user.ocupation = 'referee'

        if button.get_label() == "Modificar":
            old = self.user.email
            self.user.password = password
            self.user.name = name
            self.user.last_name = last_name
            self.user.last_last_name = last_last_name
            self.user.city = city
            self.user.suburb = suburb
            self.user.street = street
            self.user.no = number
            self.user.phone = phonenumber
            self.user.email = email
            DialogOK("Se ha modificado con éxito.")
            model, selection = self.parent.builder.get_object("selection_user").get_selected()
            model[selection][0] = self.user.name
            model[selection][1] = self.user.last_name
            model[selection][2] = self.user.last_last_name
            model[selection][3] = self.user.city
            model[selection][4] = self.user.email
            model[selection][5] = self.user.password
            model[selection][6] = self.user.ocupation
            self.user.update(self.DB_connection, old)
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
            model = self.parent.builder.get_object("treeview_user").get_model()
            model.append(
                [user.name, user.last_name, user.last_last_name, user.city, user.email,
                 user.password, user.ocupation])
        self.onDestroy()

    def onDestroy(self, *args):
        go_back(self.parent, self)


class WAddPlayer(Gtk.Window):
    """docstring for WindowAdminManager"""

    def __init__(self, parent=None, DB_connection=None, player=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.player = player
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

        # Combobox
        combobox_team = self.builder.get_object("combobox_team")
        text_team = self.DB_connection.read("Team", ["nick_name"])
        team_list = Gtk.ListStore(str)
        fill_combo_box(combobox_team, team_list, text_team)

        if self.player is not None:
            self.builder.get_object("entry_last_name").set_text(self.player.last_name)
            self.builder.get_object("entry_last_last_name").set_text(self.player.last_last_name)
            self.builder.get_object("entry_name").set_text(self.player.name)
            self.builder.get_object("entry_curp").set_text(self.player.curp)
            self.builder.get_object("entry_city").set_text(self.player.city)
            self.builder.get_object("entry_suburb").set_text(self.player.suburb)
            self.builder.get_object("entry_street").set_text(self.player.street)
            self.builder.get_object("entry_playernumber").set_text(str(self.player.no))
            self.builder.get_object("combobox_team").set_visible(False)
            self.builder.get_object("button_add").set_label("Modificar")
        if self.parent.__class__ == WTeamManager:
            combobox_team.set_visible(False)

    def _get_entries(self):
        last_name = self.builder.get_object("entry_last_name").get_text()
        last_last_name = self.builder.get_object("entry_last_last_name").get_text()
        name = self.builder.get_object("entry_name").get_text()
        curp = self.builder.get_object("entry_curp").get_text()
        city = self.builder.get_object("entry_city").get_text()
        suburb = self.builder.get_object("entry_suburb").get_text()
        street = self.builder.get_object("entry_street").get_text()
        no = self.builder.get_object("entry_playernumber").get_text()

        return [last_name, last_last_name, name, curp, city, suburb, street, no]

    def on_add_button_pressed(self, button):
        if button.get_label() == "Modificar":
            self.on_modify_button_pressed(None)
            return

        entries = self._get_entries()

        if check_void(entries):
            DialogOK("Debes llenar todos los campos.")
            return
        player = Player(last_name=entries[0], last_last_name=entries[1], name=entries[2], curp=entries[3],
                        city=entries[4], suburb=entries[5],
                        street=entries[6], no=entries[7])

        if player.valid_curp(self.DB_connection):
            DialogOK("El jugador ya está registrado.")
            return

        model = self.builder.get_object("combobox_team").get_model()
        selection = self.builder.get_object("combobox_team").get_active_iter()
        id_team = None
        if self.parent.__class__ == WAdminManager:
            team = model[selection][0]
            id_team = self.DB_connection.read("Team", ["id_team"], "nick_name='{}'".format(team))[0][0]
        else:
            id_team = self.parent.team.id_team

        player.id_team = id_team
        player.add(self.DB_connection)
        DialogOK("Se ha añadido el jugador con éxito.")
        model = self.parent.builder.get_object("treeview_player").get_model()
        if self.parent.__class__ == WAdminManager:
            model.append([player.curp, player.name, player.last_name, player.last_last_name,
                          player.city, team])
        else:
            model.append([player.curp, player.name, player.last_name, player.last_last_name,
                          player.city])
        self.onDestroy()

    def on_modify_button_pressed(self, button):
        entries = self._get_entries()
        if check_void(entries):
            DialogOK("Debes llenar todos los campos.")
            return
        self.player.last_name = entries[0]
        self.player.last_last_name = entries[1]
        self.player.name = entries[2]
        self.player.curp = entries[3]
        self.player.city = entries[4]
        self.player.suburb = entries[5]
        self.player.street = entries[6]
        self.player.no = entries[7]
        self.player.update(self.DB_connection)
        model, selection = self.parent.builder.get_object("selection_player").get_selected()
        model[selection][0] = self.player.curp
        model[selection][1] = self.player.name
        model[selection][2] = self.player.last_name
        model[selection][3] = self.player.last_last_name
        model[selection][4] = self.player.city
        DialogOK("Se ha modificado la información con éxito.")
        self.onDestroy()

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

    def on_modify_button_pressed(self, button):
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
