#!/usr/bin/env python3

import requests, json
import os

if not os.path.exists('data_collation'):
    os.makedirs('data_collation')

response = requests.get('https://covidtracking.com/api/v1/states/daily.json')
response.raise_for_status()

with open('data_collation/covidtracking.json', 'w') as f:
    json.dump(response.json(), f, indent=2)
