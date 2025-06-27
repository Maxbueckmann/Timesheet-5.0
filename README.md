# Timesheet 2.0

Ein modernes Zeiterfassungssystem mit Unterstützung für Kundenprojekte, interne Arbeitszeit und Abwesenheiten.

## Funktionen

- Hierarchische Aktivitätsauswahl (Typ → spezifische Aktivität)
- Echtzeit-Timer mit Start/Stop-Funktionalität
- Wochenübersicht mit Stundensummen
- Konfigurationsbereich für:
  - Kundenprojekte (chargeable/non-chargeable)
  - Interne Arbeitszeit
  - Abwesenheiten
- Validierung von Projekten und Kategorien
- Kommentarfunktion für Zeiteinträge

## Installation & Start

### Automatische Installation und Start
Einfach ausführen:
```bash
python start.py
```
Das Skript wird automatisch:
1. Eine virtuelle Python-Umgebung erstellen
2. Alle Abhängigkeiten installieren
3. Die Datenbank initialisieren
4. Die Anwendung starten

### Manuelle Installation
Falls Sie die Installation manuell durchführen möchten:

1. Python-Umgebung einrichten:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Unter Windows: venv\Scripts\activate
   ```

2. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```

3. Datenbank initialisieren:
   ```bash
   python init_db.py
   ```

4. Anwendung starten:
   ```bash
   python app.py
   ```

Die Anwendung ist dann unter `http://localhost:5000` erreichbar.

## Vorkonfigurierte Daten

### Abwesenheiten (Project ID: 890085)
- Uni Zeit (H03147)
- Krankheit (H03128)
- Urlaub (H03118)
- Sonderurlaub (H03003)

### Interne Arbeitszeit (Project ID: 890023)
- Training (H03107)
- Projektarbeit (H03108)
- Interne Meetings (H03104)
- 1:1 Gespräche (H03108)
- Interne Operationen (H03105)

### Beispiel-Kundenprojekt
- Siemens Xcelerator
  - Chargeable: 312464.02.01.02 (H02006.13)
  - Non-Chargeable: 312464.02.01.04 (H02006.13)

## Projektstruktur

```
timesheet/
├── app.py                 # Flask-Anwendung und API-Routen
├── init_db.py            # Datenbankinitialisierung
├── start.py              # Automatisches Setup-Skript
├── requirements.txt      # Python-Abhängigkeiten
├── static/
│   ├── css/
│   │   └── style.css     # Anwendungsstile
│   └── js/
│       ├── timer.js      # Timer-Funktionalität
│       ├── timesheet.js  # Zeiterfassungslogik
│       └── configuration.js # Konfigurationslogik
└── templates/
    ├── base.html         # Basis-Template
    ├── index.html        # Zeiterfassungsseite
    └── configuration.html # Konfigurationsseite
```

## Entwicklung

Die Anwendung verwendet:
- Flask für das Backend
- SQLite als Datenbank
- Bootstrap 5 für das Frontend
- Vanilla JavaScript für die Client-Logik

##Ich möchte ein absolut geiles nutzerfreundliches Zeiterfassungstool erstellen. Bitte lese dir hier erstmal alles durch und verstehe

Unten findest du einen sehr detaillierten Plaintext-Flow, in dem alle Abhängigkeiten klar dargestellt sind. Er gliedert sich in zwei große Bereiche:

Konfigurationsbereich (zentrale Pflege aller Kunden, Projekte, Kategorien usw.)
Zeiterfassung (Start/Stop/Manuelle Erfassung), die auf die Konfiguration zugreift.
Ziel: Jeder Entwickler soll daraus direkt erkennen, wie die Daten zusammenhängen und wo im Ablauf welche Eingaben erforderlich sind.

A) KONFIGURATIONSBEREICH
(Hier legt man alle relevanten Daten an oder bearbeitet sie. Die Zeiterfassung greift später direkt auf diese Daten zu.)

