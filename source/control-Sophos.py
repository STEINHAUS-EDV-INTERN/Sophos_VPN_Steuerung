import PySimpleGUI as sg
import requests
import sys
import os
import keyring
import time
import win32evtlogutil          # pywin32
import win32evtlog              # pywin32
import logging
import ast
import csv
from datetime import datetime
from keyring.backends import Windows
from base64 import b64encode
from configparser import ConfigParser
from pathlib import Path

"""Sophos Steuerung für die Steinhaus GmbH

Die Sophos wird über die REST-API gesteuert. Hierzu wird zunächshst eine Konfiguration
geladen, in welcher sich die URL der Sophos, sowie die abzufragenden User und Profile
befindet. Bei der Initialausführung muss der Konfigurationspfad, sowie ein Passwort
für den Zugriff auf die Sophos angegeben werden. 
Die Benutzer welche Aktionen ausführenwerden protokolliert. Im Adminbereich können 
Nutzer und die für die Identifikation notwendingen Kennwörter angelegt werden.
"""

### Global Constants ### 
PROGRAMFOLDER =  "\\\\fileserver\\Pool\\SOPHOS_Fernwartungssteuerung\\Steinhaus\\Steinhaus" + "\\logs\\"

# Favicon in Byte
FAVICON = b"iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAA7EAAAOxAG\
VKw4bAAADsElEQVRYhcWWT0xcVRTGf/cxWKYtQgsBeWWqJUPBShOjadVodAiTEhaldVFA6YKFC2P\
c1DZ2S/27M7ExcUO0jSZlShMtXaiFaacu1BQa0gqWkjpN//AoGGOKMANl5h0XrzPAtDPvzQTil7z\
k5dzvne+79517z1U4xcvNhbgLmhDVhKIa0IEKIAqMW48aQKSXYGAQECdplS2jfl8NedrHwG7gMYd\
2xxE5SnztUULH5nIz4NtbjKvgU5C3AJdD4VTcQjhMMNCdnQFr1r3A1hyFU/EFsckDhEIxewMNLfU\
o9R1QtELiCfTjjuzhzJnI0qC2jFK/r2aVxAH8zLmPkzLpvOSbb28xrvxzwCYn2SpLZqnddI/Sonk\
WYhrR+07KRG2jajuEh0PJyKK/ti9B3rZL8YznHz5sv8SzT/2djJmi+HGokveP7yQyb2vEJI/n+Cl\
wGRIrsOuNWkS6SP0lKVhfsMCJg+fZqt9DBKam3ShgTb5JdcU0GwvnCV6xXUCFsIXwyLckBU3zIxx\
sNV/dBJUlswAcOvYCLx1u5vlDr/PbWBkAzTtu2aVIoBF/m88y0NT+ONYhY4vqiunk+w9DHgDuxzT\
6L+sArF0To7wo6syCkv0ACn9LC6iAk2+8T0xTviGKacKv18qT8fKiKF7dMjcULnFSB4BM8cq2CkV\
D69coOjJRN5eVsrFwvROPVmoR/pyYZCaa8RQGTb3oetBY0qLWo3P1q88ciyfw8+9Xee29I5lJcfF\
qWF1txaEc9DkUugurpabF6G0Dz5vvULxunWNxQbgx8ZcTqq5h9fP/ByIRF9ZlYkM6zqrWAGpce2B\
gxeGoBhDDBWoApDEdZfS2wZPt72a9Da8bd21paNpFDZFeO2bcNInF484fM47Y3wgH6es2XAQDg/h\
bDdJsxxqPzmgONXDhyh/4Dn6QnqDU92A1I0Hk87S8rKUtaCpjY/0Xld+1mN/XUYAreg3Y/Ch2Lkf\
xdeMus3Pz6Rid9J88smgAoKG1DcUJxyq5QskdFuRpQj0zsPRKdmNkmKq6UmDnKspH0KSRYM/NRGD\
5j4pNHgD6V0lcUHRwtufS0uByA6FQDHdkD0pOrbB4BFEt9AV6UgfyHqKOjS0QHjlF1XaAV8l9I1h\
QcgdT7eJcIPio4YcNJBAeDlFddxphC+DNQXoG5BNi0s75kzfTkZzNzt/mQ8l+RHaDKsvAFJQaAE6\
j8rs4+82UXerslrezU+OX0R3ExYtCB3REIqDGQQw07SJ93UY2Kf8DMYxYOmQ20wYAAAAASUVORK5\
CYII="

