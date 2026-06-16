import urllib.request
import urllib.parse
import json
import os
import re

# Step 1: get access token
data = urllib.parse.urlencode({
    'client_id':     os.environ['STRAVA_CLIENT_ID'],
    'client_secret': os.environ['STRAVA_CLIENT_SECRET'],
    'refresh_token': os.environ['STRAVA_REFRESH_TOKEN'],
    'grant_type':    'refresh_token'
}).encode()

req = urllib.request.Request('https://www.strava.com/oauth/token', data=data)
token_data = json.loads(urllib.request.urlopen(req).read())
access_token = token_data['access_token']
print("Token OK")

# Step 2: fetch all running activities from Strava
page = 1
total_m = 0
while True:
    url = f"https://www.strava.com/api/v3/athlete/activities?per_page=100&page={page}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
    activities = json.loads(urllib.request.urlopen(req).read())
    if not activities:
        break
    for a in activities:
        if a.get('type') == 'Run' or a.get('sport_type') == 'Run':
            total_m += a.get('distance', 0)
    page += 1
    if len(activities) < 100:
        break

# Base fissa 903.2 km (Nike + Garmin pre-Strava) + km nuovi da Strava
KM_OFFSET = 903.2
strava_km = total_m / 1000
total_km = round(strava_km + KM_OFFSET, 1)
print(f"Km da Strava: {round(strava_km, 1)} + base {KM_OFFSET} = {total_km}")

# Format with Italian locale: 1.234,5
def fmt_km(n):
    # Split integer and decimal
    parts = f"{n:.1f}".split('.')
    integer = parts[0]
    decimal = parts[1]
    # Add dot thousands separator
    if len(integer) > 3:
        integer = integer[:-3] + '.' + integer[-3:]
    return integer + ',' + decimal

formatted = fmt_km(total_km)
print(f"Formatted: {formatted}")

# Step 3: update index.html
with open('index.html', 'r') as f:
    html = f.read()

html_new = re.sub(
    r'id="km-total">[^<]+<',
    f'id="km-total">{formatted}<',
    html
)

with open('index.html', 'w') as f:
    f.write(html_new)
print("index.html aggiornato")
