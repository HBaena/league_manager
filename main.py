import local_connection as SQL
import UI
import gi
import requests
from zeep import Client
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

pwd = "<6DeDiciembre>"
SQL_CONNECTION = SQL.SQLConnection(
    None, "localhost", "TeamManager", "sa", pwd)

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