# 🔌 PlugAndPlan: The Hybrid Project Board

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hardware](https://img.shields.io/badge/Hardware-ESP32-blue.svg)]()
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)]()
[![Integration](https://img.shields.io/badge/Integration-Miro_API-ff69b4.svg)]()

**PlugAndPlan** ist ein Open-Source-Projekt für ein hybrides Projektplanungsboard. Es verbindet die haptischen Vorteile eines analogen Scrum-Boards mit der automatisierten, digitalen Dokumentation in [Miro](https://miro.com/). 

Entwickelt nach der Konstruktionsmethodik **VDI 2221**, eliminiert dieses System Medienbrüche und Doppelarbeit im Product Engineering. Anstatt fehleranfälliger Kamera- oder OCR-Systeme nutzt PlugAndPlan eine robuste Hardware-Schnittstelle (Buchsen-Matrix).

---

## ✨ Features

* **Echtzeit-Synchronisation:** Physische Planungselemente werden in unter 5 Sekunden in Miro gespiegelt.
* **100% Zuverlässig:** Keine Bilderkennungsfehler. Jedes Task-Element wird über eine weltweit eindeutige 64-Bit-ID (ausgelesen über integrierte Temperatursensoren) hardwareseitig verifiziert.
* **Logisches Patching:** Physisches Verbinden von Tasks mit Bananenkabeln erzeugt automatisch logische Verbindungslinien (Pfeile) im digitalen Miro-Board.
* **Plug & Play:** Einfaches Einstecken reicht – der ESP32 erkennt Identität und Position (Koordinaten) sofort.

---

## 🛠️ Systemarchitektur

Das System besteht aus zwei Hauptkomponenten:

1. **Hardware (Das Board):** Eine Matrix aus Klinken-Einbaubuchsen, verwaltet von einem **ESP32-Mikrocontroller**, der durch Multiplexer (für die Ports) und IO-Expander (für das Patching) erweitert wurde.
2. **Software (Die Bridge):** Ein modulares Python-Backend, das die Sensordaten per WLAN vom ESP32 empfängt, die logische Positionierung berechnet und über einen API-Token mit dem Miro-Board kommuniziert.

---

## 📦 Hardware-Bedarf (BOM)

Um dieses Board nachzubauen, benötigst du (für das MVP):
* 1x ESP32 Mikrocontroller (mit WLAN)
* Multiplexer (Anzahl abhängig von der Board-Größe, 15 Ports pro Einheit)
* IO-Expander (für die Patch-Kabel-Erkennung)
* Klinken-Einbaubuchsen & entsprechende Stecker
* Temperatursensoren (als kostengünstige 64-Bit-ID Träger in den Steckern)
* Bananenkabel (für Patching-Verbindungen)
* Pressspanplatte (als Trägermatrix)

---

## 🚀 Installation & Setup

### 1. Miro API vorbereiten
1. Erstelle eine Developer-App in Miro.
2. Generiere einen **API Access Token** mit Schreibrechten für Boards.
3. Notiere dir die `BOARD_ID` deines Ziel-Boards.

### 2. Software Setup
Klone dieses Repository und installiere die Abhängigkeiten:

```bash
git clone [https://github.com/DeinUsername/PlugAndPlan.git](https://github.com/DeinUsername/PlugAndPlan.git)
cd PlugAndPlan
pip install -r requirements.txt
