# Pilot-Abnahmeszenarien

Ziel dieses Dokuments: typische Lagerablaeufe aus Nutzersicht einheitlich pruefen und bewerten.

Hinweis zur Bewertung je Szenario:
- funktioniert / funktioniert nicht
- verstaendlich / unklar
- schnell / umstaendlich

---

## Szenario 1: Material scannen -> Auftrag erstellen -> reservieren

**Ziel**  
Ein Lagerprozess startet mit einem Material und endet mit einem reservierten Auftrag.

**Ausgangssituation**  
Benutzer ist eingeloggt. Material ist im System vorhanden (z. B. `ART-DEMO`).

**Schritte**
1. Seite `Scan` oeffnen und Material ueber Suchfeld oder Kamera suchen.
2. Materialdetails pruefen (Artikel, Bestand, Hinweisdaten).
3. Seite `Orders` oeffnen und einen neuen Auftrag fuer das Material erfassen.
4. In der Auftragsliste den neuen Auftrag finden.
5. Aktion `Reserve` ausfuehren.

**Erwartetes Ergebnis**
- Material ist auffindbar und eindeutig erkennbar.
- Auftrag ist in der Liste sichtbar.
- Auftragsstatus wechselt auf `reserved`.

**Checkliste**
- [ ] funktioniert / funktioniert nicht
- [ ] verstaendlich / unklar
- [ ] schnell / umstaendlich

**Typische Fehlerfaelle (optional)**
- Material wird nicht gefunden.
- Reservierung wird abgelehnt (Rolle/Status).

---

## Szenario 2: Auftrag priorisieren -> Reihenfolge pruefen

**Ziel**  
Mehrere Auftraege werden in eine fachlich sinnvolle Reihenfolge gebracht.

**Ausgangssituation**  
Es existieren mindestens zwei Auftraege zum selben Material.

**Schritte**
1. Seite `Orders` oeffnen.
2. Bestehende Auftraege zum gewuenschten Material filtern.
3. Reihenfolge mit der Priorisierungsfunktion anpassen.
4. Ergebnisliste neu laden und Reihenfolge kontrollieren.

**Erwartetes Ergebnis**
- Prioritaetsreihenfolge ist sichtbar aktualisiert.
- Reihenfolge bleibt nach Reload erhalten.

**Checkliste**
- [ ] funktioniert / funktioniert nicht
- [ ] verstaendlich / unklar
- [ ] schnell / umstaendlich

**Typische Fehlerfaelle (optional)**
- Ungueltige oder fehlende Auftrags-ID in der Priorisierung.

---

## Szenario 3: Inventur durchfuehren -> Abweichung erkennen -> Korrektur anlegen

**Ziel**  
Ein Ist-Bestand wird erfasst, bewertet und als Korrekturvorgang dokumentiert.

**Ausgangssituation**  
Benutzer ist eingeloggt, Material ist vorhanden.

**Schritte**
1. Seite `Inventur` oeffnen.
2. Neue Zaehlung mit Material und Ist-Bestand erfassen.
3. Abweichung vergleichen.
4. Aus der Zaehlung einen Korrekturvorgang anlegen.
5. Korrekturstatus pruefen (angelegt/bestaetigt/storniert je nach Test).

**Erwartetes Ergebnis**
- Zaehlung ist in der Liste sichtbar.
- Abweichung ist nachvollziehbar ausgewiesen.
- Korrekturvorgang ist angelegt und statusseitig nachvollziehbar.

**Checkliste**
- [ ] funktioniert / funktioniert nicht
- [ ] verstaendlich / unklar
- [ ] schnell / umstaendlich

**Typische Fehlerfaelle (optional)**
- Ungueltige Inventur-ID bei Korrekturanlage.

---

## Szenario 4: ERP-Transfer vorbereiten -> freigeben -> senden

**Ziel**  
Ein Transfer wird kontrolliert durch den Freigabeprozess gefuehrt.

**Ausgangssituation**  
Auftrag und Material liegen vor; Benutzer mit passender Rolle ist eingeloggt.

**Schritte**
1. Seite `ERP-Transfers` oeffnen.
2. Neuen Transfer fuer Auftrag/Material erstellen.
3. Transfer in den Status `ready` setzen.
4. Transfer freigeben (`approved`).
5. Transfer senden (`sent`) mit berechtigter Rolle.

**Erwartetes Ergebnis**
- Transfer ist in der Liste sichtbar.
- Statuswechsel folgen der vorgesehenen Reihenfolge.
- Endstatus ist eindeutig erkennbar.

**Checkliste**
- [ ] funktioniert / funktioniert nicht
- [ ] verstaendlich / unklar
- [ ] schnell / umstaendlich

**Typische Fehlerfaelle (optional)**
- Aktion wegen fehlender Rolle nicht erlaubt.
- Statuswechsel ausserhalb der Reihenfolge wird abgelehnt.

---

## Szenario 5: Material mit Foto und Kommentar dokumentieren

**Ziel**  
Ein Materialvorgang wird nachvollziehbar dokumentiert.

**Ausgangssituation**  
Material ist vorhanden; Benutzer ist eingeloggt.

**Schritte**
1. Seite `Scan` oeffnen und Material aufrufen.
2. Ein Foto zum Material hochladen.
3. Einen Kommentar zum Material speichern.
4. Foto- und Kommentarbereich erneut laden bzw. pruefen.

**Erwartetes Ergebnis**
- Foto ist sichtbar hinterlegt.
- Kommentar ist sichtbar und dem Material zugeordnet.

**Checkliste**
- [ ] funktioniert / funktioniert nicht
- [ ] verstaendlich / unklar
- [ ] schnell / umstaendlich

**Typische Fehlerfaelle (optional)**
- Upload ohne Datei.
- Kommentar leer.

---

## Szenario 6: Fehlerfall ERP-Transfer -> Kommentar und Analyse

**Ziel**  
Ein gescheiterter ERP-Transfer wird dokumentiert und nachvollziehbar bewertet.

**Ausgangssituation**  
Mindestens ein Transfer existiert.

**Schritte**
1. Seite `ERP-Transfers` oeffnen.
2. Einen Transfer gezielt auf `failed` setzen (mit Fehlergrund).
3. Direkt einen Kommentar am Transfer erfassen.
4. Verlauf und Fehlergrund im Transfer pruefen.

**Erwartetes Ergebnis**
- Transferstatus ist `failed`.
- Fehlergrund ist sichtbar.
- Kommentar ist dem Transfer zugeordnet und sichtbar.

**Checkliste**
- [ ] funktioniert / funktioniert nicht
- [ ] verstaendlich / unklar
- [ ] schnell / umstaendlich

**Typische Fehlerfaelle (optional)**
- Fehlergrund fehlt oder ist zu allgemein.

---

## Hinweise aus dem Pilot (TODO/NOTES)

Hier waehrend des Piloten kurz notieren:
- Welche Schritte waren unklar?
- Wo kam es zu Rueckfragen im Team?
- Welche Aktionen wirken zu langsam oder zu umstaendlich?
- Welche Fehlermeldungen waren fuer Nutzer schwer verstaendlich?
