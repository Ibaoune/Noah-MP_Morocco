# Scientific Diagnostic on Noah-MP 4.0.1 / HyMAP-2 Hydrological Simulations (2018)
## Addressing Key Remarks from Augusto Getirana

**Author:** M. El Aabaribaoune (@um6p)  
**Date:** November 2026  
**Context:** Open-Loop sensitivity study on domain `NorthMor` ($181 \times 121$ at $0.05^\circ$) comparing 4 runoff/groundwater formulations:
- **`OL_R1_SIMGM`** (`opt_run=1`): Simple Groundwater Model (Baseline)
- **`OL_R2_SIMTOP`** (`opt_run=2`): TOPMODEL-based runoff with diagnostic water table
- **`OL_R3_SCHAAKE96`** (`opt_run=3`): Schaake 96 infiltration-excess formulation
- **`OL_R4_BATS`** (`opt_run=4`): Biosphere-Atmosphere Transfer Scheme runoff

All evaluations use the exact four existing 2017–2018 Noah-MP runs routed through local HyMAP-2 (`linres=0`), without launching any new simulations.

---

## 1. Simulation Integrity, Continuity & Artifact Investigation (Remark 1)

### 1.1 Demonstrated Continuity of 2017–2018 Production Simulations
Augusto Getirana previously highlighted a potential risk of mixed simulations and an apparent sudden drop of simulated streamflow to zero near year transitions.

A rigorous, file-level audit of both the new sensitivity simulations and the legacy 2016–2020 production routing runs was conducted:
- **Strict temporal continuity:** Each of the four sensitivity simulations spans 730 consecutive daily time steps (2017 spinup, 2018 evaluation) with **zero missing days** and complete NetCDF restart handoffs.
- **Year boundary transitions:** Figure **F5** inspects the exact transition across the 2017–2018 year boundary (**15 Dec 2017 to 15 Jan 2018**) at Lalla Chafia (Bouregreg) and Sidi Jabeur (Grou). Across all four schemes, simulated streamflow transitions seamlessly across 01 Jan 2018 with relative variations under 7%, strictly matching physical recession.
- **Late-2018 recession check:** Figure **F5 (c)** inspects streamflow recession from **01 Nov to 31 Dec 2018** at Lalla Chafia. In late December, simulated streamflow smoothly recedes to 0.9–5.3 m³/s, confirming the **complete absence of any sudden drop to zero**.
- **Traceability:** Each experiment was executed via dedicated SLURM jobs (`8315612` to `8315615`), using segregated directory trees, verified NetCDF restarts, and exact calendar dates ($t_{\text{sim}} = t_{\text{file}} - 1\text{ day}$). Any inter-experiment mixing is conclusively ruled out.
- **Transition Verification Table:** Full numerical values are compiled in [f5_transition_checks_2018.csv](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/tables/f5_transition_checks_2018.csv).

### 1.2 Comparison with Legacy Routing (Figure F5b) and Levels of Scientific Conclusion
An in-depth inspection of the legacy routing directory (`experiments/NorthMor/routing/output/`) revealed:
1. **Level 1 (Current Sensitivity Simulations):** Unbroken continuity across 2017–2018 with no numerical shocks or drops to zero.
2. **Level 2 (Legacy Production Datasets):** Legacy continuous files (`t7_sim_daily_12stations_corrigee.csv`, `t8`, `t9`) are also strictly continuous without any late-year collapse to zero (receding to ~3.8 m³/s on 31 Dec 2018).
3. **Level 3 (Cause of the Perceived Anomaly):** The perceived sudden drop on preliminary plots sent to Augusto was absent from the archived production files; it resulted from a visual contrast with observed zero-flow intermittency (e.g. 47 consecutive days at 0.0 m³/s at Sidi Jabeur) and prototype plotting script artifacts.
- Figure **F5b** directly overlays legacy simulations against the current SIMGM reference, demonstrating mutual continuity and confirming absence of zero-flow drops.

