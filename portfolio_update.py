import urllib.request
import json
from datetime import date, datetime
from collections import defaultdict

etfs = {
    'UST':  'UST.PA',
    'EUNL': 'EUNL.DE',
    'VWCE': 'VWCE.DE',
    'IS3R': 'IS3R.DE',
}

def fetch_price(symbol):
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        result = data['chart']['result'][0]
        price = result['meta']['regularMarketPrice']
        return round(price, 4)
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

print("Fetching current prices...")
prices = {}
for ticker, symbol in etfs.items():
    p = fetch_price(symbol)
    if p:
        prices[ticker] = p
        print(f"  {ticker}: {p}")

# Purchase history
purchases_personal = [
    ("2023-08-17","UST",7,54.625),("2023-08-17","UST",3,54.625),
    ("2024-07-08","UST",46,75.90),("2025-04-04","UST",15,67.85),
    ("2025-07-22","UST",37,79.85),
    ("2024-04-25","EUNL",22,88.60),("2024-05-31","EUNL",26,90.96),
    ("2024-07-19","EUNL",26,94.60),("2025-01-08","EUNL",31,104.54),
    ("2025-04-04","EUNL",11,92.25),("2025-08-01","EUNL",15,103.43),
    ("2025-09-30","EUNL",34,107.348),("2025-11-07","EUNL",22,109.00),
    ("2026-01-20","EUNL",8,112.18),("2026-02-26","EUNL",7,113.73),
    ("2026-03-13","EUNL",7,111.84),("2026-05-14","EUNL",13,117.94),
    ("2026-06-09","EUNL",7,120.62),("2026-07-06","EUNL",6,126.00),
    ("2021-01-04","IS3R",8,48.42),("2021-03-01","IS3R",11,49.63),
    ("2021-04-05","IS3R",10,52.06),("2021-06-01","IS3R",5,51.52),
    ("2021-07-05","IS3R",5,53.55),("2021-08-03","IS3R",5,54.08),
    ("2021-09-01","IS3R",5,56.06),("2021-10-01","IS3R",5,54.53),
    ("2021-11-19","IS3R",5,60.54),("2021-12-02","IS3R",4,58.25),
    ("2022-01-03","IS3R",5,59.64),("2022-02-18","IS3R",5,53.15),
    ("2022-04-22","IS3R",10,55.02),("2022-05-09","IS3R",6,51.44),
    ("2022-06-13","IS3R",6,50.31),("2022-09-16","IS3R",11,51.90),
    ("2022-12-02","IS3R",11,54.13),("2022-12-19","IS3R",12,51.62),
    ("2023-01-31","IS3R",8,50.96),("2023-02-10","IS3R",8,51.91),
    ("2023-03-10","IS3R",8,50.44),("2023-04-26","IS3R",8,50.30),
    ("2023-06-27","IS3R",16,50.63),("2023-08-11","IS3R",16,51.70),
    ("2024-08-02","IS3R",34,67.35),("2024-08-02","IS3R",1,67.35),
    ("2025-11-07","VWCE",21,141.98),("2025-12-17","VWCE",21,142.00),
    ("2026-01-20","VWCE",20,146.70),
]
purchases_family = [("2026-05-15","EUNL",413,121.00),
    ("2026-07-01","EUNL",80,125.00),]

def current_perf(purchases, prices):
    h = defaultdict(lambda: {'qty':0,'cost':0.0})
    for _, t, q, p in purchases:
        h[t]['qty'] += q
        h[t]['cost'] += q*p
    total_cost = sum(v['cost'] for v in h.values())
    total_value = sum(v['qty']*prices.get(t, v['cost']/v['qty'] if v['qty'] else 0) for t,v in h.items())
    if total_cost == 0:
        return 0.0
    return round((total_value-total_cost)/total_cost*100, 2)

perf_personal = current_perf(purchases_personal, prices)
perf_family   = current_perf(purchases_family, prices)
print(f"Personal: {perf_personal}%  Family: {perf_family}%")

# Build monthly history for chart (personal only, has real history)
def build_monthly(purchases, prices, end_month=None):
    if end_month is None:
        end_month = date.today().strftime('%Y-%m')
    purchases = sorted(purchases, key=lambda x: x[0])
    start_d = datetime.strptime(purchases[0][0][:7], '%Y-%m').date()
    end_d = datetime.strptime(end_month, '%Y-%m').date()
    months = []
    d = start_d
    while d <= end_d:
        months.append(d.strftime('%Y-%m'))
        d = date(d.year+1,1,1) if d.month==12 else date(d.year,d.month+1,1)

    def get_price(ticker, month_str):
        pts = [(datetime.strptime(p[0],'%Y-%m-%d').date().toordinal(), p[3])
               for p in purchases if p[1]==ticker]
        pts.append((date.today().toordinal(), prices.get(ticker, pts[-1][1] if pts else 0)))
        pts.sort()
        target = datetime.strptime(month_str+'-15','%Y-%m-%d').date().toordinal()
        if target <= pts[0][0]: return pts[0][1]
        if target >= pts[-1][0]: return pts[-1][1]
        for i in range(len(pts)-1):
            x0,y0=pts[i]; x1,y1=pts[i+1]
            if x0<=target<=x1:
                return y0+(target-x0)/(x1-x0)*(y1-y0)
        return pts[-1][1]

    h = defaultdict(lambda: {'qty':0,'cost':0.0})
    pi = 0
    result = []
    for month in months:
        while pi < len(purchases) and purchases[pi][0][:7] == month:
            _, t, q, p = purchases[pi]
            h[t]['qty'] += q; h[t]['cost'] += q*p
            pi += 1
        total_cost = sum(v['cost'] for v in h.values())
        if total_cost == 0: continue
        total_value = sum(v['qty']*get_price(t,month) for t,v in h.items() if v['qty']>0)
        perf = round((total_value-total_cost)/total_cost*100, 2)
        result.append({'m': month, 'pct': perf})
    return result

history_personal = build_monthly(purchases_personal, prices)
history_family   = build_monthly(purchases_family, prices)

# Force last history point to match exact current performance (no rounding/interpolation drift)
current_month = date.today().strftime('%Y-%m')
if history_personal and history_personal[-1]['m'] == current_month:
    history_personal[-1]['pct'] = perf_personal
if history_family and history_family[-1]['m'] == current_month:
    history_family[-1]['pct'] = perf_family

# Read/update data.json
try:
    with open('data.json', 'r') as f:
        site_data = json.load(f)
except FileNotFoundError:
    site_data = {}

site_data['portfolio'] = {
    'personal': {
        'performance_pct': perf_personal,
        'history': history_personal,
    },
    'family': {
        'performance_pct': perf_family,
        'history': history_family,
    },
    'prices': prices,
    'last_update': str(date.today()),
}

with open('data.json', 'w') as f:
    json.dump(site_data, f, indent=2)
print("data.json updated")
