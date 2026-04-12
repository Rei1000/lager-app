# E2E-Checkplan Pilot (Sage-Simulator)

Ziel: zentrale Pilotablaeufe mit der bestehenden Sage-Simulator-Verbindung strukturiert und reproduzierbar pruefen.

## Rahmen fuer die Durchfuehrung

- **Verbindung**: bei ERP-Login immer `sage-simulator` waehlen.
- **Empfohlene Testbenutzer**:
  - `sage_lager` (operativer Ablauf)
  - `sage_leitung` (Freigaben)
  - `sage_admin` (Admin-Senden / Gesamtpruefung)
- **Typische Seiten**: `Login`, `Scan`, `Orders`, `Inventur`, `ERP-Transfers`, `Dashboard`.
- **Hinweis zur Dokumentation**: Beobachtungen, Abweichungen und Auffaelligkeiten direkt je Check im Notizbereich erfassen.

---

## Check 1: Login mit Simulator-Benutzer

**Ziel**  
Pruefen, dass ERP-Login mit Simulator-Benutzer funktioniert und der Kontext korrekt sichtbar ist.

**Voraussetzungen**
- Laufende Pilotumgebung
- Testbenutzer `sage_lager` bekannt

**Schritte**
1. `Login` aufrufen.
2. Verbindung `sage-simulator` waehlen.
3. Login-Modus `ERP-Benutzer` waehlen.
4. Mit `sage_lager` anmelden.
5. Header/Navigation nach dem Login pruefen.

**Erwartetes Ergebnis**
- Login erfolgreich.
- Rolle ist in der UI konsistent sichtbar/nutzbar.
- Verbindungskontext ist sichtbar (z. B. ERP + `sage-simulator`).

**Ergebnis / Notizen**
- Status: [ ] OK [ ] Abweichung
- Notizen:

---

## Check 2: Materialsuche / Scan mit ERP-Daten

**Ziel**  
Sicherstellen, dass Material ueber Suche/Scan gefunden wird und ERP-Bestand sichtbar ist.

**Voraussetzungen**
- Eingeloggt als `sage_lager`
- Beispielmaterial vorhanden (z. B. `ALU-R20-2000`)

**Schritte**
1. `Scan` oeffnen.
2. Material per Suche oder Scan finden.
3. Materialdetail aufrufen.
4. ERP-Bestand pruefen.
5. Optional Kommentar/Foto pruefen oder erfassen.

**Erwartetes Ergebnis**
- Material wird gefunden.
- Materialdetail ist nachvollziehbar.
- ERP-Bestand ist sichtbar.
- Kommentar/Foto sind nutzbar (falls vorhanden/freigeschaltet).

**Ergebnis / Notizen**
- Status: [ ] OK [ ] Abweichung
- Notizen:

---

## Check 3: Auftrag anlegen und reservieren

**Ziel**  
Pruefen, dass aus Materialkontext ein Auftrag angelegt und reserviert werden kann.

**Voraussetzungen**
- Eingeloggt als `sage_lager` oder `sage_leitung`
- Material bekannt

**Schritte**
1. `Orders` oeffnen.
2. Auftrag fuer ein vorhandenes Material anlegen.
3. Auftrag in der Liste finden.
4. Reservierung ausfuehren.
5. Status und Ampelanzeige pruefen.

**Erwartetes Ergebnis**
- Auftrag ist sichtbar.
- Reservierung funktioniert.
- Status/Ampel sind konsistent dargestellt.

**Ergebnis / Notizen**
- Status: [ ] OK [ ] Abweichung
- Notizen:

---

## Check 4: Inventur / Korrektur mit Foto und Kommentar

**Ziel**  
Nachvollziehbarkeit eines Inventur- und Korrekturvorgangs inkl. Dokumentation pruefen.

**Voraussetzungen**
- Eingeloggt als `sage_lager`
- Material vorhanden

**Schritte**
1. `Inventur` oeffnen und neue Zaehlung anlegen.
2. Abweichung erzeugen oder bestehende Abweichung pruefen.
3. Korrekturvorgang anlegen.
4. Optional Foto hochladen.
5. Optional Kommentar erfassen.
6. Verlauf/Listenansicht neu laden und pruefen.

**Erwartetes Ergebnis**
- Vorgang ist sichtbar.
- Abweichung/Korrektur ist nachvollziehbar.
- Foto/Kommentar sind dem Vorgang eindeutig zugeordnet.

**Ergebnis / Notizen**
- Status: [ ] OK [ ] Abweichung
- Notizen:

---

## Check 5: ERP-Transfer vorbereiten und freigeben

**Ziel**  
Statuskette bis zur Freigabe im Rollenwechsel pruefen.

**Voraussetzungen**
- Vorhandener Auftrag/Material
- Login mit `sage_leitung` (oder rollenkonformer Benutzer)

**Schritte**
1. `ERP-Transfers` oeffnen.
2. Transfer anlegen.
3. Transfer auf `ready` setzen.
4. Transfer freigeben (`approved`) mit Leitung/Admin.
5. Transferliste inkl. Statusverlauf pruefen.

**Erwartetes Ergebnis**
- Statuswechsel erfolgen in der erwarteten Reihenfolge.
- Transfer bleibt konsistent sichtbar.
- Audit/Kommentar sind sichtbar, falls im Ablauf erfasst.

**Ergebnis / Notizen**
- Status: [ ] OK [ ] Abweichung
- Notizen:

---

## Check 6: ERP-Transfer senden (Admin)

**Ziel**  
Write-Flow gegen Sage-Simulator kontrolliert pruefen.

**Voraussetzungen**
- Transfer im sendefaehigen Zustand (`approved`)
- Eingeloggt als `sage_admin`

**Schritte**
1. `ERP-Transfers` oeffnen.
2. Sendefaehigen Transfer waehlen.
3. Senden ausfuehren.
4. Status, Rueckmeldung und Verlauf pruefen.

**Erwartetes Ergebnis**
- Entweder erfolgreicher Send-Status oder sauberer Fehlerpfad.
- Kein UI-Absturz.
- Status/Audit sind nachvollziehbar.

**Ergebnis / Notizen**
- Status: [ ] OK [ ] Abweichung
- Notizen:

---

## Check 7: Fehlerfall (ungueltige Referenz / fehlende Rolle)

**Ziel**  
Robustes Verhalten bei typischen Fehlerfaellen pruefen.

**Voraussetzungen**
- Testfall mit ungueltiger ERP-Referenz verfuegbar
- Optional Testbenutzer ohne gueltige Rolle

**Schritte**
1. Ungueltige ERP-Referenz in einem passenden Schritt verwenden (z. B. Auftragsreferenz).
2. Reaktion der UI pruefen.
3. Optional Login mit Benutzer ohne gueltige Rolle pruefen.
4. Verhalten nach Fehler (weiterarbeiten, Navigation, Meldung) pruefen.

**Erwartetes Ergebnis**
- Verstaendliche Fehlermeldung.
- Kein Absturz.
- Kein stilles Fehlverhalten.

**Ergebnis / Notizen**
- Status: [ ] OK [ ] Abweichung
- Notizen:

---

## Kurze Pilot-Auswertungsvorlage

- Was lief gut?
- Was war unklar?
- Wo gab es Medienbrueche?
- Welche Schritte fuehlten sich unnötig umstaendlich an?
