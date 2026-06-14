#!/usr/bin/env python3
# =============================================================================
# Author: M. El Aabaribaoune (@UM6P)
# Date:   2026-06-07
# =============================================================================
import urllib.request
import re

url = "https://www.fao.org/aquastat/en/geospatial-information/global-maps-irrigated-areas/latest-version"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        links = re.findall(r'href=[\'"]?([^\'" >]+)', html)
        for link in links:
            if 'gmia' in link.lower() or 'zip' in link.lower() or 'asc' in link.lower():
                print(link)
except Exception as e:
    print(e)
