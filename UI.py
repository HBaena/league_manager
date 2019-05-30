import gi
import pandas

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository.Pango import Weight
from gi.repository.Gdk import EventType
from data_structs import *
from datetime import datetime as date


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
    builder.add_from_file("UI/add_result.glade")

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
            cell.props.weight = Weight.BOLD
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


def go_to_add_matches(parent, sql=None):
    transfer(parent, WAddMatches(parent, sql))


def go_to_admin_manager(parent, sql):
    transfer(parent, WAdminManager(parent, sql))


def go_to_referee_manager(parent, sql, referee=None):
    transfer(parent, WRefereeManager(parent, sql, referee))


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
        self.builder.add_from_file("UI/main.glade")

        # LAYOUT
        self.layout_main = self.builder.get_object("layout_main")
        self.add(self.layout_main)
        # DATA
        columns = ["Team.name", "Team.nick_name", "Team.local_place", "Usr.name", "Usr.last_name"]
        tables = ["Team", "Usr"]
        condition = "Team.id_dt = Usr.id_user"
        self.teams = self.DB_connection.select_tables(tables, columns, condition)
        self.tournaments = self.DB_connection.read("Tournament", ["id_tournament, name, season"])

        # COMBOBOX
        combobox_tournament = self.builder.get_object("combobox_tournament")
        text_tournament = [[tournament[1]] for tournament in self.tournaments]
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
        headers = ["Nombre", "Total de juegos", "Juegos ganado", "Juegos empatados", "Juegos perdidos",
                   "Diferencia de goles", "Puntos"]
        list_model = Gtk.ListStore(str, int, int, int, int, int, int)
        self.set_model_to_tree(teams, list_model, headers)
        self.fill_tree_teams(self.tournaments[0][0], list_model)

        # last matches
        matches = self.builder.get_object("treeview_lastresults")
        headers = ["Equipo local", "Equipo visitante", "Lugar", "Fecha", "Hora", "ID"]
        list_model = Gtk.ListStore(str, str, str, str, str, int)
        self.set_model_to_tree(matches, list_model, headers)
        self.fill_tree_last_matches(self.tournaments[0][0])

        matches = self.builder.get_object("treeview_nextmatches")
        headers = ["Equipo local", "Equipo visitante", "Lugar", "Fecha", "Hora", "ID"]
        list_model = Gtk.ListStore(str, str, str, str, str, int)
        self.set_model_to_tree(matches, list_model, headers)
        self.fill_tree_next_matches(self.tournaments[0][0])

    def fill_tree_next_matches(self, id_tournament):
        matches = self.builder.get_object("treeview_nextmatches")
        local = self.DB_connection.select_tables(["Team", "Match", "Usr"],
                                                 ["TOP 20 Team.name", "Team.id_team", "id_match", "Match.match_date"],
                                                 "Team.id_team=Match.id_local and Match.checked=0 and id_day={} ORDER BY Match.match_date DESC".format(
                                                     id_tournament))
        visit = self.DB_connection.select_tables(["Team", "Match", "Usr"],
                                                 ["TOP 20 Team.name", "Team.id_team", "id_match", "Match.match_date"],
                                                 "Team.id_team=Match.id_visit and Match.checked=0 and id_day={} ORDER BY Match.match_date DESC".format(
                                                     id_tournament))

        match_info = self.DB_connection.select_tables(["Match", "Usr"],
                                                      ["TOP 20 Match.place", "Match.match_date", "Match.hour",
                                                       "Match.id_match", "Match.match_date"],
                                                      "Match.checked=0 and id_day={} ORDER BY Match.match_date DESC".format(
                                                          id_tournament))
        matches.get_model().clear()
        if local is None:
            return

        for i in range(len(local)):
            tmp = [local[i][0], visit[i][0], match_info[i][0],
                   str(match_info[i][1]), str(match_info[i][2]), match_info[i][3]]
            matches.get_model().append(tmp)

    def fill_tree_last_matches(self, id_tournament):
        matches = self.builder.get_object("treeview_lastresults")
        local = self.DB_connection.select_tables(["Team", "Match", "Usr"],
                                                 ["TOP 20 Team.name", "Team.id_team", "id_match", "Match.match_date"],
                                                 "Team.id_team=Match.id_local and Match.checked=1 and id_day={} ORDER BY Match.match_date DESC".format(
                                                     id_tournament))
        visit = self.DB_connection.select_tables(["Team", "Match", "Usr"],
                                                 ["TOP 20 Team.name", "Team.id_team", "id_match", "Match.match_date"],
                                                 "Team.id_team=Match.id_visit and Match.checked=1 and id_day={} ORDER BY Match.match_date DESC".format(
                                                     id_tournament))

        match_info = self.DB_connection.select_tables(["Match", "Usr"],
                                                      ["TOP 20 Match.place", "Match.match_date", "Match.hour",
                                                       "Match.id_match", "Match.match_date"],
                                                      "Match.checked=1 and id_day={} ORDER BY Match.match_date DESC".format(
                                                          id_tournament))
        data = []
        matches.get_model().clear()
        if local is None:
            return

        for i in range(len(local)):
            tmp = [local[i][0], visit[i][0], match_info[i][0],
                   str(match_info[i][1]), str(match_info[i][2]), match_info[i][3]]
            matches.get_model().append(tmp)

    def fill_tree_teams(self, id, tree):
        names = self.DB_connection.read("Team, DetailTournament", ["Team.name"],
                                        "DetailTournament.id_team=Team.id_team and DetailTournament.id_tournament={}".format(
                                            id))
        statistics = self.DB_connection.read("DetailTournament",
                                             ["win+draw+lost, win, draw, lost, goals - goals_conceded, win*3 + draw"],
                                             "DetailTournament.id_tournament={}".format(id))
        data = []
        for i in range(len(names)):
            row = []
            row.append(names[i][0])
            row.append(statistics[i][0])
            row.append(statistics[i][1])
            row.append(statistics[i][2])
            row.append(statistics[i][3])
            row.append(statistics[i][4])
            row.append(statistics[i][5])
            data.append(row)
        tree.clear()
        for row in data:
            tree.append(row)

    def set_model_to_tree(self, tree, model, headers):
        tree.set_model(model)
        for i, column in enumerate(headers):
            cell = Gtk.CellRendererText()
            if i == 0:
                # Headers
                cell.props.weight_set = True
                cell.props.weight = Weight.BOLD
            # Column
            col = Gtk.TreeViewColumn(column, cell, text=i)
            # Append column
            tree.append_column(col)

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
        id_tournament = self.DB_connection.read("Tournament", ["id_tournament"], "name='{}'".format(
            self.builder.get_object("combobox_tournament").get_model()[
                self.builder.get_object("combobox_tournament").get_active_iter()][0]))[0][0]
        model, selection = self.builder.get_object("selection_team").get_selected()
        team_data = self.DB_connection.read("Team", ["id_team, name, nick_name, local_place, id_dt"],
                                            "name='{}'".format(model[selection][0]))[0]
        statistics = self.DB_connection.read("DetailTournament", ["win, lost, draw, goals, goals_conceded"],
                                             "id_team={} and id_tournament={}".format(team_data[0], id_tournament))[0]
        team = Team(id_team=team_data[0], name=team_data[1], short_name=team_data[2], local_place=team_data[3],
                    id_dt=team_data[4], goals=statistics[0], goals_conceded=statistics[1], win=statistics[2],
                    lost=statistics[3], draw=statistics[4])
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
            go_to_referee_manager(self, self.DB_connection, user)
        elif user.ocupation == 'manager':
            id_tournament = self.DB_connection.read("Tournament", ["id_tournament"], "name='{}'".format(
                self.builder.get_object("combobox_tournament").get_model()[
                    self.builder.get_object("combobox_tournament").get_active_iter()][0]))[0][0]
            model, selection = self.builder.get_object("selection_team").get_selected()
            team_data = self.DB_connection.read("Team", ["id_team, name, nick_name, local_place, id_dt"],
                                                "name='{}'".format(model[selection][0]))[0]
            statistics = self.DB_connection.read("DetailTournament", ["win, lost, draw, goals, goals_conceded"],
                                                 "id_team={} and id_tournament={}".format(team_data[0], id_tournament))[
                0]
            team = Team(id_team=team_data[0], name=team_data[1], short_name=team_data[2], local_place=team_data[3],
                        id_dt=team_data[4], goals=statistics[0], goals_conceded=statistics[1], win=statistics[2],
                        lost=statistics[3], draw=statistics[4])

            go_to_team_manager(self, self.DB_connection, team)

    def on_tournament_changed(self, combo):
        i = combo.get_active()
        id = self.tournaments[i][0]
        print("id", id)
        self.fill_tree_teams(id, self.builder.get_object("treeview_team").get_model())
        self.fill_tree_last_matches(id)
        self.fill_tree_next_matches(id)


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
        self.builder.add_from_file("UI/view_team.glade")

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
        self.builder.add_from_file("UI/view_player.glade")

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
        self.builder.add_from_file("UI/contact.glade")

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
        self.builder.add_from_file("UI/admin_manager.glade")

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
        # Tournaments
        tournaments = self.builder.get_object("treeview_tournament")
        headers = ["ID", "NOMBRE", "TEMPORADA"]
        list_model = Gtk.ListStore(int, str, str)
        data = self.DB_connection.read("Tournament", ["id_tournament", "name", "season"])
        fill_tree_view_list(headers, data, list_model, tournaments)
        # Matches
        local = self.DB_connection.select_tables_no_distinct(["Team", "Match"], ["Team.name"],
                                                             "Team.id_team=Match.id_local")
        print("Local:", len(local))
        visit = self.DB_connection.select_tables_no_distinct(["Team", "Match"], ["Team.name"],
                                                             "Team.id_team=Match.id_visit")
        print("Visit:", len(visit))
        referee = self.DB_connection.select_tables_no_distinct(["Usr", "Match"], ["Usr.name", "Usr.last_name"],
                                                               "Usr.id_user=Match.idreferee")
        print("Referee:", len(referee))
        match_info = self.DB_connection.read("Match", ["place", "match_date", "hour", "goals_local", "goals_visit"])
        print("Match info:", len(match_info))
        tournament = self.DB_connection.select_tables_no_distinct(["Tournament", "Match"], ["Tournament.name"],
                                                                  "Match.id_day=Tournament.id_tournament")
        print("local: ", len(local))
        print("visit: ", len(visit))
        print("referee: ", len(referee))
        print("tournament: ", len(tournament))
        data = []
        for i in range(len(local)):
            tmp = [tournament[i][0], local[i][0], visit[i][0], match_info[i][0],
                   str(match_info[i][1]), str(match_info[i][2]), match_info[i][3],
                   match_info[i][4], referee[i][0], referee[i][1]]
            data.append(tmp)
        matches = self.builder.get_object("treeview_match")
        headers = ["Torneo", "Equipo local", "Equipo visitante", "Lugar", "Fecha", "Hora", "Goles local",
                   "Goles visitante", "Árbitro", ""]
        list_model = Gtk.ListStore(str, str, str, str, str, str, int, int, str, str)
        fill_tree_view_list(headers, data, list_model, matches)

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
            DialogOK("Por cuestiones de seguridad los partidos una vez\n añadidos no se pueden eliminar ni modificar.")

    def on_delete_button_pressed(self, button):

        active = self.builder.get_object("stack").get_visible_child().get_name()
        if active == "Match":
            DialogOK("Por cuestiones de seguridad los partidos una vez\n añadidos no se pueden eliminar ni modificar.")
            return
        elif active == "Tournament":
            DialogOK("Por cuestiones de seguridad los partidos una vez\n añadidos no se pueden eliminar ni modificar.")
            return

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
        self.builder.add_from_file("UI/manager_team.glade")

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
        self.builder.add_from_file("UI/add_team.glade")

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
        self.builder.add_from_file("UI/add_user.glade")

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
        self.builder.add_from_file("UI/add_player.glade")

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
        self.builder.add_from_file("UI/add_tournament.glade")

        # LAYOUT
        self.layout_main = self.builder.get_object("layout_main")
        self.add(self.layout_main)

        # TREEVIEW
        teams = self.builder.get_object("treeview_teams")
        data = self.DB_connection.read("Team", ["id_team, name, nick_name"])
        list_model = Gtk.ListStore(int, str, str, bool)
        teams.set_model(list_model)
        # adding text columns teams
        renderer_text = Gtk.CellRendererText()
        renderer_text.set_alignment(0.1, 0.5)
        column_text = Gtk.TreeViewColumn("ID", renderer_text, text=0)
        teams.append_column(column_text)
        renderer_text = Gtk.CellRendererText()
        renderer_text.set_alignment(0.5, 0.5)
        column_text = Gtk.TreeViewColumn("Nombre", renderer_text, text=1)
        teams.append_column(column_text)
        renderer_text = Gtk.CellRendererText()
        renderer_text.set_alignment(0.5, 0.5)
        column_text = Gtk.TreeViewColumn("Nombre corto", renderer_text, text=2)
        teams.append_column(column_text)
        # Adding toggle columns to teams
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.set_alignment(0.1, 0.5)
        renderer_toggle.connect("toggled", self.on_toggled_button, list_model, 3)
        column_toggle = Gtk.TreeViewColumn("¿Jugará en el torneo?", renderer_toggle, active=3)
        teams.append_column(column_toggle)

        for team in data:
            row = [int(team[0]), team[1], team[2], False]
            list_model.append(row)

        # BUTTON
        self.builder.get_object("button_back").connect(
            "clicked", lambda button, parent, present:
            go_back(parent, present), self.parent, self)

        self.builder.get_object("button_add").connect("clicked", self.on_add_button_pressed)

    @staticmethod
    def on_toggled_button(self, path, model, pos):
        model[path][pos] = not model[path][pos]

    def on_add_button_pressed(self, button):
        name = self.builder.get_object("entry_name").get_text()
        season = self.builder.get_object("entry_season").get_text()

        if check_void([name, season]):
            DialogOK("Todos los campos son requeridos.")
            return

        dialog = DialogConfirm(self, "Agregar torneo", "¿Está seguro de agregar el torneo?")
        response = dialog.run()
        dialog.destroy()
        if response != Gtk.ResponseType.OK:
            return

        model = self.builder.get_object("treeview_teams").get_model()
        count_teams = 0
        for row in model:
            count_teams += int(row[3])
        if count_teams == 0:
            DialogOK("No se ha agregado ningún equipo.")
            return
        elif count_teams < 0:
            DialogOK("Se han agregado demasiado pocos equipos.")
            return

        tournament = Tournament(name, season)
        tournament.add(self.DB_connection)
        for row in model:
            if row[3] is True:
                detail = DetailTournament(tournament.id_tournament, int(row[0]))
                detail.add(self.DB_connection)
                del detail
        DialogOK("Se ha agregado correctamente el torneo.")
        self.onDestroy()
        self.parent.builder.get_object("treeview_tournament").get_model().append(
            [tournament.id_tournament, name, season])

    def onDestroy(self, *args):
        go_back(self.parent, self)