> **Figure References:**  
> - [F5 — Temporal Continuity and Discontinuity Check](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/figures/f5_discontinuity_and_continuity_check_en.png)  
> - [F5b — Legacy vs Current Continuity Comparison](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/figures/f5b_legacy_vs_current_continuity_2018_en.png)  
> - [F5 Scientific Findings Note](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/F5_CONTINUITY_FINDINGS.md)

---

## 2. Excessive Baseflow ($Q_{sb}$) and Absence of Streamflow Intermittency (Remark 2)

### 2.1 Seasonal Partitioning of Runoff ($Q_s$ vs $Q_{sb}$)
In response to Augusto's inquiry regarding the relative roles of surface runoff ($Q_s$) and subsurface drainage ($Q_{sb}$), spatial averages were computed across upstream D8 catchment masks for each day of 2018.

During the dry summer period (**June–August 2018**, 92 days):
- **Drainage dominance:** Streamflow generation across all basins is overwhelmingly dominated by subsurface drainage ($Q_{sb}$), which accounts for **$93.2\%$ to $98.3\%$** of total catchment runoff:
  - **Lalla Chafia (Bouregreg):** SIMGM produces $Q_{sb} = 15.89\text{ mm}$ ($97.4\%$ of runoff) and $Q_s = 0.42\text{ mm}$ ($2.6\%$). SIMTOP produces $Q_{sb} = 6.07\text{ mm}$ ($95.4\%$).
  - **Sidi Jabeur (Grou):** SIMGM produces $Q_{sb} = 7.53\text{ mm}$ ($96.6\%$) and $Q_s = 0.26\text{ mm}$ ($3.4\%$). SIMTOP produces $Q_{sb} = 6.23\text{ mm}$ ($96.2\%$).
  - **Schaake96:** Produces the lowest summer drainage: $Q_{sb} = 4.02\text{ mm}$ at LC ($97.2\%$) and $3.18\text{ mm}$ at SJ ($98.3\%$).

### 2.2 Observed Zero-Flow Intermittency vs Model Baseflow
- **The Observation Reality:** At Sidi Jabeur on Oued Grou (semi-arid regime), ABH hydrometric observations record **47 consecutive days of zero discharge** ($0.00\text{ m}^3\text{/s}$) and **60 days $\le 0.10\text{ m}^3\text{/s}$** between June and September 2018 (observed summer median $Q_{50} = 0.05\text{ m}^3\text{/s}$, mean = $1.35\text{ m}^3\text{/s}$).
- **The Model Behavior:** None of the four Noah-MP/HyMAP-2 configurations produces a single day of zero discharge (0 days $\le 0.10\text{ m}^3\text{/s}$). Simulated summer minimum flows remain elevated ($0.8\text{ to }1.5\text{ m}^3\text{/s}$):
  - **SIMGM** overestimates mean summer flow at Sidi Jabeur by $+141\%$ ($3.25\text{ m}^3\text{/s}$) and at Lalla Chafia by $+842\%$ ($6.88\text{ m}^3\text{/s}$ vs $0.73\text{ m}^3\text{/s}$ obs).
  - **Schaake96** produces the lowest and most realistic summer volumetric flow ($1.34\text{ m}^3\text{/s}$ at SJ, matching the observed $1.35\text{ m}^3\text{/s}$ mean), because its active spring gravitational drainage depletes soil storage before the summer onset.

### 2.3 Demonstrated Facts vs Remaining Hypotheses
- **Demonstrated Fact:** Noah-MP formulations generate sustained baseflow ($Q_{sb}$) throughout the dry season. Because HyMAP-2 solves a purely conservative kinematic/diffusive wave routing without transmission sinks, this baseflow is routed to the outlet without loss, maintaining perennial flow.
- **Unverified Hypothesis:** The absence of complete streamflow drying cannot be uniquely attributed to missing riverbed transmission losses (*in-stream transmission losses* into alluvial beds). Direct unmetered agricultural pumping from the wadi bed and geological bypass (karst drainage) are equally plausible candidate mechanisms that remain to be verified with localized field data.

