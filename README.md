# Small-Scale Underwater Remotely Operated Vehicle (ROV) for Research Applications

## About The Project

This repository contains the design, software, and documentation for the development of a small-scale, research-grade Remotely Operated Vehicle (ROV). The primary objective of this project is to create a fully operational vehicle to be used for demonstrations at the Queensland University of Technology (QUT) and to serve as a testbed for novel Machine Learning (ML) control pipelines.

The project addresses a gap in the availability of compact, low-cost, and modular ROV platforms suitable for educational and research environments. It investigates and implements hardware and software solutions to achieve robust functionality in a small form factor, a challenge not fully addressed by larger, commercial systems.

## Key Features

* **Modular Design:** An open-frame chassis allows for the easy mounting of sensors, payloads, and thrusters, simplifying maintenance and adaptation for future research.
* **Machine Learning Ready:** Equipped with a companion computer capable of running ML pipelines for object detection, classification, and developing autonomous routines.
* **Compact and Maneuverable:** The design focuses on a small form factor while incorporating a thruster configuration that allows for the performance of complex maneuvers.
* **Robust Control System:** Utilizes the PX4 open-source autopilot software on a Pixhawk 6 for stable control and straightforward integration with the user interface and ML pipelines.

## Hardware

The ROV is constructed using a combination of off-the-shelf and custom-designed components to balance performance, cost, and modularity.

| Component | Description |
| :--- | :--- |
| **Companion Computer** | Raspberry Pi 5: Used for high-level processing, including communicating with the ground station, processing image data, and executing pathfinding and ML algorithms. |
| **Autopilot** | Pixhawk 6: Manages thruster control, interfaces with the IMU for orientation, and uses a barometer for depth control. It runs the PX4 autopilot software. |
| **Thrusters** | BlueRobotics T200: Selected for their reliability, thrust-to-weight ratio, and ease of integration with the Pixhawk 6. |
| **Frame & Enclosure** | A hybrid design featuring an aluminum open-frame chassis for mounting components and a BlueRobotics acrylic enclosure to house and waterproof the core electronics. |
| **Imaging** | Raspberry Pi Camera Module 3: Provides the visual data stream for manual operation and for the machine learning pipeline. |
| **Communication**| Fathom-X module for wired communication and an audio-based module for wireless communication.|
| **Power System** | A dedicated power management board and batteries designed to provide approximately one hour of operational time. |

## Software Stack

The software architecture is designed for modularity and to leverage existing, well-supported frameworks, facilitating rapid development and future expansion.

* **Autopilot Firmware:** PX4 is used on the Pixhawk 6 for real-time flight control and sensor integration.
* **High-Level Control:** Python is the primary language for developing the ML pipeline and high-level control logic on the Raspberry Pi 5.
* **Operating System:** The companion computer will run a Linux-based OS to support integration with PX4 and potential future use of the Robot Operating System (ROS 2).
* **Simulation & Modelling:** MATLAB/Simulink will be used for initial control system modelling and simulation before physical testing.
* **User Interface:** A basic Graphical User Interface (GUI) will be developed for manual vehicle operation.

## Project Structure

The project follows a systems engineering approach, structured into several key phases:

1.  **Literature Review & Planning:** A comprehensive review of existing small-scale ROV designs to inform the project's direction.
2.  **Detailed Design:** Creation of complete CAD models, electrical schematics, and a bill of materials.
3.  **Procurement & Assembly:** Sourcing components and constructing the mechanical frame and electronics enclosures.
4.  **Integration:** Installation of electronics and development of the software for manual control.
5.  **Testing & Validation:** A multi-stage testing process including static waterproofing tests, dynamic maneuverability tests, and performance validation in a controlled water environment.
6.  **Final Reporting:** Comprehensive documentation of the design, methodology, and results.

## Project Deliverables

The final deliverables for this project include:

1.  A fully assembled and operational small-scale underwater ROV.
2.  Complete CAD drawings and electrical schematics.
3.  The control system software, including a basic GUI for manual operation.
4.  A set of performance metrics demonstrating the ROV's capabilities.
5.  A basic automation pipeline for ML model training and inference.
6.  A final project report detailing the design process and results.

## Author

* **Joshua Hecke** - *Student Engineer* - n11585382

## Acknowledgments

* This project is submitted in partial fulfillment of the requirements for the EGH400 - Research Project 1 unit.
* Queensland University of Technology (QUT), Faculty of Engineering.
