# Architecture & Environment — Toubkal HPC (UM6P)

This directory contains environment configuration files for building and
running LISF (LIS/LDT/LVT) on different HPC systems.

## Files

| File | Description |
|------|-------------|
| `arch_toubkal.env` | Module loads for Toubkal (foss/2024a toolchain) |

## Usage

Source the environment file from any job script:

```bash
source arch/arch_toubkal.env
```

This replaces the need to duplicate `module load` commands in every script.

## Compilation Notes

LISF was compiled on Toubkal with the **foss/2024a** toolchain:
- **Compiler**: GCC 13.3.0
- **MPI**: OpenMPI 5.0.3
- **NetCDF**: 4.9.2 + Fortran 4.6.1
- **ESMF**: 8.7.0
- **HDF5**: 1.14.5

Binaries location after migration:
- LIS: `src/lisf/lis/LIS`
- LDT: `src/lisf/ldt/make/LDT`
