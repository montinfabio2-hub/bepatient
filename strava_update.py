import urllib.request
import urllib.parse
import json
import os

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

KM_OFFSET = 903.2
strava_km = total_m / 1000
total_km = round(strava_km + KM_OFFSET, 1)
print(f"Km da Strava: {round(strava_km, 1)} + base {KM_OFFSET} = {total_km}")

# Step 3: read existing data.json (or create new)
try:
    with open('data.json', 'r') as f:
        site_data = json.load(f)
except FileNotFoundError:
    site_data = {}

from datetime import date
site_data['km_total'] = total_km
site_data['km_last_update'] = str(date.today())

with open('data.json', 'w') as f:
    json.dump(site_data, f, indent=2)
print("data.json updated")