1) Kundenübersicht (Externe Projekte)
plaintext
Code kopieren
Kundenübersicht
├── Kunde_A (bearbeiten)
│   ├── Projekt_A1 (bearbeiten)
│   │   ├── Category_Options:
│   │   │   ├── Category_A: [Category] (bearbeiten)
│   │   │   ├── Category_B: [Category] (bearbeiten)
│   │   │   └── + weitere Kategorien hinzufügen
│   │   ├── Chargeable
│   │   │   └── Project ID: [Project ID] (bearbeiten)
│   │   └── Non-Chargeable
│   │       └── Project ID: [Project ID] (bearbeiten)
│   ├── Projekt_A2 (bearbeiten)
│   │   ├── Category_Options:
│   │   │   ├── Category_A: [Category] (bearbeiten)
│   │   │   ├── Category_B: [Category] (bearbeiten)
│   │   │   └── + weitere Kategorien hinzufügen
│   │   ├── Chargeable
│   │   │   └── Project ID: [Project ID] (bearbeiten)
│   │   └── Non-Chargeable
│   │       └── Project ID: [Project ID] (bearbeiten)
│   └── + weiteres Projekt hinzufügen

├── Kunde_B (bearbeiten)
│   ├── Projekt_B1 (bearbeiten)
│   │   ├── Category_Options:
│   │   │   ├── Category_A: [Category] (bearbeiten)
│   │   │   ├── Category_B: [Category] (bearbeiten)
│   │   │   └── + weitere Kategorien hinzufügen
│   │   ├── Chargeable
│   │   │   └── Project ID: [Project ID] (bearbeiten)
│   │   └── Non-Chargeable
│   │       └── Project ID: [Project ID] (bearbeiten)
│   └── + weiteres Projekt hinzufügen

└── + weiteren Kunden hinzufügen
Zweck: Definiert alle externen Projekte (pro Kunde), deren Kategorien sowie Project IDs für Chargeable bzw. Non-Chargeable.
Wichtig:
Die Project IDs für Chargeable und Non-Chargeable können unterschiedlich sein.
Category_Options enthalten die unterschiedlichen Job-Bezeichnungen, die später in der Zeiterfassung auswählbar sind.
2) Abwesenheit (Project ID: 890085)
plaintext
Code kopieren
Abwesenheit (Project ID: 890085)
Required Entries:
├── Uni Zeit
│   ├── Category: H03147 - Other Paid Time off
│   └── Notes: Während der Uni müssen weiterhin Stunden gebucht werden ...
├── Krankheitstage
│   └── Category: H03128 - Sickness Leave
├── Urlaub
│   └── Category: H03118 - Holiday
└── Feiertag/Wellness Day
    ├── Category: H03003 - Time off - Paid absence / non-holiday
    └── Notes: External comment erforderlich ("Bank holiday" oder "Wellness Day")
Zweck: Definiert alle möglichen Abwesenheitstypen (Uni Zeit, Krankheit, Urlaub, Feiertag …), jeweils mit festem Category-Wert und evtl. zusätzlichen Hinweisen.
Project ID = 890085 – wird später in der Zeiterfassung bei Auswahl „Abwesenheit“ automatisch hinterlegt.
3) Arbeitszeit im Unternehmen (Project ID: 890023)
plaintext
Code kopieren
Arbeitszeit im Unternehmen (Project ID: 890023)
Required Entries:
├── Ausbildungszeit
│   ├── Category: H03107 - Internal - Professional development ...
│   └── Notes: Dokumentation von Tutorials ...
├── Projektarbeit/One2One
│   └── Category: H03108 - Internal - Career development ...
├── Interne Meetings
│   ├── Category: H03104 - Internal - Non-client / internal meeting
│   └── Notes: Spezifizierung erforderlich ...
└── Interne Arbeit
    └── Category: H03105 - Internal - Non-client operational activities
Zweck: Definiert interne Arbeitszeiten (z. B. Ausbildungszeit, Meetings …) inkl. vordefinierter Categories und Notes.
Project ID = 890023 – wird später verwendet, wenn der Eintragstyp „Arbeitszeit im Unternehmen“ gewählt wird.
B) ZEITERFASSUNG
(Das ist die Nutzeroberfläche, in der Zeiten erfasst werden. Sie greift auf die obige Konfiguration zurück.)

Überblick der 3 Haupttypen bei der Zeiterfassung
Kundenprojekt
Projektauswahl (Kunde → Projekt)
Kategorie
Chargeable / Non-Chargeable (jeweils andere Project ID in der Config)
Abwesenheit (Project ID: 890085)
Auswahl eines Abwesenheitstyps (Uni Zeit, Krankheit, Urlaub, Feiertag …)
Category & Notizen sind bereits in der Config definiert und werden teils automatisch befüllt (oder angezeigt).
Arbeitszeit im Unternehmen (Project ID: 890023)
Auswahl eines internen Typs (Ausbildungszeit, Meetings, …)
Category und Notes laut Config.
1) TIMER STARTEN
plaintext
Code kopieren
Zeiterfassung → [Button: "Start Timer"]

