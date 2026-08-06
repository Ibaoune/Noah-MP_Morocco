# Author: M. EL Aabaribaoune (@um6p)

import re

with open('/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/src/assimilation_diagnostics/plot_innovation.py', 'r') as f:
    code = f.read()

# 1. Add accumulators
acc_insert = """    incr_sum = np.zeros(grid_shape)
    counts_innov = np.zeros(grid_shape)
    counts_incr = np.zeros(grid_shape)
    
    incr_sum_djf = np.zeros(grid_shape)
    counts_incr_djf = np.zeros(grid_shape)
    incr_sum_jja = np.zeros(grid_shape)
    counts_incr_jja = np.zeros(grid_shape)
    
    spread_sum = np.zeros(grid_shape)
    counts_spread = np.zeros(grid_shape)
    all_spread_values = []"""
code = re.sub(r'    incr_sum = np\.zeros\(grid_shape\)\n    counts_innov = np\.zeros\(grid_shape\)\n    counts_incr = np\.zeros\(grid_shape\)', acc_insert, code)

# 2. Add is_djf, is_jja inside loop
loop_start = """    while curr_date <= end_date:
        yr = curr_date.strftime("%Y")
        mo = curr_date.strftime("%m")
        is_djf = curr_date.month in [12, 1, 2]
        is_jja = curr_date.month in [6, 7, 8]"""
code = re.sub(r'    while curr_date <= end_date:\n        yr = curr_date\.strftime\("%Y"\)\n        mo = curr_date\.strftime\("%m"\)', loop_start, code)

# 3. Add spread parsing in innov loop
innov_read = """                    innov_sum += valid_inv
                    counts_innov += mask_inv
                
                if 'forecast_sigma_01' in ds.variables:
                    sprd = ds.variables['forecast_sigma_01'][:]
                    if np.ma.is_masked(sprd):
                        sprd = sprd.filled(-9999)
                    mask_sprd = np.where((sprd > -100) & (sprd < 100), 1, 0)
                    valid_sprd = np.where(mask_sprd == 1, sprd, 0)
                    spread_sum += valid_sprd
                    counts_spread += mask_sprd
                    sprd_vals = sprd[mask_sprd == 1].flatten()
                    if len(sprd_vals) > 0:
                        all_spread_values.extend(sprd_vals)"""
code = re.sub(r'                    innov_sum \+= valid_inv\n                    counts_innov \+= mask_inv', innov_read, code)

# 4. Add seasonal parsing in incr loop
incr_read = """                    incr_sum += valid_inc
                    counts_incr += mask_inc
                    
                    if is_djf:
                        incr_sum_djf += valid_inc
                        counts_incr_djf += mask_inc
                    elif is_jja:
                        incr_sum_jja += valid_inc
                        counts_incr_jja += mask_inc"""
code = re.sub(r'                    incr_sum \+= valid_inc\n                    counts_incr \+= mask_inc', incr_read, code)

# 5. Add seasonal means and spread mean
means_calc = """    mean_innov = np.where(counts_innov > 0, innov_sum / counts_innov, np.nan)
    mean_incr = np.where(counts_incr > 0, incr_sum / counts_incr, np.nan)
    mean_incr_djf = np.where(counts_incr_djf > 0, incr_sum_djf / counts_incr_djf, np.nan)
    mean_incr_jja = np.where(counts_incr_jja > 0, incr_sum_jja / counts_incr_jja, np.nan)
    mean_spread = np.where(counts_spread > 0, spread_sum / counts_spread, np.nan)"""
code = re.sub(r'    mean_innov = np\.where\(counts_innov > 0, innov_sum / counts_innov, np\.nan\)\n    mean_incr = np\.where\(counts_incr > 0, incr_sum / counts_incr, np\.nan\)', means_calc, code)

