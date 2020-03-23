#!/usr/bin/env python3

import json
import datetime
import math
from collections import defaultdict
import itertools
import os

if not os.path.exists('by_state'):
    os.makedirs('by_state')

with open('data_collation/covidtracking.json', 'r') as f:
    covid_tracking_data = json.load(f)

def date_int_parse(d):
    return datetime.date(math.floor(d / 10000), math.floor(d / 100) % 100, d % 100)

# pass 1: find the first date, map to new timeseries
first_date = None
last_date = None
for row in covid_tracking_data:
    sample_date = date_int_parse(row['date'])
    if first_date is None or sample_date < first_date:
        first_date = sample_date
    if last_date is None or sample_date > last_date:
        last_date = sample_date

print('First date:', first_date)
print('Last date:', last_date)

global_dates = []
curr = first_date
while curr <= last_date:
    global_dates.append(str(curr))
    curr = curr + datetime.timedelta(days=1)

print(global_dates)

state_data = defaultdict(lambda: defaultdict(lambda: [None] * len(global_dates)))

for row in covid_tracking_data:
    sample_date = date_int_parse(row['date'])
    state = row['state']
    # print(sample_date)

    date_index = global_dates.index(str(sample_date))

    for sample in ['positive', 'negative', 'pending', 'hospitalized', 'death', 'total']:
        state_data[state][sample][date_index] = row[sample]

def strip_trailing_none(s):
    new_s = s[:]
    while len(new_s) > 0 and new_s[-1] is None:
        new_s.pop()
    return new_s

def sum_series(*ss):
    return [sum(filter(lambda x: x is not None, samples)) for samples in itertools.zip_longest(*ss, fillvalue=0)]

state_write_whitelist = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'] + ['AS', 'GU', 'MP', 'PR', 'VI']

for state, subseries in state_data.items():
    assert state in state_write_whitelist, "{} not in whitelist".format(state)

    state_data = {
        'timeseries_dates': global_dates,
        'total': {
            'confirmed': subseries['positive'],
            'tested': sum_series(subseries['positive'], subseries['negative'], subseries['pending']),
            'hospitalized': subseries['hospitalized'],
        }
    }

    for total_name in list(state_data['total'].keys()):
        new_data = strip_trailing_none(state_data['total'][total_name])
        if len(new_data) > 0:
            state_data['total'][total_name] = new_data
        else:
            del state_data['total'][total_name]

    with open('by_state/' + state.lower() + '.json', 'w') as f:
        json.dump(state_data, f, indent=2)