# Log in Textfile
def logevent(msg):
    os.makedirs(PROGRAMFOLDER, exist_ok = True)
    logging.basicConfig(
        filename = PROGRAMFOLDER + "sophos-control.log", 
        encoding = "utf-8", 
        format = "%(asctime)s %(message)s", 
        level = logging.DEBUG
    )
    logging.info(msg)

# Pin Authentifizierung
def pinauth(pins):
    pingui = [
        [sg.Text("Bitte PIN eingeben:")],  
        [sg.Input(key = "pininput", password_char = "*")],
        [sg.Button("Ok", key="trypin"), 
        sg.Cancel(), 
        sg.Text("", size=(15,1), key="passwordmsg")]
    ]
    windowpinauth = sg.Window(
        "Steinhaus Technik VPN Verwaltung", 
        pingui, 
        no_titlebar = False, 
        grab_anywhere = True, 
        return_keyboard_events = True, 
        icon = FAVICON
    )
    while True:
        event, values = windowpinauth.Read()
        if event in (None, "Exit") or event == ("Escape:27"):
            windowpinauth.Close()
            return False, None
        if event in (None, "Cancel"):
            windowpinauth.Close()
            return False, None
        if event in (None, "trypin") or event in ("\r"):
            for name, pin in pins.items():
                if values["pininput"] == pin:
                    windowpinauth.Close()
                    return True, name
                else:
                    windowpinauth.Element("pininput").Update("")
                    windowpinauth.Element("passwordmsg").Update(
                        "Falsches Passwort", 
                        text_color = "red"
                    )

# Create / Check Base Config
def create_baseconfig(basepath):
    # Erstellung des Programmordners
    os.makedirs(PROGRAMFOLDER, exist_ok = True)
    # Erstellung der location.config Datei
    configlocationfile = PROGRAMFOLDER + "location.config"
    open(configlocationfile, "a")
    configlocation = ConfigParser(allow_no_value = True)
    configlocation.optionxform = str # Fix für Case-Sensitive
    configlocation.read(configlocationfile)    
    if not configlocation.has_option("DEFAULT", "Pfad"):
        pfad = ""
        configlocation["DEFAULT"] = {"Pfad": pfad}
        with open(configlocationfile, "w") as configfile:
            configlocation.write(configfile)
    if basepath:
        pfad = basepath
        configlocation["DEFAULT"] = {"Pfad": pfad}
        with open(configlocationfile, "w") as configfile:
            configlocation.write(configfile)        
    # Lesen der location.config Datei
    configlocation.read(configlocationfile)
    configlocation["DEFAULT"].items()
    config_path = configlocation.get("DEFAULT", "Pfad")
    return config_path

# Appdata Config Location
def create_config(failed):
    config_path = create_baseconfig(None)
    if not config_path or failed:
        if failed:
            errortext = sg.Text("Konfiguration ungültig.", text_color = "red")
        else:
            errortext = sg.Text("")

        configgui = [   [sg.Text("Konfiguration wurde nicht gefunden.")],
                        [sg.Text("Neue Konfiguration wählen:")],  
                        [sg.Input(key = "newconfigpath"), sg.FileBrowse()],
                        [sg.OK(), sg.Cancel(), errortext]
                    ]
        window = sg.Window(
            "Steinhaus Technik VPN Verwaltung", 
            configgui, 
            no_titlebar = False, 
            grab_anywhere = True, 
            return_keyboard_events = True, 
            icon = FAVICON
        )
        while True:
            event, values = window.Read()
            if event in (None, "Exit"):
                sys.exit()
            if event in (None, "Cancel"):
                sys.exit()
            if event in (None, "OK"):
                if values["newconfigpath"] == "":
                    pass
                elif values["newconfigpath"]:
                    config_path = create_baseconfig(values["newconfigpath"])
                    window.Close()
                    break
    
    return config_path

