# UMTS/WCDMA Handover Simulator

A web-based simulation tool for analyzing handover mechanisms in UMTS/WCDMA mobile networks using Python and Flask.

## Project Overview

This project simulates the behavior of a mobile user moving between two Node B base stations in a UMTS/WCDMA network. It provides a graphical interface to analyze radio signal quality and handover events throughout the user's trajectory.

The simulator focuses on the relationship between radio measurements, handover decisions, and service continuity.

## Objectives

- Analyze the received signal code power (RSCP) and Ec/No.
- Visualize the radio conditions of two neighboring cells.
- Study the Active Set and serving-cell changes.
- Detect and analyze Soft Handover and Hard Handover events.
- Identify Ping-Pong handover behavior.
- Investigate service interruptions (Drop) under different simulation conditions.

## Simulated Scenarios

### 1. Normal Handover

Study the transition between neighboring cells and observe the Soft Handover region, where the mobile can maintain connections with multiple cells.

### 2. Ping-Pong Handover

Analyze rapid and repeated transitions between two cells, where the serving cell changes from A to B and then back to A within a short time interval.

### 3. Hard Handover

Study a direct transition from one serving cell to another, where the connection to the source cell is released before the target connection is established.

### 4. Service Interruption (Drop)

Investigate conditions in which neither cell provides sufficient radio quality to maintain the connection.

## Technologies Used

- **Python** — Simulation and numerical calculations
- **NumPy** — Numerical computations and radio measurements
- **Flask** — Web application and API
- **HTML5** — Web interface
- **CSS3** — Interface styling
- **JavaScript** — Interactive behavior and visualization

## Project Structure

```text
umts-handover-simulator/
├── app.py
├── simulation.py
├── handover.py
├── propagation.py
├── requirements.txt
├── .gitignore
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

## Installation and Execution

### Prerequisites

- Python 3.10 or a compatible version
- Git
- pip

### 1. Clone the repository

```bash
git clone https://github.com/Abdoul-fath/umts-handover-simulator.git
cd umts-handover-simulator
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
```

Activate it in Command Prompt:

```bash
.venv\Scripts\activate
```

Or in Git Bash:

```bash
source .venv/Scripts/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

### 5. Open the interface

Open your browser and navigate to:

```text
http://127.0.0.1:5000
```

The application will be available locally while the Flask server is running.

## Main Radio Parameters

The simulator can be used to study the impact of parameters such as:

- Distance between Node B stations
- Mobile speed and trajectory
- Transmission power
- Handover addition and removal thresholds
- Hysteresis
- Shadowing and decorrelation distance
- Time-to-Trigger (TTT)
- Random seed

The available parameters depend on the implemented simulation configuration.

## Project Limitations

This project is an educational simulation of selected UMTS/WCDMA handover mechanisms. Its results depend on the propagation model, radio-quality calculations, and handover algorithms implemented in the source code.

It is not a complete 3GPP-compliant network simulator and does not replace measurements from a real mobile network.

## Academic Context

This project was developed as part of an engineering academic project focused on mobile telecommunications networks and UMTS/WCDMA handover mechanisms.

## Author

**Abdoul-Fatah Omar Hassan**

Engineering student — Telecommunications and Networks Systems

National School of Applied Sciences of Tetouan (ENSA Tétouan)

## Repository

GitHub: https://github.com/Abdoul-fath/umts-handover-simulator
