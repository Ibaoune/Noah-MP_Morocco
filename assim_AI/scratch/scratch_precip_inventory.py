# Author: M. EL Aabaribaoune (@um6p)
import os
import pandas as pd
import glob
from io import StringIO

data_dir = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/IA_SM_assim/data/insitu_data"
files = glob.glob(os.path.join(data_dir, "*.txt"))

results = []
for f in files:
    filename = os.path.basename(f)
    try:
        df = pd.read_csv(f, sep=r'\s+', comment='#', header=0, encoding='utf-8')
        if len(df.columns) == 1:
            df = pd.read_csv(f, sep=',', comment='#', header=0, encoding='utf-8')
        if len(df.columns) == 1:
            df = pd.read_csv(f, sep=';', comment='#', header=0, encoding='utf-8')
            
        columns = list(df.columns)
        
        # Try to find date col
        date_cols = [c for c in columns if 'date' in c.lower() or 'time' in c.lower() or 'year' in c.lower()]
        
        period_min, period_max = "unknown", "unknown"
        if len(df) > 0:
            if date_cols:
                period_min = str(df[date_cols[0]].iloc[0])
                period_max = str(df[date_cols[0]].iloc[-1])
        
        # We need to detect 2016-2020 coverage
        has_2016_2020 = False
        if len(df) > 0 and date_cols:
            dates = df[date_cols[0]].astype(str)
            has_2016_2020 = any(dates.str.contains('2016') | dates.str.contains('2017') | dates.str.contains('2018') | dates.str.contains('2019') | dates.str.contains('2020'))
            
        results.append({
            'filename': filename,
            'format': 'txt',
            'columns': ",".join(columns),
            'date_col': date_cols[0] if date_cols else "None",
            'station_col': next((c for c in columns if 'station' in c.lower() or 'id' in c.lower()), "None"),
            'lat_lon_col': next((c for c in columns if 'lat' in c.lower() or 'lon' in c.lower()), "None"),
            'precip_col': next((c for c in columns if 'precip' in c.lower() or 'rr' in c.lower().split('_') or 'p' == c.lower()), "None"),
            'frequency': 'daily/monthly (unknown)',
            'period_min': period_min,
            'period_max': period_max,
            'obs_count': len(df),
            'missing_rate': round(df.isnull().sum().sum() / max(1, (len(df) * len(columns))), 2),
            'has_2016_2020': has_2016_2020
        })
    except Exception as e:
        results.append({
            'filename': filename,
            'format': 'txt',
            'columns': f"Error: {e}",
            'date_col': '', 'station_col': '', 'lat_lon_col': '', 'precip_col': '',
            'frequency': '', 'period_min': '', 'period_max': '', 'obs_count': 0, 'missing_rate': 0, 'has_2016_2020': False
        })

inventory_df = pd.DataFrame(results)

out_dir = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/IA_SM_assim/outputs/tables"
os.makedirs(out_dir, exist_ok=True)
inventory_df.to_csv(os.path.join(out_dir, "precip_insitu_inventory.csv"), index=False)

with open("/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/IA_SM_assim/reports/precip_insitu_inventory.md", "w") as f:
    f.write("# In-Situ Precipitation Inventory\n\n")
    headers = list(inventory_df.columns)
    f.write("| " + " | ".join(headers) + " |\n")
    f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
    for _, row in inventory_df.iterrows():
        f.write("| " + " | ".join(str(x) for x in row.values) + " |\n")
    
    f.write("\n\n## Conclusion\n")
    if inventory_df['has_2016_2020'].any():
        f.write("- **usable_for_2016_2020**: partial\n")
    else:
        f.write("- **usable_for_2016_2020**: no\n")
    
    f.write(f"- **station_count**: {len(inventory_df)}\n")
    f.write("- **main_limitations**: Need to verify spatial coverage and confirm continuous temporal records for 2016-2020. Coordinates seem absent in raw text formats (to be verified).\n")
    
print(inventory_df[['filename', 'period_min', 'period_max', 'has_2016_2020']])
