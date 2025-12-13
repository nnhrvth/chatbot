# MediMini – Smart Medication Assistant (Streamlit)

MediMini ist eine einfache Webanwendung zur Verwaltung von Medikamenteneinnahmen.
Die Anwendung erkennt potenzielle zeitliche Wechselwirkungen zwischen Medikamenten
und schlägt automatische Anpassungen des Einnahmeplans vor.

Dieses Projekt wurde als Hands-On Software-Engineering-Projekt umgesetzt und dient
als Demonstrationsbeispiel für modulare Architektur, Testbarkeit und saubere
Trennung von Verantwortlichkeiten.

> Hinweis: Dieses Projekt ist ein Demonstrationssystem und ersetzt keine
> medizinische Beratung.

---

## Zielsetzung

Ziel der Anwendung ist es, Benutzerinnen und Benutzer bei der Planung ihrer
Medikamenteneinnahme zu unterstützen, indem potenziell kritische Einnahmezeitpunkte
erkannt und aufgelöst werden.

**Zielgruppe**
- Studierende
- Lehrveranstaltungen
- Software-Engineering-Demonstrationen

---

## Funktionsumfang

### Implementierte Funktionen
- Hinzufügen von Medikamenten mit Einnahmezeiten
- Anzeige eines Einnahmeplans
- Erkennung zeitlicher Konflikte zwischen Medikamenten
- Automatische Generierung von Lösungsvorschlägen
- Anwendung von Vorschlägen mit Persistenz
- Lokale Datenspeicherung mittels JSON-Dateien

### Nicht implementiert
- Medizinische Validierung
- Externe APIs oder Datenbanken
- Benutzer-Authentifizierung

---

## Architektur und Technologien

### Architekturprinzipien
- Trennung von Benutzeroberfläche und Geschäftslogik
- Modularer Aufbau
- Hohe Testbarkeit
- Single Responsibility Principle

### Technologiestack
- Programmiersprache: Python
- Benutzeroberfläche: Streamlit
- Datenhaltung: JSON
- Tests: pytest
- Versionskontrolle: Git und GitHub

### Architekturübersicht

```text
UI (Streamlit)
   |
   v
Business Logic
(rule_engine, suggestion_engine)
   |
   v
Persistence Layer
(storage)
