# Sophos VPN-Fernsteuerung
Steuerung von Fernzugriffen mittels Python Tool (Sowohl Sophos User als auch Regeln)

## Wichtige Informationen

- Benutzer Pins/Passwörter können bei Bedarf mehr als 4-Stellige sein
- Logs können durch die EDV-Abteilung eingesehen werden
- Logs können durch die EDV-Abteilung zurückgesetzt werden
- Neue Firmen können und sollten nur durch die EDV hinzugefügt werden
- Pins/Passwörter von Benutzern sind personenbezogen und dürfen nicht weitergesagt werden
- Sollten ein neuer Benutzer benötigt werden wird dies  vom zuständigen Administrator durchgeführt
- Das Administratorpasswort darf niemals digital vorliegen (Optimalerweise auch nicht physikalisch)

## Fernwartungsteuerung durch Benutzer

### Initial Maske

Startet der Benutzer das Programm, wird er mit der Firmen Ansicht konfrontiert.

![standard-firmen-maske](http://weissenfels.icu/bilder/standard-firmen-maske.PNG)

Firmen mit einem roten Button haben momentan keinen Zugriff auf das Netzwerk.
Firmen mit einem grünen Button haben Zugriff.

### Firmen zuschalten

Möchte der Benutzer eine Firma zuschalten, tut er dies mit der Betätigung des roten Buttons mit dem Lable _Off_.
Darauf hin bekommt er ein Pop-up, indem er aufgefordert wird seinen *benutzerspezifischen Pin* einzugeben.

![pin_eingabe](http://weissenfels.icu/bilder/ping_eingabe.PNG)

Die Eingabe seines Pins bestätigt er mit dem Button _OK_.
Nun sollte die angewählte Firma einen grünen Button haben mit dem Lable _ON_.

### Firmen abschalten

Möchte der Benutzer eine Firma abschalten, tut er dies mit der Betätigung des roten Buttons mit dem Lable _FF_.
Darauf hin bekommt er ein Pop-up, indem er aufgefordert wird seinen *Benutzerspezifischen Pin* einzugeben.

![pin_eingabe](http://weissenfels.icu/bilder/ping_eingabe.PNG)

Die Eingabe seines Pins bestätigt er mit dem Button _OK_.
Nun sollte die angewählte Firma einen roten Button haben mit dem Lable _OFF_.

## Nachverfolgbarkeit

Die Nachverfolgbarkeit von Zu- und Abschaltungen ist gewährt durch ein Logging von allen Aktionen.
Um diese Logs einzusehen, bietet die Oberfläche einen Button _Logs_.

![log_button](http://weissenfels.icu/bilder/log_button.png)

Mit dem Klick auf den Button Logs erscheint folgende Maske

![admin_auth](http://weissenfels.icu/bilder/admin_auth.PNG)

Hier muss nun die Eingabe des _Admin Passworts_ erfolgen (längerer Schlüssel).
Nach Eingabe des Schlüssels das ganze mit dem _OK_ Button bestätigen.
Daraufhin öffnet sich ein neues Fenster mit allen wichtigen Informationen.

![log_maske](http://weissenfels.icu/bilder/log_maske.PNG)

Einträge, die länger zurückliegen und somit obsolet sind können durch die EDV-Abteilung entfernt werden (eigentlich nicht nötig).

## Benutzersteuerung

### Benutzer anlegen

Um einen neuen Benutzer anzulegen, muss zunächst die Admin-Steuerung geöffnet werden.

![admin_rot_kreis](http://weissenfels.icu/bilder/admin_rot_kreis.PNG)

Mit dem Klick auf den Button Admin erscheint folgende Maske

![admin_auth](http://weissenfels.icu/bilder/admin_auth.PNG)

Hier muss nun die Eingabe des _Admin Passworts_ erfolgen (längerer Schlüssel).
Mit dem Klick auf OK gelangt der Administrator dann in die Benutzersteuerung.
Hier kann der Administrator im unteren Bereich einen neuen Benutzer anlegen,
dies geschieht mit einem Namen und einem 4-Stelligen Pin.

![neuer_benutzer_eingeben](http://weissenfels.icu/bilder/neuer_benutzer_eingeben.PNG)

Hier Beispielhaft mit dem Benutzer *testbenutzer* mit dem Pin 1234.
Diese Aktion dann bestätigen mit dem Button _Benutzer hinzufügen_.

### Benutzer löschen

Um einen bestehenden Benutzer zu löschen, muss zunächst die Admin-Steuerung geöffnet werden.

![admin_rot_kreis](http://weissenfels.icu/bilder/admin_rot_kreis.PNG)

Mit dem Klick auf den Button Admin erscheint folgende Maske

![admin_auth](http://weissenfels.icu/bilder/admin_auth.PNG)

Hier muss nun die Eingabe des _Admin Passworts_ erfolgen (längerer Schlüssel).
Mit dem Klick auf OK gelangt der Administrator dann in die Benutzersteuerung.
Hier kann der Administrator den bestehenden Benutzer löschen, indem er den Button _Benutzer löschen_ betätigt.

![benuter-loeschen](http://weissenfels.icu/bilder/benutzer-loeschen.PNG)

### Benutzer Pins ändern

Um einen bestehenden Benutzer zu löschen, muss zunächst die Admin-Steuerung geöffnet werden.

![admin_rot_kreis](http://weissenfels.icu/bilder/admin_rot_kreis.PNG)

Mit dem Klick auf den Button Admin erscheint folgende Maske

![admin_auth](http://weissenfels.icu/bilder/admin_auth.PNG)

Hier muss nun die Eingabe des _Admin Passworts_ erfolgen (längerer Schlüssel).
Mit dem Klick auf OK gelangt der Administrator dann in die Benutzersteuerung.
Hier kann der Administrator den Pin eines bestehenden Benutzers ändern indem er ihn neu eintippt.

![benutzer_pin_aender](http://weissenfels.icu/bilder/benutzer_pin_aendern.PNG)

Bestätigt werden muss das ganze mit dem Button _Übernehmen_
