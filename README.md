# Satellite-Informed Land Surface Modelling over Morocco (Noah-MP/LIS)

This project focuses on **Satellite-Informed Land Surface Modelling for Drought, Vegetation, and Water Availability Monitoring over the Allal El Fassi Basin** in Morocco using the NASA **Land Information System Framework (LISF)** (LIS/Noah-MP, LDT, and LVT).

## Author
* **M. El Aabaribaoune** ([@um6p](https://github.com/um6p))

## Project Structure
* `lisf/`: Contains the Land Information System Framework (LISF) source code and compiled executables.
* `COMPILATION_AND_STATUS_SUMMARY.txt`: A detailed summary of the compilation process, loaded modules, code bug patches, and the simulation configuration steps.
* `.gitignore`: Configured to exclude heavy binaries, compilation artifacts, and log files.

## Component Executables
After successful compilation, the following binaries are ready for use:
1. **LDT (Land Data Toolkit)**: `/lisf/ldt/LDT`
2. **LIS (Land Information System)**: `/lisf/lis/LIS`
3. **LVT (Land Verification Toolkit)**: `/lisf/lvt/LVT`

## Environment & Build Setup
The build environment is set up on the cluster using the following modules:
```bash
module purge
module load foss/2024a netCDF-Fortran/4.6.1-gompi-2024a netCDF/4.9.2-gompi-2024a ESMF/8.7.0-foss-2024a JasPer/4.2.4-GCCcore-13.3.0 ecCodes/2.38.3-gompi-2024a HDF5/1.14.5-gompi-2024a CMake/3.29.3-GCCcore-13.3.0
```

## Simulation Configuration Steps
Please refer to `COMPILATION_AND_STATUS_SUMMARY.txt` for detailed step-by-step instructions on:
1. Defining the 1 km spatial domain bounds for the Allal El Fassi Basin.
2. Generating static parameters using LDT.
3. Setting up Open-Loop (OPL) and Data Assimilation (DA) retrospective simulations over a 3-month period.
4. Performing validation against satellite observations (soil moisture, LAI, ET) using LVT.
