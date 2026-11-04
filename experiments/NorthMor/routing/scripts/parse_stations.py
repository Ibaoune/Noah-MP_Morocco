
import numpy as np
np.float = float
np.int = int
import os, xlrd, openpyxl, datetime

base = "data/streamflow_data"

# Adamna
wb = openpyxl.load_workbook(f"{base}/adamna monthly.xlsx", data_only=True)
ws = wb["Sheet1"]
dates_ad, vals_ad = [], []
for r in range(2, ws.max_row+1):
    d = ws.cell(r, 1).value
    v = ws.cell(r, 2).value
    if d is not None:
        dates_ad.append(d)
        vals_ad.append(v)
val_ad_valid = [v for v in vals_ad if v is not None and str(v).strip() != "" and not np.isnan(float(v))]
n_exp_ad = (dates_ad[-1].year - dates_ad[0].year)*12 + (dates_ad[-1].month - dates_ad[0].month) + 1
pct_gap_ad = (n_exp_ad - len(val_ad_valid)) / n_exp_ad * 100.0

# Zelten
wb = openpyxl.load_workbook(f"{base}/Zelten.xlsx", data_only=True)
ws = wb["Sheet1"]
dates_ze, vals_ze = [], []
for r in range(2, ws.max_row+1):
    d = ws.cell(r, 1).value
    v = ws.cell(r, 2).value
    if d is not None:
        dates_ze.append(d)
        vals_ze.append(v)
val_ze_valid = [v for v in vals_ze if v is not None and str(v).strip() != "" and not np.isnan(float(v))]
n_exp_ze = (dates_ze[-1].year - dates_ze[0].year)*12 + (dates_ze[-1].month - dates_ze[0].month) + 1
pct_gap_ze = (n_exp_ze - len(val_ze_valid)) / n_exp_ze * 100.0

print(f"Adamna: {dates_ad[0].strftime('%Y-%m')} to {dates_ad[-1].strftime('%Y-%m')} | records={len(dates_ad)} | valid={len(val_ad_valid)} | expected={n_exp_ad} | gaps={pct_gap_ad:.2f}%")
print(f"Zelten: {dates_ze[0].strftime('%Y-%m')} to {dates_ze[-1].strftime('%Y-%m')} | records={len(dates_ze)} | valid={len(val_ze_valid)} | expected={n_exp_ze} | gaps={pct_gap_ze:.2f}%")

# XLS files
month_map = {
    "A09": 9, "B10": 10, "C11": 11, "D12": 12,
    "E01": 1, "F02": 2, "G03": 3, "H04": 4,
    "I05": 5, "J06": 6, "K07": 7, "L08": 8
}

xls_files = ["Igronzar.xls", "Qm_Ain_Aicha.xls", "Qm_Ain_Al_ouali.xls", "Qm_Ain_Timidrine.xls", "Qm_Allal_Tazi.xls", "Qm_Azib_Soltane.xls", "Qm_Azzaba.xls"]

for f in xls_files:
    wb = xlrd.open_workbook(f"{base}/{f}")
    sh_qm = wb.sheet_by_name("qm")
    name = sh_qm.cell_value(4, 2)
    ire = sh_qm.cell_value(3, 2)
    unit = sh_qm.cell_value(4, 8)
    
    sh_sdata = wb.sheet_by_name("sdata")
    records = []
    for r in range(1, sh_sdata.nrows):
        y = sh_sdata.cell_value(r, 1)
        m = sh_sdata.cell_value(r, 2)
        v = sh_sdata.cell_value(r, 3)
        mq = sh_sdata.cell_value(r, 4)
        if y != "" and m in month_map:
            yr = int(y)
            mo = month_map[m]
            records.append((yr, mo, v, mq))
            
    records.sort(key=lambda x: (x[0], x[1]))
    first_date = f"{records[0][0]}-{records[0][1]:02d}"
    last_date = f"{records[-1][0]}-{records[-1][1]:02d}"
    n_exp = (records[-1][0] - records[0][0])*12 + (records[-1][1] - records[0][1]) + 1
    
    valid_count = 0
    for yr, mo, v, mq in records:
        if v != "" and v is not None:
            try:
                fv = float(v)
                valid_count += 1
            except:
                pass
    pct_gap = (n_exp - valid_count) / n_exp * 100.0
    print(f"{name.strip()} ({ire}): {first_date} to {last_date} | records={len(records)} | valid={valid_count} | expected={n_exp} | gaps={pct_gap:.2f}%")
