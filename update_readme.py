import re

with open('scripts/download/validation/README_validation.md', 'r') as f:
    content = f.read()

# Update statuses in the table
content = content.replace('|  **MISSING** — needs download | `download_gldas.py` (new) |', '|  Available | `download_gldas.py` |')
content = content.replace('|  **MISSING** — needs download | `download_fluxsat_gpp.py` (new) |', '|  Available | `download_fluxsat_gpp.py` |')
content = content.replace('|  Dummy files — needs real download | `download_wapor.py` (moved + rewritten) |', '|  **Pending** — requires Google Earth Engine `set_project` | `download_wapor.py` |')

# Add missing datasets to the table
table_end_idx = content.find('> **Excluded**')
table_part = content[:table_end_idx]
rest_part = content[table_end_idx:]

new_rows = """| 7 | ESA CCI Soil Moisture (COMBINED v8.1) | pp01, pp02 | Available | `download_esa_cci_sm.py` |
| 8 | Copernicus ASCAT SWI | pp01, pp02 | Available | `download_ascat.py` |
| 9 | Copernicus LAI 300m | pp02 | **Running** | `download_copernicus_lai.py` |
| 10 | GLEAM v3.8a ET | pp01, pp02 | **Running** | `download_gleam.py` |
| 11 | GRACE / GRACE-FO | pp01 | Available | `download_grace.py` |
"""

new_content = table_part + new_rows + "\n" + rest_part

# Fix quick start section to mention the new scripts
qs_target = "# Check downloaded inventories"
qs_new = """# Check downloaded inventories
ls ../../data/reports/inventory_*.csv

# Other submission scripts available:
# sbatch submit_ascat.sh
# sbatch submit_cop_lai.sh
# sbatch submit_esacci.sh
# sbatch submit_gleam.sh
"""
new_content = new_content.replace(qs_target + "\nls ../../data/reports/inventory_*.csv", qs_new)

with open('scripts/download/validation/README_validation.md', 'w') as f:
    f.write(new_content)