┌── Pop-up "Neuen Eintrag starten" ──────────────────────────────────────────┐
│  A) Auswahl des Eintragstyps (Pflicht):                                   │
│     1) Kundenprojekt                                                      │
│        - Kunde wählen (Dropdown: Kunde_A, Kunde_B, ...)                   │
│          -> Projekte zeigen (z. B. Projekt_A1, Projekt_A2)                │
│        - Projekt wählen (abhängig von gewähltem Kunden)                   │
│          -> Zeigt zugehörige Category_Options (Category_A, B, ...)        │
│        - Kategorie wählen (Pflicht)                                       │
│        - Chargeable ODER Non-Chargeable (Pflicht)                         │
│          -> Interne Zuordnung zur richtigen Project ID                    │
│        - Optional: Notizen hinzufügen                                     │
│                                                                           
│     2) Abwesenheit (Project ID: 890085)                                   │
│        - Typ wählen (Uni Zeit, Krankheit, Urlaub, Feiertag …)             │
│          -> Je nach Typ werden Category/Notes automatisch gesetzt         │
│        - Optional: Freitext-Note ergänzen                                  │
│                                                                           
│     3) Arbeitszeit im Unternehmen (Project ID: 890023)                    │
│        - Interner Typ wählen (z. B. Ausbildungszeit, Meetings …)          │
│          -> Category und evtl. vorgegebene Notes werden aus Config geholt │
│        - Optional: Freitext-Note ergänzen                                  │
│                                                                           
│  B) [Button: "Timer starten"]                                             │
│    -> Legt den neuen Eintrag mit gewählten Parametern an und startet die   │
│       Zeitmessung.                                                        │
└────────────────────────────────────────────────────────────────────────────┘
Wichtige Abhängigkeiten:

Für Kundenprojekt:
Im Dropdown „Kunde“ nur Werte aus Kundenübersicht.
Bei „Projekt“ nur die Projekte des gewählten Kunden.
Bei „Kategorie“ nur die in Category_Options definierten Kategorien zu diesem Projekt.
Chargeable oder Non-Chargeable entscheidet, welche Project ID intern verwendet wird (z. B. 123456 vs. 654321).
Für Abwesenheit: Fixe Project ID (890085); bei „Typ“ nur die unter Abwesenheit hinterlegten Werte.
Für Arbeitszeit: Fixe Project ID (890023); bei „Interner Typ“ nur die vordefinierten Optionen (Ausbildungszeit, …).
2) TIMER LÄUFT
plaintext
Code kopieren
- Der Timer wird prominent angezeigt (z. B. 00:12:45).
- Angezeigte Metadaten (abhängig vom gewählten Eintragstyp):
  - Kundenprojekt -> Kunde, Projekt, Kategorie, Chargeable/Non-ch. 
  - Abwesenheit   -> Typ (Uni Zeit, Urlaub, …)
  - Arbeitszeit   -> Interner Typ (Ausbildungszeit, Meetings …)
- Buttons:
  ├ [Pause/Resume]: Timer anhalten oder fortsetzen
  ├ [Bearbeiten]:   Öffnet obiges Pop-up erneut, mit vorausgefüllten Feldern
  └ [Stop]:         Beendet den Timer
Abhängigkeiten:

Beim Bearbeiten muss erneut auf die Konfiguration zugegriffen werden, falls der Nutzer den Typ oder Kunde/Projekt/Kategorie wechselt.
3) STOP-TIMER
plaintext
Code kopieren
[Button: "Stop"] → beendet Timer

┌── Pop-up "Zeit erfassen/prüfen" ──────────────────────────────────────────┐
│ - Start-/Endzeit werden angezeigt und können manuell korrigiert.         │
│ - Eintragstyp & Detailfelder (Kunde, Projekt, Typ, ...) können ggf.       │
│   nochmal bearbeitet werden.                                             │
│ - Notizen können ergänzt werden.                                         │
│                                                                          │
│ [Button: "Speichern"]                                                    │
│   -> Speichert den Eintrag endgültig in der Datenbank (o.ä.).            │
└────────────────────────────────────────────────────────────────────────────┘