class WRefereeManager(Gtk.Window):
    """docstring for WindowAdminManager"""

    def __init__(self, parent=None, DB_connection=None, referee=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        self.DB_connection = DB_connection
        self.referee = referee
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
        self.builder.add_from_file("UI/referee_manager.glade")

        # LAYOUT
        self.layout_main = self.builder.get_object("layout_main")
        self.add(self.layout_main)

        # BUTTON
        self.builder.get_object("button_back").connect(
            "clicked", lambda button, parent, present:
            go_back(parent, present), self.parent, self)

        self.referee.id_user = self.DB_connection.read("Usr", ["id_user"], "email='{}'".format(self.referee.email))[0][
            0]
        # TREEVIEW
        today = date.now()

        print(str(today), str(today.strftime("%X")))
        local = self.DB_connection.select_tables(["Team", "Match", "Usr"], ["Team.name", "Team.id_team", "id_match"],
                                                 "Team.id_team=Match.id_local and Match.idreferee='{}' and Match.checked=0".format(
                                                     self.referee.id_user))
        visit = self.DB_connection.select_tables(["Team", "Match", "Usr"], ["Team.name", "Team.id_team", "id_match"],
                                                 "Team.id_team=Match.id_visit and Match.idreferee='{}' and Match.checked=0".format(
                                                     self.referee.id_user))
        match_info = self.DB_connection.select_tables(["Match", "Usr"],
                                                      ["Match.place", "Match.match_date", "Match.hour",
                                                       "Match.id_match"],
                                                      "Match.idreferee='{}' and Match.checked=0".format(
                                                          self.referee.id_user))
        data = []
        teams = []
        self.teams = {}

        if local is None:
            return
        for i in range(len(local)):
            tmp = [local[i][0], visit[i][0], match_info[i][0],
                   str(match_info[i][1]), str(match_info[i][2]), match_info[i][3]]
            data.append(tmp)
            teams.append(local[i][1])
            teams.append(visit[i][1])
            self.teams[local[i][0]] = local[i][1]
            self.teams[visit[i][0]] = visit[i][1]
        matches = self.builder.get_object("treeview_match")
        headers = ["Equipo local", "Equipo visitante", "Lugar", "Fecha", "Hora", "ID"]
        list_model = Gtk.ListStore(str, str, str, str, str, int)
        fill_tree_view_list(headers, data, list_model, matches)
        self.builder.get_object("selection_match").connect("changed", self.on_row_changed)
        teams = list(set(teams))
        self.players = {}
        for team in teams:
            self.players[team] = self.DB_connection.read("Player", ["name", "last_name", "last_last_name"],
                                                         "id_team='{}'".format(team))

        treeview_local = self.builder.get_object("treeview_local")
        local_model = Gtk.ListStore(str, str, str, bool, int, bool, bool)
        treeview_local.set_model(local_model)
        treeview_visit = self.builder.get_object("treeview_visit")
        visit_model = Gtk.ListStore(str, str, str, bool, int, bool, bool)
        treeview_visit.set_model(visit_model)
        # Adding name columns to local
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Nombre", renderer_text, text=0)
        treeview_local.append_column(column_text)

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Apellido paterno", renderer_text, text=1)
        treeview_local.append_column(column_text)

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Apellido materno", renderer_text, text=2)
        treeview_local.append_column(column_text)
        # Adding name columns to local
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Nombre", renderer_text, text=0)
        treeview_visit.append_column(column_text)

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Apellido paterno", renderer_text, text=1)
        treeview_visit.append_column(column_text)

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Apellido materno", renderer_text, text=2)
        treeview_visit.append_column(column_text)

        # Adding toggle columns to local
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_toggled_button, local_model, 3)
        column_toggle = Gtk.TreeViewColumn("¿Jugó?", renderer_toggle, active=3)
        treeview_local.append_column(column_toggle)

        renderer_text = Gtk.CellRendererText(editable=True)
        renderer_text.connect("edited", self.on_text_edited, local_model)
        column_text = Gtk.TreeViewColumn("Anotaciones", renderer_text, text=4)
        treeview_local.append_column(column_text)

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_toggled_button, local_model, 5)
        column_toggle = Gtk.TreeViewColumn("Amonestación", renderer_toggle, active=5)
        treeview_local.append_column(column_toggle)

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_toggled_button, local_model, 6)
        column_toggle = Gtk.TreeViewColumn("Expulsión", renderer_toggle, active=6)
        treeview_local.append_column(column_toggle)
        # Adding toggle columns to visit
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_toggled_button, visit_model, 3)
        column_toggle = Gtk.TreeViewColumn("¿Jugó?", renderer_toggle, active=3)
        treeview_visit.append_column(column_toggle)

        renderer_text = Gtk.CellRendererText(editable=True)
        renderer_text.connect("edited", self.on_text_edited, visit_model)
        column_text = Gtk.TreeViewColumn("Anotaciones", renderer_text, text=4)
        treeview_visit.append_column(column_text)

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_toggled_button, visit_model, 5)
        column_toggle = Gtk.TreeViewColumn("Amonestación", renderer_toggle, active=5)
        treeview_visit.append_column(column_toggle)

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_toggled_button, visit_model, 6)
        column_toggle = Gtk.TreeViewColumn("Expulsión", renderer_toggle, active=6)
        treeview_visit.append_column(column_toggle)

        self.builder.get_object("button_add_result").connect("clicked", self.on_add_button_pressed, local_model,
                                                             visit_model)

    @staticmethod
    def on_text_edited(self, path, text, model):
        try:
            model[path][4] = int(text)
        except:
            DialogOK("Sólo números enteros.")

    @staticmethod
    def on_toggled_button(self, path, model, pos):
        if model[path][pos] is True:
            model[path][pos] = False
        else:
            model[path][pos] = True

    def on_row_changed(self, row):
        model, selection = row.get_selected()
        if selection is None:
            return
        local = self.teams[model[selection][0]]
        visit = self.teams[model[selection][1]]
        print(local, visit)
        treeview_local = self.builder.get_object("treeview_local")
        treeview_visit = self.builder.get_object("treeview_visit")

        treeview_local.get_model().clear()
        treeview_visit.get_model().clear()
        for player in self.players[local]:
            tmp = []
            # name
            tmp.append(player[0])
            # last name
            tmp.append(player[1])
            # last last name
            tmp.append(player[2])
            tmp.append(False)
            tmp.append(0)
            tmp.append(False)
            tmp.append(False)
            treeview_local.get_model().append(tmp)

        for player in self.players[visit]:
            tmp = []
            print(player)
            # name
            tmp.append(player[0])
            # last name
            tmp.append(player[1])
            # last last name
            tmp.append(player[2])
            tmp.append(False)
            tmp.append(0)
            tmp.append(False)
            tmp.append(False)
            treeview_visit.get_model().append(tmp)

            treeview_local.show_all()
            treeview_visit.show_all()

    def on_add_button_pressed(self, button, model_local, model_visit):

        local_appearences = 0
        local_goals = 0
        for row in model_local:
            if row[3]:
                local_appearences += 1
            local_goals += row[4]

        visit_appearences = 0
        visit_goals = 0
        for row in model_visit:
            if row[3]:
                visit_appearences += 1
            visit_goals += row[4]

        dialog = None
        tmp = 0
        if local_appearences < 7 and visit_appearences < 7:
            dialog = DialogConfirm(self, title="¿Desea agregar el resultado?",
                                   text_content="Una vez agregado el resultado, la información no podrá ser modificada.\n" +
                                                "Los equipos tienen menos de 7 jugadores seleccionados,\n" +
                                                "ningún equipo sumaría puntos.")
            tmp = 1
        elif local_appearences < 7:
            dialog = DialogConfirm(self, title="¿Desea agregar el resultado?",
                                   text_content="Una vez agregado el resultado, la información no podrá ser modificada.\n" +
                                                "El equipo local tiene menos de 7 jugadores seleccionados,\n" +
                                                "el equipo pierde 0 - 3 por default.")
            tmp = 2
        elif visit_appearences < 7:
            dialog = DialogConfirm(self, title="¿Desea agregar el resultado?",
                                   text_content="Una vez agregado el resultado, la información no podrá ser modificada.\n" +
                                                "El equipo visitante tiene menos de 7 jugadores seleccionados,\n" +
                                                "el equipo pierde 3 - 0 por default.")
            tmp = 3
        else:
            dialog = DialogConfirm(self, title="¿Desea agregar el resultado?",
                                   text_content="Una vez agregado el resultado, la información no podrá ser modificada.\n" +
                                                "El marcador es: " + str(local_goals) + " - " + str(visit_goals))

        response = dialog.run()
        dialog.destroy()

        if response != Gtk.ResponseType.OK:
            return

        model, selection = self.builder.get_object("selection_match").get_selected()
        id_local = self.teams[model[selection][0]]
        id_visit = self.teams[model[selection][1]]
        id_tournament = model[selection][5]
        print("Id_local", id_local)
        print("id_visit", id_visit)
        if tmp == 0:
            # local players
            for row in model_local:
                if row[3]:
                    player = Player(name=row[0], last_name=row[1], last_last_name=row[2])
                    player.update_statistics(self.DB_connection, int(row[3]), int(row[4]), int(row[5]), int(row[6]))
                    del player
            # visit players
            for row in model_local:
                if row[3]:
                    player = Player(name=row[0], last_name=row[1], last_last_name=row[2])
                    player.update_statistics(self.DB_connection, int(row[3]), int(row[4]), int(row[5]), int(row[6]))
                    del player
            # local
            team = Team(id_team=id_local)
            team.update_statistics(self.DB_connection, id_tournament, local_goals, visit_goals,
                                   int(local_goals > visit_goals),
                                   int(local_goals < visit_goals), int(local_goals == visit_goals))
            # visit
            team = Team(id_team=id_visit)
            team.update_statistics(self.DB_connection, id_tournament, visit_goals, local_goals,
                                   int(visit_goals > local_goals),
                                   int(visit_goals < local_goals), int(visit_goals == local_goals))

        elif tmp == 3:
            # local
            team = Team(id_team=id_local)
            team.update_statistics(self.DB_connection, id_tournament, 3, 0, 1, 0, 0)

        elif tmp == 2:
            # visit
            team = Team(id_team=id_visit)
            team.update_statistics(self.DB_connection, id_tournament, 3, 0, 1, 0, 0)

        DialogOK("Los cambios han sido guardados.")

        self.DB_connection.query(
            "UPDATE Match SET checked=1, " +
            "goals_local={}, goals_visit={} WHERE id_match={}".format(local_goals, visit_goals, model[selection][5]))

        model.remove(selection)
        self.builder.get_object("treeview_local").get_model().clear()
        self.builder.get_object("treeview_visit").get_model().clear()

    def onDestroy(self, *args):
        go_back(self.parent, self)


