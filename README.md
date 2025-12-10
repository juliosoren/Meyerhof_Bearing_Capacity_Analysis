# Automation of the Bearing Capacity Calculation (Meyerhof, 1963)

## 🧭 Table of Contents

1.  Introduction
2.  Project Summary
3.  Execution Guide (Workflow)
    * 3.1 OPTION 1: Online Execution (Google Colab - Recommended)
    * 3.2 OPTION 2: Local Execution
4.  Nomenclature and Data Structure
    * 4.1 Nomenclature and Data Structure
    * 4.2 Input File Worksheets (Tabs) (`Geotech_InputData.xlsx`)
    * 4.3 Detail of Cells in `Geotech_InputData.xlsx`
        * 4.3.1 `geotechnical_input` Sheet (Global Parameters and Strata)
        * 4.3.2 `footing_configuration` Sheet (Structural Check)
5.  Output Files
6.  Limitations and Scope of Analysis
7.  Version Control and Roadmap
8.  Technical and Bibliographical References
9.  Contribution


---



## 📝 Introduction

This project delivers an automated tool for the analysis and verification of the bearing capacity of shallow foundations, intended for professional use in geotechnical engineering and for integration into reproducible workflows.  
The solution is designed to process stratigraphic characterizations, explore geometric combinations (width, depth, aspect ratio), and compare results under traditional safety factor criteria and under LRFD.  
The purpose is to reduce repetitive tasks, minimize calculation errors, and provide documented outputs (tables and graphs) that facilitate decision-making during the design phase.  




## 🌟 Project Summary

This repository offers a modular and automated Python solution for the geotechnical design of shallow foundations (footings). The project implements Meyerhof's Ultimate Bearing Capacity theory (1963) and considers specialized analyses:

-**Safety Factors**: Support for classical safety factors (Bowles) and the Load and Resistance Factor Design (LRFD) methodology, such as that proposed by AASHTO 2020.  
-**Two-Layer Capacity**: Includes checking the capacity in two-layer strata, which is critical when the bearing layer is thin and the underlying layer affects the failure mechanism.  
-**Heterogeneous Stratigraphy**: Allows the evaluation of the embedment depth capacity in different strata along the depth.  

The automated workflow performs:
1.  **Data Loading:** Reading of strata parameters and geometric configurations from an Excel file (`Geotech_InputData.xlsx`).
2.  **Calculation:** Generation of the combinations table ($\text{D}_\text{f}$, $\text{B}$, $\text{L}$) with allowable bearing capacity.
3.  **Structural Check:** Verification of the footings proposed by structural design.
4.  **Reporting:** Exporting tabular and graphical results to Excel files.



---

## 🛠️ Execution Guide (Workflow)

1️⃣ OPTION 1: Online Execution (Google Colab - Recommended)

This project is configured for seamless execution in Google Colab, allowing you to upload your data directly from your local machine, run the analysis, and download the results automatically.

* **Prepare Data and Open Notebook**:
  * Download and Edit: Download the example input file `Geotech_InputData.xlsx` and the execution file `Run_Meyerhof_Bearing_Capacity.ipynb` rom the $\text{data/}$ folder. Modify the `Geotech_InputData.xlsx` file with your own data.
  * Open the Notebook: Upload and open the `Run_Meyerhof_Bearing_Capacity.ipynb` file directly in Google Colab.

* **Run the Analysis (3 Steps in Colab)**:  
  The Colab notebook is split into three executable cells:  
  |Step|Action|Description|
  | :--- | :--- | :--- |
  |1| Initialization|Runs the initial setup and defines project variables.|
  |2|Interactive Upload (User Action)|CRITICAL: Click the "Choose Files" button that appears and upload your modified `Geotech_InputData.xlsx` file from your computer.|
  |3|Execute and Download|Automatically performs the following sequence: clones the repository, installs dependencies, runs the main analysis script using your uploaded data, and initiates the download of the final Excel reports to your machine.|

* **Development & Automation**: This project is configured for local execution via command line and for continuous automation via GitHub Actions.
  


2️⃣ OPTION 2: Local Execution
For developers or those who prefer working in a local environment (VS Code, Jupyter).


1. **Prerequisites**: Ensure you have Python 3.8+ installed.

2. **Dependency Installation:**: Use the `requirements.txt` file to install all the necessary external libraries:

```bash 
pip install -r requirements.txt
```
3. **Analysis Execution**: Run the main script ($\text{main.py}$) from the project root, specifying the relative path to the input file:

```bash 
python src/main.py data/Geotech_InputData.xlsx
```
---
### 📂 Nomenclature and Data Structure
---

#### 1. **Nomenclature and Data Structure**: Ensure the input file is correctly located:

```bash 
/meyerhof_bearing_capacity/
├── data/
│   └── Geotech_InputData.xlsx  <-- INPUT FILE
└── src/
    └── main.py                 <-- EXECUTION SCRIPT
    └── data_io.py 
    └── geotechnical_params.py 
    └── capacity_calc.py
    └── plotting.py  
```


#### 2. **Input File Worksheets (Tabs)** (Geotech_InputData.xlsx)  


| Nombre Hoja | Descripción |   
| :--- | :--- |  
|**geotechnical_input**| Strata properties, WT (Water Table, $\text{Nivel Freatico}$) and global parameters. |   
|**footing_configuration**| Configuration of the structural footings to be checked.|  

#### 3. Detail of Cells in `Geotech_InputData.xlsx`

#### 3.1  `geotechnical_input` Sheet (Global Parameters and Strata)

