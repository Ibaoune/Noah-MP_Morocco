# Author: M. El Aabaribaoune (@um6p)

import re

def fix_mptable(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    if len(content) == 0:
        print("File is empty!")
        return
        
    print(f"Original size: {len(content)}")

    # Rename &noahmp_ to &noah_mp_
    content = content.replace('&noahmp_', '&noah_mp_')

    # Remove unrecognized keys that cause Fortran namelist to fail
    unrecognized = [
        r'^\s*ISICE\s*=.*?\n',
        r'^\s*ISCROP\s*=.*?\n',
        r'^\s*NATURAL\s*=.*?\n',
        r'^\s*LOW_DENSITY_RESIDENTIAL\s*=.*?\n',
        r'^\s*HIGH_DENSITY_RESIDENTIAL\s*=.*?\n',
        r'^\s*HIGH_INTENSITY_INDUSTRIAL\s*=.*?\n',
        r'^\s*MFSNO\s*=.*?\n',
        r'^\s*NROOT\s*=.*?\n',
        r'^\s*RGL\s*=.*?\n',
        r'^\s*RS\s*=.*?\n',
        r'^\s*HS\s*=.*?\n',
        r'^\s*TOPT\s*=.*?\n',
        r'^\s*RSMAX\s*=.*?\n'
    ]
    for pattern in unrecognized:
        content = re.sub(pattern, '', content, flags=re.MULTILINE)

    content = re.sub(r'RHOL_VIS\s*=', 'RHOL=', content)
    content = re.sub(r'RHOL_NIR\s*=.*?\n', '', content)

    content = re.sub(r'RHOS_VIS\s*=', 'RHOS=', content)
    content = re.sub(r'RHOS_NIR\s*=.*?\n', '', content)

    content = re.sub(r'TAUL_VIS\s*=', 'TAUL=', content)
    content = re.sub(r'TAUL_NIR\s*=.*?\n', '', content)

    content = re.sub(r'TAUS_VIS\s*=', 'TAUS=', content)
    content = re.sub(r'TAUS_NIR\s*=.*?\n', '', content)

    # Same for SAI_JAN ... SAI_DEC -> SAIM
    content = re.sub(r'SAI_JAN\s*=', 'SAIM=', content)
    for m in ['FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']:
        content = re.sub(rf'SAI_{m}\s*=.*?\n', '', content)

    # Same for LAI
    content = re.sub(r'LAI_JAN\s*=', 'LAIM=', content)
    for m in ['FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']:
        content = re.sub(rf'LAI_{m}\s*=.*?\n', '', content)

    # EPS1 -> EPS
    content = re.sub(r'EPS1\s*=', 'EPS=', content)
    for i in range(2, 6):
        content = re.sub(rf'EPS{i}\s*=.*?\n', '', content)

    print(f"New size: {len(content)}")
    with open(filename, 'w') as f:
        f.write(content)
        print("Wrote file.")

fix_mptable('input/noah_2dparms/MPTABLE.TBL')