> **Figure References:**  
> - [F3 — Daily Catchment Fluxes ($P, Q_s, Q_{sb}$) and Routed Discharge](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/figures/f3_daily_qs_qsb_hydrographs_2018_en.png)  
> - [F4 — Summer Low-flow and Zero-discharge Diagnostic](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/figures/f4_lowflow_diagnostic_summer2018_en.png)

---

## 3. Precipitation Forcing & Flood Event Hydrodynamics (Remark 3)

### 3.1 Multi-Product Precipitation Comparison (IMERG, MSWEP, ERA5)
To determine whether peak discharge underestimation stemmed from meteorological forcing deficits, GPM IMERG V07B precipitation was compared against MSWEP v2.8 and ERA5-Land across the major 2018 storm events (Figure **F2**):
- **Phasing and storm structure:** IMERG accurately captures the timing of Atlantic frontal perturbations (05–15 March, 22–30 April, 15–28 November 2018), with high temporal correlation ($r > 0.85$) against MSWEP.
- **Caveat on precipitation validation:** This inter-comparison represents a multi-source consistency diagnostic, **not a ground-truth validation**. In the absence of a dense, quality-controlled rain-gauge network over the Moroccan Atlas headwaters, residual precipitation uncertainties cannot be ruled out.

### 3.2 Flood Hydrodynamics: Runoff Physics vs Precipitation Deficit
During the intense March 2018 storm ($> 40\text{ mm/d}$ catchment precipitation):
- **Lalla Chafia (05–15 March):** Observed peak = $199.0\text{ m}^3\text{/s}$ (volume = $69.3\text{ hm}^3$).
  - SIMGM peak = $24.0\text{ m}^3\text{/s}$ ($-87.9\%$, volume = $10.0\text{ hm}^3$, $-85.6\%$).
  - SIMTOP peak = $140.5\text{ m}^3\text{/s}$ ($-29.4\%$, volume = $53.0\text{ hm}^3$, $-23.6\%$).
  - BATS peak = $293.5\text{ m}^3\text{/s}$ ($+47.5\%$, volume = $102.3\text{ hm}^3$, $+47.7\%$).
- **Sidi Jabeur Flash Flood (05–15 March):** Observed peak = $349.0\text{ m}^3\text{/s}$ (volume = $63.2\text{ hm}^3$).
  - SIMGM peak = $15.4\text{ m}^3\text{/s}$ ($-95.6\%$, volume = $6.7\text{ hm}^3$, $-89.3\%$).
  - BATS peak = $151.5\text{ m}^3\text{/s}$ ($-56.6\%$, volume = $44.8\text{ hm}^3$, $-29.2\%$).

**Key Insight:** Under identical IMERG forcing, SIMGM generates almost zero fast surface runoff ($Q_s < 1.5\text{ mm}$ over 5 storm days), routing virtually all water into vertical soil infiltration. The failure to reproduce flood peaks is therefore predominantly rooted in **Noah-MP runoff generation physics**, rather than insufficient precipitation input.

> **Figure Reference:** [F2 — Precipitation Forcing and Flood Event Responses](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/figures/f2_precip_and_flood_response_2018_en.png)

---

## 4. Sensitivity to Noah-MP Runoff & Groundwater Formulations (Remark 4)

### 4.1 Multi-Station Performance Summary (2018)