# Überprüfung der Gültigkeit der Hauptkonfiguration
def check_config():
    try:
        config_path = create_config(None)
        # Relativer Pfad Hack
        base_path = Path(__file__).parent
        file_path = (base_path / config_path).resolve()
        # Laden der Konfigurationsdatei config.ini
        config = ConfigParser(allow_no_value = True)
        config.optionxform = str # Fix für Case-Sensitive#
        config.read(file_path)
        user_liste = config["user"].items()
        return config
    except:
        create_config(True)
        check_config()

# Windows Event Logging
def printevent(name, sophosobject, status):
    # Switch, wenn Benutzer aktiviert, dann wurde Benutzer deaktiviert.
    if status:
        status = "deaktiviert"
    else:
        status = "aktiviert"

    # Event Text
    eventmsg = f"{name} {sophosobject} {status}"
    logevent(eventmsg)
    # Windows Event
    evt_app_name = "Sophos Control"
    EVT_STRS = [eventmsg]
    EVT_ID = 0  
    EVT_CATEG = 0 
    EVT_DATA = "Application\0Data".encode("ascii")
    EVENT_TYPE = win32evtlog.EVENTLOG_INFORMATION_TYPE
    win32evtlogutil.ReportEvent(
        evt_app_name, 
        EVT_ID, 
        eventCategory = EVT_CATEG,
        eventType = EVENT_TYPE, 
        strings = EVT_STRS,
        data = EVT_DATA
    )

# PIns abspeichern / Default PINs setzen
def savepins(pins):
    # Password Store
    service_id = "control-sophos-pins"
    username = "pins"
    keyring.set_keyring(Windows.WinVaultKeyring())  # Pyinstaller Fix
    if pins == "initial":
        storedpins = keyring.get_password(service_id, username)
        if storedpins is None:
            # Userpins
            pins = '{   "Waldemar Zydziak": "1957", \
                        "Thilo Bicking": "9263", \
                        "Peter Hutsch": "6150", \
                        "Andreas Isberner": "1812",  \
                        "Maximilian Greve": "8429",  \
                        "Ulrich Schmitz": "3492",  \
                        "Alexander Tag": "2184", \
                        "Przemyslaw Tworkiewicz": "3243",  \
                        "Justin Bilgard": "1370",  \
                        "Helmut Kleinen": "3279",  \
                        "Frank Bilgard": "1185",  \
                        "Darius Porzezinski": "6875",  \
                        "André Runge": "9272" \
            }'
            keyring.set_password(service_id, username, pins)
    else:
        keyring.set_password(service_id, username, pins)
    storedpins = keyring.get_password(service_id, username)
    storedpins = ast.literal_eval(storedpins)
    return storedpins

# Abfrage für den Adminbereich
def adminauth(password):
    adminauthgui = [
        [sg.Text("Bitte autorisieren:")],
        [sg.Input(key = "adminpassword", password_char = "*")],
        [sg.Ok(), sg.Cancel(), sg.Text("", size = (15,1), key = "passwordmsg")]
    ]
    adminauthwindow = sg.Window(
        "Steinhaus Technik VPN Verwaltung", 
        adminauthgui, 
        no_titlebar = False, 
        grab_anywhere = True, 
        return_keyboard_events = True, 
        icon = FAVICON
    )
    while True:
        event, values = adminauthwindow.Read()
        if event in (None, "Exit") or event == ("Escape:27"):
            adminauthwindow.Close()
            return False
        if event in (None, "Cancel"):
            adminauthwindow.Close()
            return False
        if event in (None, "Ok") or event in ("\r"):
            if values["adminpassword"] == password:
                adminauthwindow.Close()
                return True
            else:
                adminauthwindow.Element("adminpassword").Update("")
                adminauthwindow.Element("passwordmsg").Update(
                    "Falsches Passwort", 
                    text_color = "red"
                )

