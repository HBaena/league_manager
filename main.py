#! /usr/bin/python3.6
import db_connection as SQL
import UI
import gi
import glades
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio
from gi.repository.Gdk import Screen
from sys import argv

def gtk_style():
    css_provider = Gtk.CssProvider()
    try:
        css_provider.load_from_path(argv[1]+"/styles.css")
        print("Css loades")
    except Exception as e:
        print(e)


    screen = Screen.get_default()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(
        screen, css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_USER)

print("Connecting to remote db ...")
SQL_CONNECTION = SQL.SQLConnection(
    connection_str="Driver={ODBC Driver 17 for SQL Server};" + "Server=tcp:league-manager.database.windows.net,1433;" +
                   "Database=LeagueManager;Uid=HBaena@league-manager;" + "Pwd={Leaguemanager12345};Encrypt=yes;" +
                   "TrustServerCertificate=no;Connection Timeout=10;")

'''
if SQL_CONNECTION.connection is None:
    del SQL_CONNECTION

SQL_CONNECTION = SQL.SQLConnection(
    None, "localhost", "TeamManager", "sa", "<6DeDiciembre>")
'''

if SQL_CONNECTION.connection is None:
    print("Error to connect to the server.")
    UI.DialogOK("No se ha podido conectar ni localmente ni remotamente a una base de datos.\nRevise sus requerimeinto.")
    Gtk.main()
    exit()
# SQL_CONNECTION = None
window = UI.WMain(SQL_CONNECTION)
# Applying css styles
# Init window
window.present()
# Init gtk bucle

gtk_style()
Gtk.main()