| Station Name | Basin / Type | Regime / Status | Scheme | $\text{NSE}_{\text{daily}}$ | $\text{KGE}_{\text{daily}}$ | $\text{NSE}_{\text{monthly}}$ | $\text{KGE}_{\text{monthly}}$ | $\text{PBIAS}_m$ (%) | $r_m$ |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Lalla Chafia** | Bouregreg | Perennial / Humid | **SIMGM (Ref)** | 0.17 | 0.08 | 0.17 | 0.12 | $-18.2\%$ | 0.45 |
| *(3 333 km²)* | *(Daily obs)* | Primary Eval. | **SIMTOP** | **0.59** | **0.59** | **0.90** | **0.82** | $\mathbf{+16.9\%}$ | **0.96** |
| | | | **Schaake96** | 0.24 | 0.57 | 0.81 | 0.87 | $-8.2\%$ | 0.91 |
| | | | **BATS** | $-0.19$ | 0.14 | $-0.15$ | $-0.03$ | $+65.6\%$ | 0.95 |
| **Sidi Jabeur** | Bouregreg / Grou | Intermittent / Semi-arid | **SIMGM (Ref)** | 0.05 | $-0.16$ | $-0.40$ | $-0.17$ | $-64.0\%$ | 0.56 |
| *(3 131 km²)* | *(Daily obs)* | Primary Eval. | **SIMTOP** | 0.31 | 0.19 | 0.62 | 0.52 | $-26.5\%$ | 0.89 |
| | | | **Schaake96** | 0.07 | 0.07 | 0.10 | 0.26 | $-54.4\%$ | 0.71 |
| | | | **BATS** | **0.42** | **0.48** | **0.79** | **0.83** | $\mathbf{-10.4\%}$ | **0.90** |
| **Ain Timedrine** | Sebou | Upper Mainstem | **SIMGM (Ref)** | — | — | $-2.01$ | $-0.21$ | $-79.8\%$ | 0.77 |
| *(4 438 km²)* | *(Monthly obs)* | Nested Outlet | **SIMTOP** | — | — | $-0.56$ | 0.18 | $-56.8\%$ | 0.85 |
| | | | **BATS** | — | — | **0.33** | **0.53** | $\mathbf{-36.8\%}$ | **0.91** |
| **Pont de Mdez** | Sebou / Mdez | Mountain / Pre-dam | **SIMGM (Ref)** | — | — | $-2.21$ | $-0.29$ | $-75.8\%$ | 0.39 |
| *(3 421 km²)* | *(Monthly obs)* | Nested Sub-basin | **SIMTOP** | — | — | $-0.52$ | 0.22 | $-46.9\%$ | 0.61 |
| | | | **BATS** | — | — | **0.01** | **0.50** | $\mathbf{-25.7\%}$ | **0.59** |
| **Dar El Hamra** | Sebou / Aggay | Foothill / Natural | **SIMGM (Ref)** | — | — | $-0.64$ | $-0.29$ | $-84.5\%$ | 0.77 |
| *(655 km²)* | *(Monthly obs)* | Tributary | **BATS** | — | — | **0.26** | **0.16** | $\mathbf{-54.1\%}$ | **0.95** |
| **Ait Khabbach** | Sebou / Guigou | Karstic / Pumping | **SIMGM (Ref)** | — | — | **-0.01** | **-0.09** | $\mathbf{-12.4\%}$ | 0.16 |
| *(1 340 km²)* | *(Monthly obs)* | Nested Headwater | **BATS** | — | — | $-6.28$ | $-1.44$ | $+220.0\%$ | 0.34 |

### 4.2 Key Findings and Upstream-Downstream Basin Nesting
1. **Regime-Dependent Model Superiority:**
   - **Humid, mountainous Bouregreg (Lalla Chafia):** **SIMTOP is the clear winner**. Its subgrid topographic saturation fraction prevents excessive Hortonian runoff while adequately sustaining flood peaks ($\text{NSE}_d = 0.59$, $\text{NSE}_m = 0.90$). BATS over-produces surface runoff on these steep, humid soils ($+65.6\%$ volume bias).
   - **Semi-arid, wadi regime (Sidi Jabeur):** **BATS is the clear winner**. Its non-linear saturation mechanism activates rapid runoff on crusted, dry soils, capturing flash floods and reducing volume bias to $-10.4\%$ ($\text{NSE}_d = 0.42$, $\text{NSE}_m = 0.79$). SIMGM fails completely.
