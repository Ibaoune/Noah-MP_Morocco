# Assimilation diagnostics post-processing

This module generates diagnostic figures for the 2016 SMAP assimilation experiment.

## Scientific purpose

The diagnostics are used to verify:
- where SMAP observations were assimilated;
- the observation footprint;
- the sign and magnitude of innovations;
- the sign and magnitude of analysis increments;
- the consistency of diagnostic variables before interpretation.

## Important note on spread diagnostics

The variables forecast_sigma_01 and ensspread_Soil Moisture Layer 1_01 are not directly comparable.

forecast_sigma_01 is read from LIS innovation files. It represents a forecast variance or uncertainty diagnostic in observation space and is only available at assimilated SMAP observation locations.

ensspread_Soil Moisture Layer 1_01 is read from LIS spread files. It represents a model-state ensemble spread snapshot for Soil Moisture Layer 1, written on the LIS land mask at daily output times.

Because these diagnostics differ in:
- physical space: observation space versus model-state space;
- spatial support: assimilated observation footprint versus full LIS land mask;
- timing: assimilation times versus daily snapshots;
- diagnostic meaning: forecast variance/uncertainty versus model-state ensemble spread;

they must not be interpreted as a prior/posterior spread pair.

Therefore, the module does not compute or plot spread reduction from these two variables.

## Figure 08

Figure 08 is a consistency-check diagnostic showing that forecast_sigma_01 and ensspread_Soil Moisture Layer 1_01 differ in physical space, spatial support, and timing. It must not be interpreted as a prior/posterior spread-reduction diagnostic.

## Configuration

All plotting options are controlled by:
config_assimilation_diagnostics.yaml

The Python source code should not contain hard-coded figure titles, colorbar limits, colormaps, or output names.

## Output policy

Figures 06a, 06b, 07a, and 07b related to separated uncertainty/spread plots are disabled.
Only the consistency-check figure 08 is kept for this diagnostic family.