# PINs im Adminbereich ändern
def changepin(pins):
        description = [[sg.Text("PIN ändern:")]]
        layoutpinsuser = []
        for user, pin in pins.items():
            header = [[
                sg.Text(
                    "Benutzer", 
                    size = (14,1), 
                    font = (None,10,"underline")), 
                sg.Text(
                    "PIN", 
                    font = (None,10,"underline"))
            ]]
            layoutpinsuser += [[
                sg.Text(
                    user,
                    size = (14,1), 
                    key = "usertext"+user, 
                    tooltip = "Aktueller PIN: "+ pin),  
                sg.Input(
                    size = (20,1), 
                    key = "newpin"+user), 
                sg.Button(
                    "Benutzer löschen", 
                    button_color = ("white", "red"), 
                    key = "deleteuser" + user, 
                    size = (15,1))
            ]]
        layoutpinsuser += [[
            sg.Input(key = "newusername", size = (16,1)), 
            sg.Text(" "* 27, visible = False), 
            sg.Input(key = "newpassword", size = (20,1)), 
            sg.Button(
                "Benutzer hinzufügen", 
                button_color = ("white", "green"), 
                key = "adduser", 
                size = (15,1)
            )
        ]]
        layoutbottom = [[
            sg.Button("Übernehmen", key = "OK"), 
            sg.Button("Exit", key = "Exit"), 
            sg.Text(key="error_pin", size = (24,1))
        ]]
        layout =  header + layoutpinsuser
        layout = [[sg.Frame("PIN ändern", layout)]] + layoutbottom

        changepinwindow = sg.Window(
            "Steinhaus Technik VPN Verwaltung", 
            layout, 
            no_titlebar = False, 
            grab_anywhere = True, 
            return_keyboard_events = True, 
            icon = FAVICON, 
            finalize = True
        )
        while True:     
            event, values = changepinwindow.Read()
            if event in (None, "Exit") or event == ("Escape:27"):
                changepinwindow.Close()
                break
            if event in (None, "OK") or event in (None, "adduser") or event in ("\r"):
                changepinwindow.Element("error_pin").Update("")
                for user, pin in pins.items():
                    if values["newpin" + user]:
                        if values["newpin" + user].casefold() in pins.values():
                            changepinwindow.Element("error_pin").Update(
                                "PIN muss einzigartig sein.", 
                                text_color = "red"
                            )
                            changepinwindow.Element("newpin"+user).Update("")
                        else:
                            pins[user] = values["newpin" + user]
                            changepinwindow.Element("newpin"+user).Update("")
                            changepinwindow.Element("usertext" + user).set_tooltip(
                                "Aktueller PIN: "+ values["newpin" + user]
                            )
                            changepinwindow.Element("error_pin").Update(
                                "Änderung erfolgreich.", 
                                text_color = "green"
                            )
                            savepins(pins)
                if values["newusername"]:
                    if values["newpassword"]:
                        if values["newpassword"].casefold() in pins.values():
                            changepinwindow.Element("error_pin").Update(
                                "PIN muss einzigartig sein.", 
                                text_color = "red"
                            )
                            changepinwindow.Element("newpin"+user).Update("")
                        elif values["newusername"].casefold() in pins.keys():
                            changepinwindow.Element("error_pin").Update(
                                "Benutzer muss einzigartig sein.", 
                                text_color = "red"
                            )
                            changepinwindow.Element("newpin"+user).Update("")
                        else:
                            pins.update({values["newusername"] : values["newpassword"]})
                            changepinwindow.Element("usertext" + user).set_tooltip(
                                "Aktueller PIN: "+ values["newpin" + user]
                            )
                            savepins(pins)
                            changepinwindow.Close()
                            changepin(pins)
            for user, pin in list(pins.items()):
                if event in (None, "deleteuser"+ user):
                    if len(pins) > 1:
                        del pins[user]
                        savepins(pins)
                        changepinwindow.Close()
                        changepin(pins)

# Allgemeines Errorfenster
def errorwindow(errortext):
    error_window = [
        [sg.Text(errortext)], 
        [sg.Button("Exit", key="Exit")]
    ]
    window = sg.Window(
        "Steinhaus Technik VPN Verwaltung", 
        error_window, 
        no_titlebar = False, 
        grab_anywhere = True, 
        return_keyboard_events = True, 
        icon = FAVICON
        )
    while True:
        event, values = window.Read()
        if event in (None, "Exit"):
            sys.exit()