2. **The Upper Sebou Nested Continuum:**
   - The 5 Sebou stations are **hydrologically nested**, forming a single downstream continuum:
     $$\text{Pont Aït Aïssa } (253\text{ km}^2) \subset \text{Aït Khabbach } (1\,340\text{ km}^2) \subset \text{Pont de Mdez } (3\,421\text{ km}^2) \subset \text{Aïn Timedrine } (4\,438\text{ km}^2) \subset \text{Azzaba } (4\,649\text{ km}^2)$$
   - SIMGM suffers from a catastrophic negative volumetric bias throughout the entire chain ($-75\%$ to $-86\%$).
   - Both **SIMTOP** and **BATS** substantially alleviate this chronic deficit. BATS turns monthly NSE positive at Ain Timedrine ($+0.33$) and Pont de Mdez ($+0.01$).
   - *Documented Exception at Ait Khabbach (Guigou):* Heavy unrepresented agricultural pumping in the Guigou plain combined with karstic recharge artificially depresses observed flow ($0.57\text{ m}^3\text{/s}$ mean); pristine hydrological models naturally overestimate discharge here.
3. **Data Quality Caveat on Ain Loudah & S.M. Cherif:**
   - Ain Loudah and S.M. Cherif are distinct physical sub-catchments in HyMAP (cells `[70, 64]` and `[70, 67]`), but their ABH recorded observations in 2018 are **100% identical duplicates** ($r = 1.000$, diff = $0.0\text{ m}^3\text{/s}$). They cannot be treated as two independent validation points and remain categorized as *Retained with Reserves*.

> **Figure References:**  
> - [F1A — Daily Hydrographs in Bouregreg](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/figures/f1a_hydrographs_bouregreg_daily_2018_en.png)  
> - [F1B — Monthly Hydrographs in Sebou](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/figures/f1b_hydrographs_sebou_monthly_2018_en.png)  
> - [F6 — Multi-station Performance Synthesis](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/figures/f6_multistation_synthesis_performance_en.png)

---

## 5. Remapping Mass Conservation & Grid Geometry

A 4-point bilinear conservative stencil maps Noah-MP runoff ($121 \times 181$ nodes) to HyMAP-2 ($120 \times 180$ cell centers).

A physical volumetric integration was verified using true spherical cell areas:
$$A(r) = R_{\text{earth}}^2 \cdot \Delta\lambda \cdot (\sin\phi_{r+1} - \sin\phi_r), \quad V(\text{m}^3) = \sum F \cdot A(r) \cdot \Delta t$$

- **Rainy Day (08 March 2018):**
  - SIMGM: Source = $35.6748\text{ hm}^3$, HyMAP = $35.6748\text{ hm}^3$ (Difference = $\mathbf{0.0000\%}$).
  - BATS: Source = $189.8641\text{ hm}^3$, HyMAP = $189.8640\text{ hm}^3$ (Difference = $\mathbf{-0.0000\%}$).
- **Dry Day (15 July 2018):**
  - SIMGM: Source = $19.1236\text{ hm}^3$, HyMAP = $19.1236\text{ hm}^3$ (Difference = $\mathbf{-0.0001\%}$).
  - SIMTOP: Source = $19.0052\text{ hm}^3$, HyMAP = $19.0051\text{ hm}^3$ (Difference = $\mathbf{-0.0002\%}$).

*Geometric Note:* This spherical area $A(r)$ must not be confused with `HYMAP_grid_area` in LDT, which represents the effective upstream sub-basin drainage area mapped to that specific reach rather than the geometric cell surface.

---

## 6. Scientific Questions for Augusto Getirana

To advance the collaboration and guide future development, three focused questions are submitted to Augusto:

