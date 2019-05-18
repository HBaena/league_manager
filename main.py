import db_connection as SQL
import UI
import gi
import requests
from zeep import Client

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

'''
SQL_CONNECTION = SQL.SQLConnection(
    connection_str="Driver={ODBC Driver 17 for SQL Server};" + "Server=tcp:league-manager.database.windows.net,1433;" +
                   "Database=LeagueManager;Uid=HBaena@league-manager;" + "Pwd={Leaguemanager12345};Encrypt=yes;" +
                   "TrustServerCertificate=no;Connection Timeout=10;")
SQL_CONNECTION.connection = SQL
if SQL_CONNECTION.connection is None:
    del SQL_CONNECTION
'''
SQL_CONNECTION = SQL.SQLConnection(
    None, "localhost", "TeamManager", "sa", "<6DeDiciembre>")

if SQL_CONNECTION is None:
    print("Error to connect to the server.")
    exit()


def gtk_style():
    css_provider = Gtk.CssProvider()
    css_provider.load_from_path('styles.css')

    screen = Gdk.Screen.get_default()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(
        screen, css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_USER)


window = UI.WMain(SQL_CONNECTION)
# Applying css styles
gtk_style()
# Init window
window.present()
# Init gtk bucle
Gtk.main()
