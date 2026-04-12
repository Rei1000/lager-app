# Verifizierte Testzugaenge (Pilot)

Stand: lokaler Verifikationstest gegen laufende API.

## Hinweise

- Passwoerter werden im Seed ueber die bestehende Hashing-Logik (`Pbkdf2PasswordHasher`) gespeichert.
- Diese Zugaenge sind nur fuer lokale Demo-/Pilotumgebungen gedacht.
- ERP-Login immer mit Verbindung `sage-simulator`.

## Funktionierende Logins

| Login-Typ | Verbindung | Benutzername | Passwort | Erwartete Rolle |
|---|---|---|---|---|
| admin | sage-simulator | admin | Admin123! | admin |
| erp | sage-simulator | sage_admin | SageAdmin123! | admin |
| erp | sage-simulator | sage_leitung | SageLeitung123! | leitung |
| erp | sage-simulator | sage_lager | SageLager123! | lager |

## Gepruefte Fehlerfaelle

- Falsches Passwort -> `401 Ungueltige Anmeldedaten`
- Nicht unterstuetzte Verbindung (`middleware`) -> `400 Verbindung noch nicht unterstuetzt`
- Fehlende App-Rolle-Mapping-Logik ist im Use-Case als Fehlerpfad verifiziert (`Keine App-Rolle zugeordnet`).
