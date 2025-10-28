<p align="center">
  <img src="/Documentation/images/logo.png" alt="QUT Logo" width="300"/>
</p>

> The Queensland University of Technology (QUT) acknowledges the Turrbal and Yugara, as the First Nations owners of the lands where QUT now stands. We pay respect to their Elders, lores, customs and creation spirits. We recognise that these lands have always been places of teaching, research and learning.
>
> QUT acknowledges the important role Aboriginal and Torres Strait Islander people play within the QUT community. [cite: 452]

# SubbyROV: A Small-Scale Underwater ROV

| ![Final SolidWorks Render (Design #4)](/CAD/Renders/Full.gif) | ![Final SolidWorks Render (Design WTE #4)](/CAD/Renders/WTE.gif) |
| :---: | :---: |
| *Final SolidWorks Render (Design #4)* | *Final SolidWorks Render (Design WTE #4)* |
| ![Initial prototyping workspace and components](/Documentation/images/workshop) | ![Test-fitting the internal electronics tray](/Documentation/images/progress.jpg) |
| *Initial prototyping workspace and components* | *Test-fitting the internal electronics tray* |

## About the SubbyROV Project

This project, part of the EGH400 Research Project at Queensland University of Technology (QUT), documents the development of a small-scale, research-grade Remotely Operated Vehicle (ROV).

This repository will serve as the open-source hub for the project, containing all design specifications, CAD models, software, and simulation files.

### Motivation

While QUT possesses a capable BlueROV2, its large size, complex handling, and setup requirements (e.g., pool approval) make it impractical for rapid prototyping, small-scale tests, or educational demonstrations .

This project aims to fill that gap by creating a highly modular, cost-effective, and compact ROV. The primary objective is to build a fully operational vehicle that can serve as:

1.  A versatile testbed for novel Machine Learning (ML) control pipelines.
2.  An accessible and portable platform for QUT open days and demonstrations.

### At a Glance

The SubbyROV is designed from the ground up to be small, agile, and computationally capable, using a mix of Commercial-Off-The-Shelf (COTS) and custom 3D-printed parts.

| Specification | Details |
| :--- | :--- |
| **Project Name** | SubbyROV  |
| **Structure** | Blue Robotics 3" watertight enclosure on a custom aluminum Item profile frame. |
| **Propulsion** | 4 x APISQUEEN U2 MINI thrusters with external waterproof ESCs. |
| **Configuration** | Experimental 45-45 degree vectored thruster layout. |
| **Main Controller** | Pixhawk 6X flight controller. |
| **Software** | ArduSub firmware communicating via MAVLink protocol. |
| **Camera** | Z-1 Mini gimballed camera. |
| **Communication** | Fathom-X Tether Interface Boards for Ethernet-over-tether. |
| **Power** | Tattu 5200mAh 4S (14.8V) LiPo Battery. |
| **Est. Runtime** | ~32 minutes (at typical cruising draw). |
| **Est. Cost** | ~$2,900 - $3,000 AUD. |

## Project Status

**Current Status:** Phase 1 (Research and Design) is complete. The project is now actively in **Phase 2: Assembly and System Integration**.

### Key Milestones Achieved

* **Literature Review:** A comprehensive review of existing ROV designs was completed to inform key design philosophies.
* **Design Iterations:** The project progressed through four major design iterations in SolidWorks, pivoting from an initial 6-thruster concept to the final, compact 4-thruster design to meet strict size and power constraints .
* **Final CAD Model:** A complete, detailed CAD assembly of the final design has been produced.
* **Procurement:** A full Bill of Materials (BOM) has been finalized. All critical long-lead components (Pixhawk 6X, thrusters, enclosure) have been procured and received.
* **Initial Prototyping:** The internal electronics tray has been 3D-printed and assembled with the core components to test-fit and validate the SolidWorks design.
* **Safety:** A comprehensive Risk Assessment (ID: 18339) has been submitted to the QUT HSE Hub, covering electrical, operational, and battery-handling hazards.

### Next Steps

The project is now transitioning from the theoretical design phase to physical construction and validation.

1.  **Phase 2: Assembly & System Integration**
    * Complete the full physical assembly of the aluminum frame, thrusters, and watertight enclosure.
    * Wire all internal electronics (Pixhawk, PDB, Fathom-X) and seal all cable penetrators.
    * Flash the Pixhawk controller with ArduSub firmware and establish a communication link with the ground station.
    * Simulate the ROV in ROS2/Gazebo using a URDF model to validate control algorithms and buoyancy.
    * Design and add custom buoyancy modules based on the final assembled mass.

2.  **Phase 3: Testing & Validation**
    * Conduct initial waterproofing and leak tests in a controlled tank.
    * Ballast the ROV to achieve neutral buoyancy and a stable trim.
    * Perform system identification and tune PID control loops for stable depth-holding and heading-holding.
    * Validate the ROV's performance against the original project objectives.

## Repository Contents

This repository will be populated as the project progresses and will contain:

* **/CAD:** All SolidWorks 2023 part files, assembly files, and technical drawings for the final design.
* **/URDF:** Robot Operating System (ROS2) models and Gazebo simulation files.
* **/Software:** Configuration files for the ArduSub firmware and any custom control software.
* **/Documentation:** The final project report, Bill of Materials (BOM), and assembly guides.

## The Team

![Photo of Joshua Hecke](/Documentation/images/profileB.jpg)
* **Student Engineer:** Joshua Hecke (Queensland University of Technology) 

![Photo of Tobias Fischer](/Documentation/images/profileA.jpg)
* **Project Supervisor:** Tobias Fischer (Queensland University of Technology) 