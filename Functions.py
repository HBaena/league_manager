import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Pango

from UI import WMain, WViewTeam, WViewPlayer, WContact, WAdminManager, WTeamManager, DialogConfirm

def init_menu_bar(parent):
    parent.builder.get_object("menuitem_contact").set_label("Comité")
    parent.builder.get_object("menuitem_contact").connect("activate",
                                                          lambda i, parent : go_to_contact(parent),
                                                          parent)

def add_result():
    builder = Gtk.Builder()
    builder.add_from_file("add_result.glade")

    # LAYOUT
    result = [None, None]
    dialog = builder.get_object("main")
    accept = builder.get_object("button_ok")
    cancel = builder.get_object("button_cancel")
    visit  = builder.get_object("entry_visitgoals")
    local  = builder.get_object("entry_localgoals")
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
    cancel.connect("clicked", lambda button, dialog : dialog.destroy(), dialog)

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
            cell.props.weight     = Pango.Weight.BOLD
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

def go_to_contact(parent):
    parent.set_visible(False)
    parent.set_focus(None)
    contact = WContact(parent)
    contact.present()

def go_to_admin_manager(parent):
    parent.set_visible(False)
    parent.set_focus(None)
    contact = WAdminManager(parent)
    contact.present()

def go_to_team_manager(parent):
    parent.set_visible(False)
    parent.set_focus(None)
    contact = WTeamManager(parent)
    contact.present()

def go_to_view_team(parent):
    parent.set_visible(False)
    parent.set_focus(None)
    contact = WViewTeam(parent)
    contact.present()

def go_to_view_player(parent):
    parent.set_visible(False)
    parent.set_focus(None)
    contact = WViewPlayer(parent)
    contact.present()