class WAddMatch(Gtk.Window):
    """docstring for WindowAdminManager"""

    def __init__(self, parent=None, DB_connection=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        self.DB_connection = DB_connection
        self.matches = []
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
        self.builder.add_from_file("UI/add_match.glade")

        # LAYOUT
        self.layout_main = self.builder.get_object("layout_main")
        self.add(self.layout_main)

        # BUTTON
        self.builder.get_object("button_back").connect(
            "clicked", lambda button, parent, present:
            go_back(parent, present), self.parent, self)
        self.builder.get_object("button_add_match").connect("clicked", self.on_add_button_pressed)
        self.builder.get_object("button_help").connect("clicked", lambda button: DialogOK(
            "De click derecho sobre el botón \npara desplegar la ayuda sobre su función."))
        self.builder.get_object("button_add_matches").connect("clicked",
                                                              lambda widget, parent, sql: go_to_add_matches(parent,
                                                                                                            sql), self,
                                                              self.DB_connection)
        self.builder.get_object("button_finish").connect("clicked", self.on_finish_button_pressed)

        # Calendar
        self.builder.get_object("calendar_date").select_day(date.now().day)
        self.builder.get_object("calendar_date").select_month(date.now().month, date.now().year)

        #  combobox
        text_team = self.DB_connection.read("Team", ["nick_name"])
        combobox_team = self.builder.get_object("combobox_local")
        team_list = Gtk.ListStore(str)
        fill_combo_box(combobox_team, team_list, text_team)
        combobox_team = self.builder.get_object("combobox_visit")
        team_list = Gtk.ListStore(str)
        fill_combo_box(combobox_team, team_list, text_team)
        combobox_tournament = self.builder.get_object("combobox_tournament")
        league = League(1)
        text_tournament = league.get_tournaments(self.DB_connection)
        tournament_list = Gtk.ListStore(str)
        fill_combo_box(combobox_tournament, tournament_list, text_tournament)
        combobox_referee = self.builder.get_object("combobox_referee")
        data = self.DB_connection.read("Usr", ["name", "last_name"], "job='referee'")
        referee_list = Gtk.ListStore(str, str)
        fill_combo_box(combobox_referee, referee_list, data)
        # treeview
        tree = self.builder.get_object("treeview_matches")
        headers = ["LUGAR", "DIA", "HORA", "LOCAL", "VISITANTE", "ARBITRO", "TORNEO"]
        model = Gtk.ListStore(str, str, str, int, int, int, int)
        data = []
        fill_tree_view_list(headers, data, model, tree)

        '''
            POPOVERS
            HELP
        '''
        # popover de cada button
        popover = self.builder.get_object("popover_add_match")
        button = self.builder.get_object("button_add_match")
        popover.set_relative_to(button)
        popover.set_modal(True)
        button.connect("event", self.on_event, popover)

        popover = self.builder.get_object("popover_finish")
        button = self.builder.get_object("button_finish")
        popover.set_relative_to(button)
        popover.set_modal(True)
        button.connect("event", self.on_event, popover)

        popover = self.builder.get_object("popover_add_matches")
        button = self.builder.get_object("button_add_matches")
        popover.set_relative_to(button)
        popover.set_modal(True)
        button.connect("event", self.on_event, popover)

    def on_event(self, widget, event, popover):
        # doc(event)
        MOUSE_RIGHT = 3
        if event.type == EventType.BUTTON_PRESS and event.get_button()[1] == MOUSE_RIGHT:
            popover.popup()

    def on_finish_button_pressed(self, button):
        dialog = DialogConfirm(self, "Agregar partidos", "¿Ha terminado de agregar partidos?")
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.OK:
            for match in self.matches:
                match.add(self.DB_connection)
            self.onDestroy()

    def on_add_button_pressed(self, button):
        date = self.builder.get_object("calendar_date").get_date()
        date = str(date[0]) + '/' + str(date[1]) + '/' + str(date[2])
        # time
        time = self.builder.get_object("entry_time")
        # place
        place = self.builder.get_object("entry_place")
        combo = self.builder.get_object("combobox_tournament")
        i = combo.get_active_iter()
        tournament = combo.get_model()[i][0]
        combo = self.builder.get_object("combobox_local")
        i = combo.get_active_iter()
        local = combo.get_model()[i][0]
        combo = self.builder.get_object("combobox_visit")
        i = combo.get_active_iter()
        visit = combo.get_model()[i][0]
        combo = self.builder.get_object("combobox_referee")
        i = combo.get_active_iter()
        referee = [combo.get_model()[i][0], combo.get_model()[i][1]]

        if check_void([time, place]):
            DialogOK("Todos los campos son requeridos.")
            return

        if local == visit:
            DialogOK("Debe elegir diferentes equipos.")
            return

        # id_tournament
        id_tournament = self.DB_connection.read("Tournament", ["id_tournament"], "name='{}'".format(tournament))[0]
        # id_local
        id_local = self.DB_connection.read("Team", ["id_team"], "nick_name='{}'".format(local))[0]
        # id_visit
        id_visit = self.DB_connection.read("Team", ["id_team"], "nick_name='{}'".format(visit))[0]
        # id_referee
        id_referee = self.DB_connection.read("Usr", ["id_user"],
                                             "job='referee' and name='{}' and last_name='{}'".format(referee[0],
                                                                                                     referee[1]))[0]
        match = Match(place=place, match_date=date, hour=time, id_local=id_local, id_visit=id_visit,
                      id_day=id_tournament,
                      id_referee=id_referee)
        dialog = DialogConfirm(self, "¿Agregar partido?", "¿Está seguro de agregar el partido?")
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            headers = ["LUGAR", "DIA", "HORA", "LOCAL", "VISITANTE", "ARBITRO", "TORNEO"]

            row = [place, date, time, local, visit, referee, tournament]
            self.builder.get_object("treeview_matches").get_model().append(row)
            self.matches.append(match)
            DialogOK("Se ha añadido el encuentro.")

    def onDestroy(self, *args):
        go_back(self.parent, self)


class WAddMatches(Gtk.Window):
    """docstring for WindowMain"""

    def __init__(self, parent=None, DB_connection=None):
        Gtk.Window.__init__(self)
        # Setting parent window
        self.parent = parent
        self.DB_connection = DB_connection
        self.matches = []
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
        self.builder.add_from_file("UI/add_matches.glade")

        # LAYOUT
        self.layout_main = self.builder.get_object("layout_main")
        self.add(self.layout_main)
        # treeviewlist
        tree = self.builder.get_object("treeview_matches")
        headers = ["LUGAR", "DIA", "HORA", "ID LOCAL", "ID VISITANTE", "ID ARBITRO", "ID TORNEO"]
        model = Gtk.ListStore(str, str, str, int, int, int, int)
        data = []
        fill_tree_view_list(headers, data, model, tree)

        # BUTTON
        self.builder.get_object("button_back").connect(
            "clicked", lambda button, parent, present:
            go_back(parent, present), self.parent, self)
        self.builder.get_object("filebutton_matches").connect("file-set", self.on_file_choose)
        self.builder.get_object("button_add").connect("clicked", self.on_button_add_pressed)
        self.builder.get_object("button_help").connect("clicked", self.on_help_button_pressed)

    def on_help_button_pressed(self, button):
        dialog = self.builder.get_object("dialog_help")
        button = self.builder.get_object("button_ok")
        button.connect("clicked", lambda button, parent: parent.close(), dialog)
        dialog.add_button("OK", 10)
        dialog.run()
        dialog.destroy()

    def on_button_add_pressed(self, button):
        dialog = DialogConfirm(self, "Agregar la jornada", "¿Está seguro de agregar la jornada?")
        response = dialog.run()
        dialog.destroy()
        if response != Gtk.ResponseType.OK:
            return;
        if self.matches == []:
            DialogOK("No se han agregado encuentros aún.")
            return
        try:
            for match in self.matches:
                match.add(self.DB_connection)
        except Exception as e:
            print(e)
            DialogOK("Ha ocurrido un problema.")
            return
        DialogOK("Se han añadido con éxito")
        self.onDestroy()

    def on_file_choose(self, widget):
        d = []
        self.matches = []
        try:
            data = pandas.read_excel(widget.get_filename())

            self.matches = []
            for i in data.index:
                place = (str(data["LUGAR"][i]))
                date = (str(data["DIA"][i].date()))
                hour = (str(data["HORA"][i]))
                id_local = (int(data["ID LOCAL"][i]))
                id_visit = (int(data["ID VISITANTE"][i]))
                id_referee = (int(data["ID ARBITRO"][i]))
                id_tournament = (int(data["ID TORNEO"][i]))
                match = Match(place=place, match_date=date, hour=hour, id_local=id_local,
                              id_visit=id_visit, id_referee=id_referee, id_day=id_tournament)
                self.matches.append(match)
                d.append([place, date, hour, id_local, id_visit, id_referee, id_tournament])

        except Exception as e:
            print(e)
            DialogOK("Parece ser que el archivo no cumple con\n las características para el programa.")
            return
        model = self.builder.get_object("treeview_matches").get_model()
        model.clear()
        for row in d:
            model.append(row)
        DialogOK("Se ha podido leer correctamente el documento")

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