# 6. Add the new figures at the very end
new_figures = """    # ==============================================================
    # Figure 4: Seasonal Increment (DJF and JJA)
    # ==============================================================
    fig4 = plt.figure(figsize=(14, 6), constrained_layout=True)
    
    # DJF
    ax4a = fig4.add_subplot(1, 2, 1, projection=ccrs.PlateCarree())
    add_map_features(ax4a)
    ax4a.set_title(f"Mean SMAP increment (DJF) – {exp_name}, {year_str}", fontsize=12, fontweight='bold', pad=15)
    
    vmax4 = np.nanpercentile(np.abs(mean_incr_djf), 98) if not np.all(np.isnan(mean_incr_djf)) else 0.05
    if np.isnan(vmax4) or vmax4 == 0: vmax4 = 0.05
    levels4 = np.linspace(-vmax4, vmax4, 11)
    norm4 = mcolors.BoundaryNorm(levels4, ncolors=cmap1.N, clip=True)
    
    pcm4a = ax4a.pcolormesh(lon, lat, mean_incr_djf, cmap=cmap1, norm=norm4, transform=ccrs.PlateCarree())
    
    # JJA
    ax4b = fig4.add_subplot(1, 2, 2, projection=ccrs.PlateCarree())
    add_map_features(ax4b)
    ax4b.set_title(f"Mean SMAP increment (JJA) – {exp_name}, {year_str}", fontsize=12, fontweight='bold', pad=15)
    
    pcm4b = ax4b.pcolormesh(lon, lat, mean_incr_jja, cmap=cmap1, norm=norm4, transform=ccrs.PlateCarree())
    
    cbar4 = fig4.colorbar(pcm4b, ax=[ax4a, ax4b], orientation='vertical', shrink=0.8, pad=0.02)
    cbar4.set_label('Increment', fontsize=12, fontweight='bold')
    cbar4.ax.tick_params(labelsize=10)
    
    f4a_png = os.path.join(out_dir, f"04a_smap_seasonal_increment_DJF_JJA_{exp_name}_{year_str}.png")
    fig4.savefig(f4a_png, dpi=300)
    plt.close(fig4)
    
    # ==============================================================
    # Figure 5: Prior Ensemble Spread Map
    # ==============================================================
    fig5 = plt.figure(figsize=(9, 7), constrained_layout=True)
    ax5 = plt.axes(projection=ccrs.PlateCarree())
    add_map_features(ax5)
    
    ax5.set_title(f"Time-averaged SMAP prior ensemble spread – {exp_name}, {period_str}", fontsize=13, fontweight='bold', pad=15)
    
    cmap5 = plt.get_cmap('YlOrRd').copy()
    cmap5.set_bad(color='#f0f0f0')
    
    vmax5 = np.nanpercentile(mean_spread, 98) if not np.all(np.isnan(mean_spread)) else 0.05
    if np.isnan(vmax5) or vmax5 == 0: vmax5 = 0.05
    levels5 = np.linspace(0, vmax5, 11)
    norm5 = mcolors.BoundaryNorm(levels5, ncolors=cmap5.N, clip=True)
    
    pcm5 = ax5.pcolormesh(lon, lat, mean_spread, cmap=cmap5, norm=norm5, transform=ccrs.PlateCarree())
    
    cbar5 = fig5.colorbar(pcm5, ax=ax5, orientation='vertical', shrink=0.8, pad=0.03)
    cbar5.set_label('Spread', fontsize=12, fontweight='bold')
    cbar5.ax.tick_params(labelsize=10)
    
    f4b_png = os.path.join(out_dir, f"04b_smap_prior_ensemble_spread_map_{exp_name}_{year_str}.png")
    fig5.savefig(f4b_png, dpi=300)
    plt.close(fig5)
    
    # ==============================================================
    # Figure 6: Prior Ensemble Spread Histogram
    # ==============================================================
    fig6, ax6 = plt.subplots(figsize=(8, 6), constrained_layout=True)
    if len(all_spread_values) > 0:
        ax6.hist(all_spread_values, bins=50, color='orange', edgecolor='black', alpha=0.7)
    
    ax6.set_title(f"Histogram of SMAP prior ensemble spread – {exp_name}, {year_str}", fontsize=13, fontweight='bold')
    ax6.set_xlabel("Ensemble Spread", fontsize=12)
    ax6.set_ylabel("Frequency", fontsize=12)
    ax6.grid(axis='y', linestyle='--', alpha=0.7)
    
    f4c_png = os.path.join(out_dir, f"04c_smap_prior_ensemble_spread_histogram_{exp_name}_{year_str}.png")
    fig6.savefig(f4c_png, dpi=300)
    plt.close(fig6)

    return [f1_png, f2_png, f3_png, f4a_png, f4b_png, f4c_png]"""
code = re.sub(r'    return \[f1_png, f2_png, f3_png\]', new_figures, code)

with open('/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/src/assimilation_diagnostics/plot_innovation.py', 'w') as f:
    f.write(code)

