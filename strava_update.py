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
print(f"Token OK")

# Step 2: fetch all activities and sum running km
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

total_km = round(total_m / 1000, 1)
print(f"Km totali: {total_km}")

# Step 3: update index.html
with open('index.html', 'r') as f:
    html = f.read()

html_new = re.sub(
    r'id="km-total">[0-9.,]+<',
    f'id="km-total">{total_km}<',
    html
)

with open('index.html', 'w') as f:
    f.write(html_new)
print("index.html aggiornato")
