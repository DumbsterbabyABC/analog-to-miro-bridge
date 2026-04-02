# 🔌 PlugAndPlan: The Hybrid Project Board

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hardware](https://img.shields.io/badge/Hardware-ESP32-blue.svg)]()
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)]()
[![Integration](https://img.shields.io/badge/Integration-Miro_API-ff69b4.svg)]()

**PlugAndPlan** is an open-source hardware and software bridge for hybrid project management. It combines the tactile benefits of an analog Scrum board with automated, digital documentation in [Miro](https://miro.com/). 

Engineered according to the **VDI 2221** design methodology, this system eliminates media breaks and duplicate data entry in product engineering. Instead of relying on error-prone computer vision or OCR systems, PlugAndPlan utilizes a robust hardware interface (a physical jack matrix).

---

## ✨ Features

* **Real-Time Synchronization:** Physical planning elements are mirrored in Miro in under 5 seconds.
* **100% Reliable Tracking:** Zero computer vision errors. Each task element is hardware-verified via a globally unique 64-bit ID (read through repurposed integrated temperature sensors).
* **Logical Patching:** Physically connecting tasks on the board with banana cables automatically generates logical relationship lines (arrows) in the digital Miro workspace.
* **Plug & Play:** Simply plug a task in – the ESP32 instantly recognizes its identity and spatial coordinates.

---

## 🛠️ System Architecture

The system consists of two main components:

1. **Hardware (The Board):** A matrix of panel-mount audio jacks managed by an **ESP32 microcontroller**. The IO capacity is expanded using multiplexers (for the grid ports) and IO expanders (for the patching logic).
2. **Software (The Bridge):** A modular Python backend that receives sensor data from the ESP32 via Wi-Fi, calculates the logical positioning, and communicates with the Miro board via an API token.

---

## 📦 Bill of Materials (BOM)

To build the MVP of this board, you will need:
* 1x ESP32 Microcontroller (Wi-Fi enabled)
* Multiplexers (Quantity depends on board size; 16 ports per unit)
* IO Expanders (for patch cable detection)
* Audio jacks (panel mount) & matching plugs
* Digital Temperature Sensors (used purely as low-cost 64-bit ID carriers inside the plugs)
* Banana cables (for patching connections)
* Particle board / MDF (as the physical base matrix)

---

## 🚀 Installation & Setup

### 1. Prepare the Miro API
1. Create a Developer App in Miro.
2. Generate an **API Access Token** with board read/write permissions.
3. Note down the `BOARD_ID` of your target Miro board.

### 2. Software Setup
Clone this repository and install the dependencies:

```bash
git clone [https://github.com/YourUsername/PlugAndPlan.git](https://github.com/YourUsername/PlugAndPlan.git)
cd PlugAndPlan
pip install -r requirements.txt