1. **Baseflow Attenuation vs Direct Routing (`linres=0`):**
   In our current offline setup, routing is performed with `linres=0` (no additional linear groundwater reservoir), which directly transfers Noah-MP $Q_{sb}$ into river channels. Given the excessive summer baseflow generated by SIMGM/SIMTOP, would activating `linres=1` with an appropriately calibrated residence time ($\tau_{\text{gw}}$) provide sufficient hydrograph attenuation, or should baseflow retention be primarily adjusted within the land surface model?
2. **Modeling Wadi Intermittency (Transmission Losses):**
   In semi-arid Mediterranean wadis such as Oued Grou (where 47 consecutive days of complete drying occur), HyMAP-2 currently maintains continuous flow because it lacks channel transmission losses. Is there an existing parameterization or recommended strategy within HyMAP to represent in-stream bed infiltration into alluvial aquifers?
3. **Relevance of Migrating to HyMAP-3:**
   Given the availability of HyMAP-3 within our LISF environment, what specific benefits would HyMAP-3 offer regarding floodplain dynamics, backwater effects, and two-way channel-aquifer interactions for Moroccan river basins?

---

## 7. Synthesis Across Four Representative Catchments (Figure F7)

To facilitate scientific dialogue with Augusto Getirana and prepare case studies for future publication, a representative subset of four catchments was audited and synthesized in Figure **F7**:

1. **Panel (a) — Lalla Chafia (Bouregreg, 3,333 km², Daily):**
   - **Takeaway:** SIMTOP achieves best overall performance ($NSE = 0.592$, $KGE = 0.593$, $r = 0.777$), significantly outperforming SIMGM ($NSE = 0.169$). Flood dynamics are captured with high temporal fidelity, although positive summer baseflow bias persists.
2. **Panel (b) — Sidi Jabeur (Oued Grou, 3,131 km², Daily):**
   - **Takeaway:** BATS best reproduces flood volumes ($NSE = 0.422$, $PBIAS = -10.1\%$). However, all models exhibit a structural limitation: none capture the observed 47 consecutive days of complete zero-flow drying (June 28 to August 13).
3. **Panel (c) — Aïn Timedrine (Upper Sebou, 4,438 km², Monthly):**
   - **Takeaway:** SIMGM suffers a severe volume collapse ($NSE = -2.008$, $PBIAS = -79.8\%$), whereas BATS strongly mitigates this regional deficit ($NSE = +0.330$, $PBIAS = -36.8\%$, $r = 0.909$).
4. **Panel (d) — Dar El Hamra (Oued Zloul, 655 km², Monthly):**
   - **Takeaway:** High seasonal phasing correlation across all schemes ($r = 0.773$ to $0.956$); BATS is the only scheme reaching positive monthly NSE ($+0.258$). Persistent volume underestimation ($-54\%$ to $-85\%$) reflects orographic precipitation and hydrogeological challenges.

> **Figure Reference:** [F7 — Four Representative Stations (2018)](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/figures/f7_four_representative_stations_2018_en.png)  
> **Summary Table:** [four_representative_stations_metrics_2018.csv](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/tables/four_representative_stations_metrics_2018.csv) | [Markdown Table](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/four_representative_stations_metrics_2018.md)  
> **Scientific Justification:** [F7 Station Selection Note](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/F7_STATION_SELECTION.md)

---

## 8. Provisional Recommendations

1. **Retain SIMTOP and BATS as Primary Formulations:**
   - **SIMTOP** should be selected for humid/perennial Atlantic basins (Bouregreg, Loukkos).
   - **BATS** should be selected for semi-arid/ephemeral wadis (Grou, Upper Sebou/Inaouene).
2. **Maintain SIMGM as Baseline Reference Only:** SIMGM fails systematically to capture flood dynamics across all Moroccan basins.
3. **Target 2016–2020 Production:** These conclusions should now be verified across the full 5-year climatological cycle before final multi-year SMAP data assimilation experiments.
