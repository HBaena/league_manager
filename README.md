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
cd league_manager
pip3 install gobject pandas pyodbc --user
chmod a+x main.py
```

#### Correr la aplicación
```bash
./main.py
```