| Field | Description and Units | Important Notes |
| :--- | :--- | :--- |
| **Project Name** | Project name. | |
| **Design Code** | Selection of the safety method. | Drop-down list between: **Bowles\_FS\_3.0** (Factor of Safety) or **AASHTO 2020** (Load and Resistance Factor Design). |
| **GWL** | Groundwater Level depth. | Measured from the surface (meters, **m**). |
| **Df Values** | Embedment Depths ($\text{D}_\text{f}$) to be Evaluated. | Enter the desired values (meters, **m**). 'n' columns are supported. |
| **B Values** | Foundation Widths ($\text{B}$) to be Evaluated. | Enter the desired values (meters, **m**). 'n' columns are supported. |
| **Stratum ID** | Stratum Identifier. | **MUST** be strictly consecutive: `"Stratum 1", "Stratum 2", "Stratum n"` |
| **Stratum Description** | Stratum Description. | Name given in the geotechnical characterization. |
| **Initial Depth** | Stratum Initial Depth. | (meters, **m**)|
| **Final Depth** | Stratum Final Depth. | (meters, **m**) |
| **Unit Weight Moist** | Moist Unit Weight of the Stratum. | (kN/m³) |
| **Unit Weight Saturated** | Saturated Unit Weight of the Stratum. | (kN/m³) |
| **Cohesion** | Effective Cohesion. | (kPa) |
| **Friction Angle** | Effective Friction Angle. | (Degrees, **°**) |

> **Note for Undrained Parameters:** For undrained evaluation, enter the value of the **Undrained Shear Strength** (`Su`) in the **Cohesion** cell, and set the **Friction Angle** equal to zero ($\phi=0$).

#### 3.2  `footing_configuration` Sheet (Structural Check)

| Field | Description and Units |
| :--- | :--- |
| **Support Name** | Name given in the structural design to the support or foundation to be evaluated. |
| **Footing Base** | Foundation Width ($\text{B}$) in meters, (**m**) |
| **Footing Length** | Foundation Length ($\text{L}$). in meters, (**m**) |
| **Embedment Depth** | Embedment Depth ($\text{D}_\text{f}$) in meters, (**m**) |
| **Design Load** | Structural Axial Load (or Ultimate Design Load) in kiloNewtons, (**kN**) |


---
### 📊 Output Files
---
The results are generated in the $\text{output/}$ folder:  
1. **Results_Bearing_Capacity.xlsx**: Tabular DataFrames of capacities per combination ($\text{D}_\text{f}$, $\text{B}$, $\text{L}$) and checks.  
2. **Charts_bearing_capacity.xlsx:** Generated plots using Matplotlib/Seaborn.  

---
### ⚠️ Limitations and Scope of Analysis
---
It is crucial to understand the boundaries of this tool to prevent its incorrect use in design. The following are the main limitations of Version 1.0:  


1. **Eccentricity and Moment**: The model does not evaluate load eccentricity or moments applied to the foundation. It is assumed that the structural axial load is applied at the footing's centroid.  
2. **Ground Inclination**: The calculation of the bearing capacity does not consider the inclination or slope of the surrounding ground or the ground beneath the foundation. It is assumed that the ground is horizontal.  
3. **Uniform Stratigraphy**: The analysis assumes that the stratigraphy provided in the geotechnical_input sheet applies to all foundation combinations being evaluated.   
4. **Two-Layer System (Critical Restriction)**:For the Two-Layer capacity check to function, there must be at least one complete stratum below the embedment depth ($\text{D}_\text{f}$). If the embedment depth falls exactly on the last layer of the stratigraphy, the system will generate errors when attempting to interpolate the underlying stratum. Ensure that the stratigraphy reaches the necessary depth.


---
### 🔄 Version Control and Roadmap
---
This project is managed under a clear version control scheme to ensure continuous improvement and traceability of functionalities.  

| Version | Status | Scope and Objective |
| :--- | :--- | :--- |
|**v1.0** |CURRENT |**Initial Release**. Implementation of Meyerhof, two-layer capacity, structural check, and full workflow automation (CI/CD via GitHub Actions). Warning: May contain errors if not executed strictly according to the README. |
|**v2.0** |Next |**Robustness and Usability**. Focused on correcting reported bugs, improving user experience (UX), and implementing error-proof validations (`try/except`) for inconsistent data. |
|**v3.0**  |Planned |**Geometric Complexity**. Addition of advanced functionalities to handle ground slope and the evaluation of foundations subjected to eccentricities and moments. |
|**v4.0**   |Planned |**Probabilistic Analysis**. Probabilistic Analysis. Implementation of an Analysis of the probability of foundation failure using the Monte Carlo method. |


---
### 📚 Technical and Bibliographical References
---

This project is based on the following sources to ensure engineering validity:

1. Meyerhof, G.G. (1963). "Shallow Foundations." Journal of the Soil Mechanics and Foundations Division, ASCE.
2. Bowles, J. E., & Guo, Y. (1996). Foundation analysis and design (Vol. 5, p. 127). New York: McGraw-hill.
3. AASHTO (2020). LRFD Bridge Design Specifications. (Framework for Load and Resistance Factor Design (LRFD)).  

---
### 🤝 Contribution
---

This project's **core geotechnical logic, architectural design, and calculation methodology** are based entirely on specialized geotechnical knowledge and extensive project experience.  


The Python code implementation was accelerated with the support of Generative AI, serving as a co-programmer in the following tasks:  
* Function and Module Generation: Creating the initial structure of functions and classes.  
* Boilerplate Code: Writing repetitive and auxiliary code.  
* Debugging and Optimization: Assisting in the identification of errors and the improvement of code efficiency. 


We encourage you to audit the code, modify the implementation, and propose improvements.