# Verbindungsüberprüfung
def checkconnection(SophosAuth):
    response = requests.get(
        SophosAuth.userURI, 
        headers = {"Authorization": "Basic " + SophosAuth.encodedpair}, 
        verify = SophosAuth.verifyCert
    )
    print(response)
    if response.status_code == 401:
        error_text = [  [sg.Text("Error: Benutzer ist nicht autorisiert.")],
                        [sg.Text(" "*30)],
                        [sg.Text("Neues Passwort:", size = (15, 1)), 
                            sg.InputText("", key = "Password", password_char = "*")],
                        [sg.Button("Ok", key = "changepassword"), 
                            sg.Button("Abbrechen", key="Exit")]
                        ]
        window = sg.Window(
            "Steinhaus Technik VPN Verwaltung", 
            error_text, 
            no_titlebar = False, 
            grab_anywhere = True, 
            return_keyboard_events = True, 
            icon = FAVICON
        )
        while True:
            event, values = window.Read()
            if event in (None, "Exit"):
                break
            if event in (None, "changepassword") or event in ("\r"):
                password = values["Password"]
                if password:
                    # Create Authentication
                    pair = SophosAuth.username + ":" + password
                    encodedpair = b64encode(pair.encode())
                    encodedpair = encodedpair.decode("utf-8")
                    # Verbindungsüberprüfung
                    response = requests.get(
                        SophosAuth.userURI, 
                        headers = {"Authorization": "Basic " + encodedpair}, 
                        verify = SophosAuth.verifyCert
                    )
                    if response.status_code == 200:
                        keyring.set_password(SophosAuth.service_id, SophosAuth.username, password)
                        sg.popup(
                            "Neues Passwort ist korrekt und wurde gesetzt.", 
                            title = "", 
                            no_titlebar = False, 
                            grab_anywhere = True, 
                            icon = FAVICON
                        )
                        window.Close()
                        os.execv(sys.executable, ["python"] + sys.argv)     # Neustart der Anwendung
                    if response.status_code == 401:
                        sg.popup(
                            "Das Passwort ist falsch.", 
                            title = "", 
                            no_titlebar = False, 
                            grab_anywhere = True, 
                            background_color = "red", 
                            icon = FAVICON
                        )
                        window.Element("Password").Update("")
        sys.exit()
    if response.status_code == 404:
        error_text = [[sg.Text("Error: Die Webadresse wurde nicht gefunden.")]]
        window = sg.Window(
            "Steinhaus Technik VPN Verwaltung", 
            error_text, 
            no_titlebar = False, 
            grab_anywhere = True, 
            icon = FAVICON
        )
        while True:
            event, values = window.Read()
            if event in (None, "Exit"):
                break
        sys.exit()
    if response.status_code != 200:
        error_text = [[sg.Text("Error Code: " + str(response.status_code))]]
        window = sg.Window(
            "Steinhaus Technik VPN Verwaltung", 
            error_text, 
            no_titlebar = False, 
            grab_anywhere = True, 
            icon = FAVICON
        )
        while True:             # Event Loop
            event, values = window.Read()
            if event in (None, "Exit"):
                break
        sys.exit()
    if response.status_code == 200:
        pass

# Funktion um den aktuellen Status von der Sophos neu abzurufen
def refreshstatus(SophosAuth, window):
    print("Refreshing " + time.strftime("%X %x %Z"))
     # Benutzerüberprüfung
    user_resp = requests.get(
        SophosAuth.userURI, 
        headers = {"Authorization": "Basic " + SophosAuth.encodedpair}, 
        verify = SophosAuth.verifyCert
    )
    for listuser, temp in SophosAuth.user_liste:
        for user in user_resp.json():
            if listuser == user["name"]:
                status = user["enabled"]
                if status:
                    window.Element(listuser).Update(
                        "On",
                        button_color = ("white", "green")
                    )
                if not status:
                    window.Element(listuser).Update(
                        "Off",
                        button_color = ("white", "red")
                    )
    # Profilüberprüfung
    profile_resp = requests.get(
        SophosAuth.profileURI, 
        headers = {"Authorization": "Basic " + SophosAuth.encodedpair}, 
        verify = SophosAuth.verifyCert
    )
    for listprofile, temp in SophosAuth.profile_liste:
        for profile in profile_resp.json():
            if listprofile == profile["_ref"]:
                status = profile["status"]
                if status:
                    window.Element(listprofile).Update(
                        "On",
                        button_color = ("white", "green")
                    )
                if not status:
                    window.Element(listprofile).Update(
                        "Off",
                        button_color = ("white", "red")
                    )

