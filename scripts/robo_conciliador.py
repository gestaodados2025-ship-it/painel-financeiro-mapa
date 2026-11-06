import pandas as pd
import requests
import json
import re
from datetime import datetime
from pathlib import Path

UGS_PRINCIPAIS = ["130010", "130141", "130255", "135098", "420013"]

URLS_EXE_2026 = {
    "EXE_PADRAO": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRFcFQpuXUjut17Ftj89ugQvu-eK-ZPI7a90FoPOnhcvXFSL2ymU-WOPiYwBT8qa8tzCeyo05q_YanW/pub?gid=1204904051&single=true&output=csv",
    "EXE_MDIR": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRFcFQpuXUjut17Ftj89ugQvu-eK-ZPI7a90FoPOnhcvXFSL2ymU-WOPiYwBT8qa8tzCeyo05q_YanW/pub?gid=32904262&single=true&output=csv"
}

URLS_RAP_2026 = {
    "20ZV": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=1255285299&single=true&output=csv",
    "20ZY": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=1626303078&single=true&output=csv",
    "2000": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=1251866406&single=true&output=csv",
    "215A": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=2071147261&single=true&output=csv",
    "2161": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=240279963&single=true&output=csv",
    "214Z": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=557514819&single=true&output=csv",
    "21B6": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=238112304&single=true&output=csv",
    "8593": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=296590604&single=true&output=csv",
    "8622": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=1039014086&single=true&output=csv",
    "00PN": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=1888642019&single=true&output=csv",
    "8606": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=1419215442&single=true&output=csv",
    "OUT
