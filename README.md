# Manual de instalación
## Linux (Basados en DEBIAN)
#### Depependencias de python
```bash
sudo apt install python3 python3-pip
```
#### ODBC Driver 13.1 for SQL Server
```bash
sudo apt install msodbcsql17
```
o en [la página oficial de Windows](https://www.microsoft.com/en-us/download/details.aspx?id=53339)
#### Git
```bash
sudo apt install git
```

#### Clonación del repositorio
En la ruta de ru preferencia ...

```bash
git clone "https://github.com/HBaena/league_manager.git"
pip3 install gobject pandas pyodbc --user
mv league_manager ~
cd ~/league_manager
chmod a+x main.py
```
Ahora, para crear el lanzador
```bash
pwd
```
Copia la salida que será la ruta absoluta del directorio donde se encuentra nuestro progarama.
Abre league_manager.desktop con tu editor de texto de preferencia.

```bash
subl league_manager.dektop
vi league_manager.dektop
nano league_manager.dektop
gedit league_manager.dektop
```
Sustituye FULL_PATH por la ruta que copiaste antes.

```
[Desktop Entry]
Type=Application
Name=League Manager
Exec=FULL_PATH/main.py $PWD
Icon=FULL_PATH/icon.png
Terminal=true

```
Mueve el lanzador a la carpeta donde lo reconocerá el sistema y atualiza los lanzadores
```bash
mv league_manager.desktop ~/.local/share/applications/
sudo update-desktop-database
```

#### Correr la aplicación
```bash
./main.py
```
O desde el lanzador de aplicaciones