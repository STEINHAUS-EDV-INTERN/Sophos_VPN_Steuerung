# Sophos_VPN_Steuerung
Steuerung von Fernzugriffen mittels Python Tool (Sowohl Sophos User als auch Regeln)

## Ferwartungssteuerung durch Benutzer

### Initial Maske

Startet man das Programm wird man mit der Firmen Ansicht konfrontiert.

![standard-firmen-maske](bilder/standard-firmen-mask.PNG)

Firmen mit einem roten Button haben momentan keinen Zugriff auf das Netzwerk.
Firmen mit einem grünen Buttone haben Zugriff.

### Firmen zuschalten

Möchte der Benutzer eine Firma zuschalten, tut er dies mit der betätigung des roten Buttons mit dem Lable _Off_.
Darauf hin bekommt er ein Popup indem er aufgefordert wird seinen *benutzerspezifischen Pin* einzugeben.

![pin_eingabe](bilder/pin_eingabe.PNG)

Die eingabe seines Pins bestätigt er mit dem Button _OK_.
Nun sollte die Firma einen grünen Button haben mit dem Lable _ON_.

### Firmen abschalten

Möchte der Benutzer eine Firma zuschalten, tut er dies mit der betätigung des roten Buttons mit dem Lable _ON_.
Darauf hin bekommt er ein Popup indem er aufgefordert wird seinen *benutzerspezifischen Pin* einzugeben.

![pin_eingabe](bilder/pin_eingabe.PNG)

Die eingabe seines Pins bestätigt er mit dem Button _OK_.
Nun sollte die Firma einen roten Button haben mit dem Lable _OFF_.


## Benutzersteuerung

### Benutzer anlegen

Um einen neuen Benutzer anzulegen, muss zunächst die Admin-Steuerung geöffnet werden.

![admin_rot_kreis](bilder/admin_rot_kreis.PNG)

Mit dem Klick auf den Button Admin erscheint folgende Maske

![admin_auth](bilder/admin_auth.PNG)

Hier muss nun die eingabe des _Admin Passworts_ erfolgen (längerer Schlüssel).
Mit dem Klick auf OK gelangt der Administrator dann in die Benutzersteuerung.
Hier kann der Administrator im unteren Bereich einen neuen Benutzer anlegen,
dies geschieht mit einem Namen und einem 4-Stelligen Pin.

![neuer_benutzer_eingeben](bilder/neuer_benutzer_eingeben.PNG)

Hier Beispielhaft mit dem Benutzer testbenutzer mit dem Pin 1234
Diese Aktion dann bestätigen mit dem Button _Benutzer hinzufügen_

### Benutzer löschen

Um einen bestehenden Benutzer zu löschen, muss zunächst die Admin-Steuerung geöffnet werden.

![admin_rot_kreis](bilder/admin_rot_kreis.PNG)

Mit dem Klick auf den Button Admin erscheint folgende Maske

![admin_auth](bilder/admin_auth.PNG)

Hier muss nun die eingabe des _Admin Passworts_ erfolgen (längerer Schlüssel).
Mit dem Klick auf OK gelangt der Administrator dann in die Benutzersteuerung.
Hier kann der Administrator den bestehenden Benutzer löschen indem er den Button _Benutzer löschen_ betätigt.

![benuter-loeschen](bilder/benutzer-loeschen.PNG)

### Benutzer Pins ändern

Um einen bestehenden Benutzer zu löschen, muss zunächst die Admin-Steuerung geöffnet werden.

![admin_rot_kreis](bilder/admin_rot_kreis.PNG)

Mit dem Klick auf den Button Admin erscheint folgende Maske

![admin_auth](bilder/admin_auth.PNG)

Hier muss nun die eingabe des _Admin Passworts_ erfolgen (längerer Schlüssel).
Mit dem Klick auf OK gelangt der Administrator dann in die Benutzersteuerung.
Hier kann der Administrator den Pin eines bestehenden Benutzers ändern indem er ihn neu eintippt.

![benutzer_pin_aender](bilder/benutzer_pin_aendern.PNG)

Bestätigt werden muss das ganze mit dem Button _Übernehmen_