# User-GUI
def maingui(SophosAuth):
    # GUI Elemente
    layout_space1 = [[sg.Text(" "*40)]]

    user_resp = requests.get(
        SophosAuth.userURI, 
        headers = {"Authorization": "Basic " + SophosAuth.encodedpair}, 
        verify = SophosAuth.verifyCert
    )  

    # Benutzer in die GUI laden
    # layout_usertext = [[sg.Text("Benutzer")]]
    layout_user = []
    for user in user_resp.json():
        for listuser, temp in SophosAuth.user_liste:
            if listuser == user["name"]:
                if user["enabled"]:
                    layout_user += [[
                        sg.Button(
                            "On", 
                            size = (5,1), 
                            button_color = ("white", "green"), 
                            key = listuser
                        ), 
                        sg.Text(user["realname"])
                    ]]
                if not user["enabled"]:
                    layout_user += [[
                        sg.Button(
                            "Off", 
                            size = (5,1), 
                            button_color = ("white", "red"), 
                            key = listuser
                        ), 
                        sg.Text(user["realname"])
                    ]]


    profile_resp = requests.get(
        SophosAuth.profileURI, 
        headers = {"Authorization": "Basic " + SophosAuth.encodedpair}, 
        verify = SophosAuth.verifyCert
    )

    # Profile in die GUI laden
    layout_profile = []
    for profile in profile_resp.json():
        for listprofile, temp in SophosAuth.profile_liste:
            if listprofile == profile["_ref"]:
                if profile["status"]:
                    layout_profile += [[
                        sg.Button(
                            "On", 
                            size = (5,1), 
                            button_color = ("white", "green"), 
                            key = listprofile
                        ), 
                        sg.Text(profile["comment"])
                    ]]
                if not profile["status"]:
                    layout_profile += [[
                        sg.Button(
                            "Off", 
                            size = (5,1), 
                            button_color = ("white", "red"), 
                            key = listprofile
                        ), 
                        sg.Text(profile["comment"])
                    ]]

    # Erstellung der Struktur
    layout_refresh = [[sg.Button("Refresh"), sg.Button("Admin"), sg.Button("Logs"), sg.Button("Exit")]]
    layout = [[sg.Frame("Steinhaus Technik VPN Steuerung", layout_user + layout_profile)]]
    layout = layout + layout_space1 + layout_refresh

    # GUI Erstellung
    window = sg.Window(
        "Steinhaus Technik VPN Verwaltung", 
        layout, 
        element_justification = "r", 
        no_titlebar = False, 
        grab_anywhere = True, 
        icon = FAVICON
    )
    while True:
        event, values = window.Read(timeout=1000)
        # Benutzersteuerung
        for listuser, temp in SophosAuth.user_liste:
            if event == listuser:
                window.disable()
                value, name = pinauth(SophosAuth.pins)
                window.enable()
                window.BringToFront()
                if value:
                    user_resp = requests.get(
                        SophosAuth.userURI, 
                        headers = {"Authorization": "Basic " + SophosAuth.encodedpair}, 
                        verify = SophosAuth.verifyCert
                    ) 
                    for user in user_resp.json():
                        if listuser == user["name"]:
                            ref = user["_ref"]
                            status = user["enabled"]
                            if status:
                                printevent(name, listuser, status)
                                task = {"enabled": False}
                                window.Element(event).Update(
                                    "Off",
                                    button_color = ("white", "red")
                                )
                            if not status:
                                printevent(name, listuser, status)
                                task = {"enabled": True}
                                window.Element(event).Update(
                                    "On",
                                    button_color = ("white", "green")
                                )
                    resp = (requests.patch(
                        SophosAuth.userURI + ref, 
                        headers = {"Authorization": "Basic " + SophosAuth.encodedpair}, 
                        json = task, 
                        verify = SophosAuth.verifyCert
                    ))
        # Profilsteuerung
        for listprofile, temp in SophosAuth.profile_liste:
            if event == listprofile:
                window.disable()
                value, name = pinauth(SophosAuth.pins)
                window.enable()
                window.BringToFront()
                if value:
                    profile_resp = requests.get(
                        SophosAuth.profileURI, 
                        headers = {"Authorization": "Basic " + SophosAuth.encodedpair}, 
                        verify = SophosAuth.verifyCert
                    ) 
                    for profile in profile_resp.json():
                        if listprofile == profile["_ref"]:
                            ref = profile["_ref"]
                            status = profile["status"]
                            if status:
                                printevent(name, listprofile, status)
                                task = {"status": False}
                                window.Element(event).Update(
                                    "Off",
                                    button_color = ("white", "red")
                                )
                            if not status:
                                printevent(name, listprofile, status)
                                task = {"status": True}
                                window.Element(event).Update(
                                    "On",
                                    button_color = ("white", "green")
                                )
                    resp = (requests.patch(
                        SophosAuth.profileURI + ref, 
                        headers = {"Authorization": "Basic " + SophosAuth.encodedpair}, 
                        json = task, 
                        verify = SophosAuth.verifyCert
                    ))
        if event == "Refresh":
            refreshstatus(SophosAuth, window)
        if round(time.time()) % 30  == 0:
            refreshstatus(SophosAuth, window)
        if event == "Admin":
            window.disable()
            if adminauth(SophosAuth.password):
                changepin(SophosAuth.pins)
            window.enable()
            window.BringToFront()
        if event == "Logs":
            window.disable()
            if adminauth(SophosAuth.password):
                show_log_window()
            window.enable()
            window.BringToFront
        if event in (None, "Exit"):
            window.Close()
            break

