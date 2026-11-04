
import numpy as np
np.float = float
np.int = int
import os, xlrd, openpyxl, datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

base = "data/streamflow_data"

month_map = {
    "A09": 9, "B10": 10, "C11": 11, "D12": 12,
    "E01": 1, "F02": 2, "G03": 3, "H04": 4,
    "I05": 5, "J06": 6, "K07": 7, "L08": 8
}

stations_data = {}

# 1. Adamna
wb = openpyxl.load_workbook(f"{base}/adamna monthly.xlsx", data_only=True)
ws = wb["Sheet1"]
d_ad = []
for r in range(2, ws.max_row+1):
    d = ws.cell(r, 1).value
    v = ws.cell(r, 2).value
    if d is not None and v is not None and str(v).strip() != "":
        try:
            fv = float(v)
            if isinstance(d, datetime.datetime):
                d_ad.append(datetime.date(d.year, d.month, 1))
            else:
                dt = datetime.datetime.strptime(str(d)[:10], "%Y-%m-%d")
                d_ad.append(datetime.date(dt.year, dt.month, 1))
        except:
            pass
stations_data["Adamna"] = ("non renseigne", sorted(set(d_ad)))

# 2. Zelten
wb = openpyxl.load_workbook(f"{base}/Zelten.xlsx", data_only=True)
ws = wb["Sheet1"]
d_ze = []
for r in range(2, ws.max_row+1):
    d = ws.cell(r, 1).value
    v = ws.cell(r, 2).value
    if d is not None and v is not None and str(v).strip() != "":
        try:
            fv = float(v)
            if isinstance(d, datetime.datetime):
                d_ze.append(datetime.date(d.year, d.month, 1))
            else:
                dt = datetime.datetime.strptime(str(d)[:10], "%Y-%m-%d")
                d_ze.append(datetime.date(dt.year, dt.month, 1))
        except:
            pass
stations_data["Zelten"] = ("non renseigne", sorted(set(d_ze)))

# 3. XLS stations
xls_list = [
    ("Igronzar.xls", "Igrounzar"),
    ("Qm_Ain_Aicha.xls", "Ain Aicha"),
    ("Qm_Ain_Al_ouali.xls", "Ain El Ouali"),
    ("Qm_Ain_Timidrine.xls", "Ain Timedrine"),
    ("Qm_Allal_Tazi.xls", "Allal Tazi"),
    ("Qm_Azib_Soltane.xls", "Azib Soltane"),
    ("Qm_Azzaba.xls", "Azzaba")
]

for fname, sname in xls_list:
    wb = xlrd.open_workbook(f"{base}/{fname}")
    sh_qm = wb.sheet_by_name("qm")
    ire = str(sh_qm.cell_value(3, 2)).strip()
    
    sh_sdata = wb.sheet_by_name("sdata")
    dates_s = []
    for r in range(1, sh_sdata.nrows):
        y = sh_sdata.cell_value(r, 1)
        m = sh_sdata.cell_value(r, 2)
        v = sh_sdata.cell_value(r, 3)
        if y != "" and m in month_map and v != "" and v is not None:
            try:
                fv = float(v)
                yr = int(y)
                mo = month_map[m]
                dates_s.append(datetime.date(yr, mo, 1))
            except:
                pass
    stations_data[sname] = (ire, sorted(set(dates_s)))

print("=== COUVERTURE DES 9 STATIONS ===")
target_start = datetime.date(2016, 1, 1)
target_end = datetime.date(2020, 12, 31)
total_target_months = 60

for sname, (ire, dlist) in stations_data.items():
    if not dlist:
        print(f"{sname:15s}: AUCUNE DONNEE")
        continue
    min_d = dlist[0]
    max_d = dlist[-1]
    
    # 2016-2020 count
    in_target = [d for d in dlist if target_start <= d <= target_end]
    pct_target = len(in_target) / total_target_months * 100.0
    print(f"{sname:15s} (IRE: {ire:8s}): {min_d} au {max_d} ({len(dlist):4d} mois valides) | 2016-2020: {len(in_target):2d}/60 mois ({pct_target:5.1f}%)")

# Plot diagram
fig, ax = plt.subplots(figsize=(12, 7), dpi=150)

# Shade target period
ax.axvspan(target_start, target_end, color="#ffdddd", alpha=0.7, label="Periode simulations LIS (2016-2020)")

y_labels = []
y_ticks = []

for idx, (sname, (ire, dlist)) in enumerate(stations_data.items()):
    y_pos = idx
    y_ticks.append(y_pos)
    y_labels.append(f"{sname} ({ire})")
    
    # plot each contiguous block or points
    if dlist:
        ax.plot(dlist, [y_pos]*len(dlist), "|", color="#1f77b4", markersize=14, markeredgewidth=2)
        # annotate coverage
        in_tgt = [d for d in dlist if target_start <= d <= target_end]
        pct = len(in_tgt) / 60.0 * 100.0
        ax.text(datetime.date(2021, 6, 1), y_pos, f"{len(in_tgt)}/60 mois ({pct:.0f}%)", 
                va="center", fontsize=9, color="#333333", fontweight="bold" if len(in_tgt)>0 else "normal")

ax.set_yticks(y_ticks)
ax.set_yticklabels(y_labels, fontsize=10)
ax.set_xlim(datetime.date(1930, 1, 1), datetime.date(2025, 1, 1))
ax.set_xlabel("Annee", fontsize=11, fontweight="bold")
ax.set_title("Couverture temporelle des 9 stations de debit (data/streamflow_data)", fontsize=13, fontweight="bold", pad=12)
ax.grid(True, axis="x", linestyle="--", alpha=0.5)
ax.legend(loc="upper left", frameon=True)

plt.tight_layout()
out_png = "experiments/NorthMor/routing/plots/streamflow_coverage_timeline.png"
plt.savefig(out_png)
plt.close()
print(f"Plot saved to: {out_png}")