def show_log_window():
    filename = PROGRAMFOLDER + 'logs.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as out_file, open(PROGRAMFOLDER + 'sophos-control.log', 'r') as in_file:
        writer = csv.writer(out_file)
        writer.writerow(['Datum', 'Zeit', 'Benutzer Nachname', 'Benutzer Vorname', 'VPN Benutzer', 'Geschaltet auf'])
        
        for line in in_file:
              columns = line[:-1].split(' ')
              if(len(columns) == 6):
                  writer.writerow(columns[:6])
    
    if filename is not None:
        with open(filename, "r") as infile:
            reader = csv.reader(infile)
            header_list = next(reader)
            try:
                data = list(reader)
            except:
                sg.popup_error('Fehler beim Lesen der Datei')
                return

    sg.set_options(element_padding=(0, 0))

    layout = [[sg.Table(values=data,
                            headings=header_list,
                            max_col_width=25,
                            auto_size_columns=True,
                            justification='right',
                            num_rows=min(len(data), 20))]]


    window = sg.Window('Logs', layout, grab_anywhere=False)
    event, values = window.read()

    window.close()

# Hauptfunktion
def main():
    logevent("Programm wurde gestartet.")

    # Theme Color
    sg.theme("DarkTeal9")

    # Prüfung ob die Konfiguration vorhanden ist
    config = check_config()
    if config is None:
        config = check_config()

    # Klasse mit allen Verbindungsinformationen
    class SophosAuth:
        # Lesen der Benutzer
        user_liste = config["user"].items()
        profile_liste = config["profile"].items()
        # Parameter
        username = config.get("allgemein", "username")
        userURI = config.get("allgemein", "userURI")
        profileURI = config.get("allgemein", "profileURI")
        verifyCert = config.get("allgemein", "verifyCert")
        verifyCert = verifyCert.casefold() in ["true", "1", "ja", "an", "aktiv"]
        # Password Store
        service_id = "control-sophos"
        password = ""
        keyring.set_keyring(Windows.WinVaultKeyring())  # Pyinstaller Fix
        if keyring.get_password(service_id, username):
            password = keyring.get_password(service_id, username)
        # Create Authentication
        pair = username + ":" + password
        encodedpair = b64encode(pair.encode())
        encodedpair = encodedpair.decode("utf-8")
        # Speicherung der PINs
        pins = savepins("initial")

    # Verbindungsüberprüfung
    try:
        checkconnection(SophosAuth)
    except Exception as e:
        errorwindow("Verbindung konnte nicht hergestellt werden. Error: \n" + str(e))

    # Start Main-GUI
    try:
        maingui(SophosAuth)
    except Exception as e:
        errorwindow("GUI Error: \n" + str(e))

if __name__ == "__main__":
    main()
